from HTMLParser import HTMLParser
from pprint import pprint


class ApiInfo(object):
    pass



PATH_TD = object()
PATH_CLASS = ('class', 'path')


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.seen_header = False
        self.data = []
        self.tag_stack = []
        self.cell_data = ''
        path_str = ''
        path_params = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td' and PATH_CLASS in attrs:
            self.tag_stack.append(PATH_TD)
            self.path_str = ''
            self.path_params = []
        else:
            self.tag_stack.append(tag)

        if not self.seen_header:
            return


        if tag == 'tr':
            self.row = []

    def handle_endtag(self, tag):
        last_tag = self.tag_stack.pop()

        if not self.seen_header and tag == 'tr':
            self.seen_header = True
            return

        if last_tag == 'tr':
            self.data.append(self.row)

        elif last_tag == 'td':
            self.row.append(self.cell_data)
            self.cell_data = ''

        elif last_tag == PATH_TD:
            self.row.append(self.path_str)
            self.cell_data = ''

    def handle_data(self, data):
        if not self.seen_header:
            return

        if 'td' in self.tag_stack:
            self.handle_td_data(data)

        elif PATH_TD in self.tag_stack:
                self.handle_path_data(data)

    def handle_td_data(self, data):

        if self.tag_stack[-1] in ['pre', 'code']:
            self.cell_data += '`{}` '.format(data)

        else:
            self.cell_data += ' '.join(data.split()) + ' '

    def handle_path_data(self, data):
        if self.tag_stack[-1] == 'i':
            self.path_str += '{%s}' % data
            self.path_params.append(data)
        else:
            self.path_str += data



parser = MyHTMLParser()
with open('html_sample.html') as handle:
    parser.feed(handle.read())
pprint(parser.data)
# print
# for row in parser.data:
    # print row[-1]
