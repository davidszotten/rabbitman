import itertools
from HTMLParser import HTMLParser
from pprint import pprint
from StringIO import StringIO

from html2rest import html2rest


def to_rst(html):
    buf= StringIO()
    html2rest(html, writer=buf)
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
            return '{}_{}_by_{}'.format(
                prefix,
                '_'.join(self.fixed_path_parts),
                '_and_'.join(self.variable_path_parts),
            )
        else:
            return '{}_{}'.format(
                prefix,
                '_'.join(self.fixed_path_parts),
            )


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


parser = MyHTMLParser()
with open('rabbit_api_reference.html') as handle:
    parser.feed(handle.read())


all_prefxies = ['get', 'create', 'delete']

for api in parser.data:
    for method in api.methods():
        print api.method_name(method)


# print
# for api in parser.data:
    # if api.method_flags[-1]:
        # print '/'.join(api.path_parts)
        # print api.description
        # print
