import itertools
from HTMLParser import HTMLParser
from pprint import pprint


class Columns(object):
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"
    POST = "POST"
    Path = "Path"
    Description = "Description"

    methods = [GET, PUT, DELETE, POST]
    iterate = itertools.cycle([GET, PUT, DELETE, POST, Path, Description])


class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.seen_header = False
        self.data = []
        self.tag_stack = []
        self.cell_data = ''
        self.path_str = ''
        self.path_params = []

        self.column = None

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

        if not self.seen_header:
            return

        if tag == 'td':
            self.column = next(Columns.iterate)
            if self.column in Columns.methods:
                self.cell_data = False

        if tag == 'tr':
            self.row = []

    def handle_endtag(self, tag):
        self.tag_stack.pop()

        if not self.seen_header and tag == 'tr':
            self.seen_header = True
            return

        if tag == 'tr':
            self.data.append(self.row)

        elif tag == 'td':
            if self.column == Columns.Path:
                self.row.append((self.path_str, self.path_params))
                self.path_str = ''
                self.path_params = []
            else:
                self.row.append(self.cell_data)
                self.cell_data = None


    def handle_data(self, data):
        if not self.seen_header:
            return

        if 'td' in self.tag_stack:
            if self.column in Columns.methods:
                self.cell_data = bool(data)
            elif self.column == Columns.Path:
                self.handle_path_data(data)
            else:
                self.handle_td_data(data)

    def handle_td_data(self, data):

        if self.tag_stack[-1] in ['pre', 'code']:
            self.cell_data += '`{}` '.format(data)

        else:
            if self.cell_data is None:
                self.cell_data = ''
            self.cell_data += ' '.join(data.split()) + ' '

    def handle_path_data(self, data):
        if self.tag_stack[-1] == 'i':
            self.path_str += '{%s}' % data
            self.path_params.append(data)
        else:
            self.path_str += data



parser = MyHTMLParser()
with open('api_reference.html') as handle:
    parser.feed(handle.read())
# pprint(parser.data)
# print

all_prefxies = ['get', 'create', 'delete']

for row in parser.data:
    url_parts = row[-2][0][5:].split('/')  # skipping /api/
    fixed_url_parts = [p for p in url_parts if not p.startswith('{')]
    variable_url_parts = [p[1:-1] for p in url_parts if p.startswith('{')]
    prefixes = [
        info[1]
        for info in zip(row[:3], all_prefxies)
        if info[0]
    ]

    for prefix in prefixes:
        if variable_url_parts:
            print '{}_{}_by_{}'.format(
                prefix,
                '_'.join(fixed_url_parts),
                '_'.join(variable_url_parts),
            )
        else:
            print '{}_{}'.format(
                prefix,
                '_'.join(fixed_url_parts),
            )

    if row[3]:
        print '\t', row[-2][0]
