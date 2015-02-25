import itertools
import json
from HTMLParser import HTMLParser
from pprint import pprint, pformat
from StringIO import StringIO

from html2rest import Parser, CODEBLOCK


class Pep8Parser(Parser):
    def end_pre(self):
        sbuf = self.stringbuffer.getvalue()
        if sbuf:
            try:
                parsed = json.loads(sbuf)
                sbuf = json.dumps(parsed, indent=4)
            except Exception:
                pass
            self.linebuffer.rawwrite(sbuf)
            self.linebuffer.indent(4)
        self.clear_stringbuffer()
        self.writeendblock()
        #self.inblock -= 1
        self.verbatim = False

def to_rst(html):
    buf = StringIO()
    parser = Pep8Parser(buf, 'utf8')
    parser.linebuffer._wrapper.width = 72 - 2*4  # will be indented two levels
    parser.feed(html.decode('utf8'))
    parser.close()
    buf.seek(0)
    return buf.read()


class Columns(object):
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"
    POST = "POST"
    Path = "Path"
    Description = "Description"

    methods = [GET, PUT, DELETE, POST]
    iterate = itertools.cycle([GET, PUT, DELETE, POST, Path, Description])


def is_placeholder(part):
    return part.startswith('{') and part.endswith('}')


def placehoholder_name(part):
    assert is_placeholder(part)
    return part[1:-1]


def is_single_char(part):
    return len(part) == 1


custom_method_names = {
    'definitions': 'set_definitions',
    'exchanges/{vhost}/{name}/publish': 'publish',
    'queues/{vhost}/{name}/actions': 'do_action',
    'queues/{vhost}/{name}/get': 'get_messages',
    'bindings/{vhost}/e/{exchange}/q/{queue}': 'bind_exchange_to_queue',
    'bindings/{vhost}/e/{source}/e/{destination}': 'bind_exchange_to_exchange',
}


class ApiInfo(object):
    def __init__(self, row):
        self.method_flags = row[:4]
        (path_string, path_params) = row[4]
        path = path_string[5:]  # skip /api/

        if '\n' in path:
            # deprecated path for definitions. ignore
            path = path.split()[0]


        self.path_parts = path.split('/')

        self.fixed_path_parts = [
            part for part in self.path_parts
            if not is_placeholder(part) and not is_single_char(part)
        ]
        self.variable_path_parts = [
            placehoholder_name(part) for part in self.path_parts
            if is_placeholder(part)
        ]

        self.description = to_rst(row[5])

    def methods(self):
        return [
            method for (method, is_available) in
            zip(Columns.methods, self.method_flags)
            if is_available and method != Columns.POST
        ]

    def method_name(self, method):
        prefixes = {
            Columns.GET: 'get',
            Columns.PUT: 'create',
            Columns.DELETE: 'delete',
            Columns.POST: 'set',
        }
        prefix = prefixes[method]
        if self.variable_path_parts:
            name = '{}_{}_by_{}'.format(
                prefix,
                '_'.join(self.fixed_path_parts),
                '_and_'.join(self.variable_path_parts),
            )
        else:
            name = '{}_{}'.format(
                prefix,
                '_'.join(self.fixed_path_parts),
            )
        return name.replace('-', '_')


    def parameter_string(self):
        return ', '.join(['self'] + self.variable_path_parts)

    def request_parameters(self):
        """arguments to self.request"""
        parameters = []
        for part in self.path_parts:
            if is_placeholder(part):
                parameters.append(placehoholder_name(part))
            else:
                parameters.append("'{}'".format(part))
        return ', '.join(parameters)

    def description_string(self):
        params = '\n'.join(
            ':param str {}:'.format(param)
            for param in self.variable_path_parts
        )
        if params:
            doc = '{}\n{}\n'.format(self.description, params)
        else:
            doc = '{}\n'.format(self.description)

        return doc


class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.seen_header = False
        self.data = []
        self.tag_stack = []
        self.cell_data = ''
        self.path_string = ''
        self.path_params = []

        self.column = None

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

        if not self.seen_header:
            return

        if tag == 'tr':
            self.row = []

        elif tag == 'td':
            self.column = next(Columns.iterate)
            if self.column in Columns.methods:
                self.cell_data = False
            elif self.column == Columns.Description:
                self.cell_data = ''

        elif self.column == Columns.Description and 'td' in self.tag_stack:
            self.cell_data += '<{}>'.format(tag)


    def handle_endtag(self, tag):
        self.tag_stack.pop()

        if not self.seen_header and tag == 'tr':
            self.seen_header = True
            return

        if tag == 'tr':
            self.data.append(ApiInfo(self.row))

        elif tag == 'td':
            if self.column == Columns.Path:
                self.row.append((self.path_string, self.path_params))
                self.path_string = ''
                self.path_params = []
            else:
                self.row.append(self.cell_data)
                self.cell_data = None

        elif self.column == Columns.Description and 'td' in self.tag_stack:
            self.cell_data += '</{}>'.format(tag)
            self.row.append(self.cell_data)


    def handle_data(self, data):
        if not self.seen_header:
            return

        if 'td' in self.tag_stack:
            if self.column in Columns.methods:
                self.cell_data = bool(data)
            elif self.column == Columns.Path:
                self.handle_path_data(data)
            else:
                self.cell_data += data

    def handle_path_data(self, data):
        if self.tag_stack[-1] == 'i':
            self.path_string += '{%s}' % data
            self.path_params.append(data)
        else:
            self.path_string += data


def parse(filename):
    parser = MyHTMLParser()
    with open(filename) as handle:
        parser.feed(handle.read())

    return parser.data


def indent(text, size=4):
    lines = text.split('\n')
    indent = ' ' * size
    def indent_unless_blank(line):
        if line:
            return indent + line
        return ''

    indented = '\n'.join(
        indent_unless_blank(line)
        for line in lines
    )
    return indented


preamble = '''\
try:
    # python 2.x
    from urllib import quote
except ImportError:
    # python 3.x
    from urllib.parse import quote

import requests


def _quote(value):
    return quote(value, '')


class Client(object):
    """RabbitMQ Management plugin api

    Usage:
        client = Client('http://localhost:15672', 'guest', guest')
        client.get_vhosts()
    """
    def __init__(self, url, username, password):
        self._base_url = '{}/api'.format(url)
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers['content-type'] = 'application/json'

    def _build_url(self, args):
        args = map(_quote, args)
        return '{}/{}'.format(
            self._base_url,
            '/'.join(args),
        )

    def request(self, method, *args, **kwargs):
        url = self._build_url(args)
        result = self._session.request(method, url, **kwargs)
        result.raise_for_status()
        if result.content:
            return result.json()

'''


def render(data):
    print preamble

    for api in data:
        for method in api.methods():
            print indent(
                'def {}({}):'.format(
                    api.method_name(method),
                    api.parameter_string(),
                )
            )
            print indent(
                '"""{}"""'.format(api.description_string()),
                size=8,
            )
            print indent(
                "return self.request('{}', {})".format(
                    method,
                    api.request_parameters()
                ),
                size=8,
            )
            print


if __name__ == '__main__':
    data = parse('rabbit_api_reference.html')
    render(data)
