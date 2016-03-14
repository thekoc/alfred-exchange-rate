# coding=utf-8

import xml.dom.minidom as Dom


class AlfredXmlGenerator(object):
    def __init__(self):
        self.doc = Dom.Document()
        self.root_node = self.doc.createElement('items')
        self.doc.appendChild(self.root_node)
        self._uid = 0

    def add_text_node(self, name, value, item_node):
        node = self.doc.createElement(name)
        node_value = self.doc.createTextNode(value)
        node.appendChild(node_value)
        item_node.appendChild(node)

    @property
    def uid(self):
        self._uid += 1
        return str(self._uid - 1)

    def add_item(self, title, subtitle, icon='default_icon', arg=None, autocomplete=None):
        doc = self.doc
        item_node = doc.createElement('item')
        item_node.setAttribute('uid', self.uid)
        if autocomplete is not None:
            item_node.setAttribute('autocomplete', autocomplete)
        if arg is not None:
            item_node.setAttribute('arg', arg)
        self.add_text_node('title', title, item_node)
        self.add_text_node('subtitle', subtitle, item_node)
        self.add_text_node('icon', icon, item_node)
        self.root_node.appendChild(item_node)

    def save_to_file(self, name='result.xml'):
        with open(name, 'w') as f:
            f.write(self.doc.toprettyxml(encoding='utf-8').decode())

    def print_xml(self):
        b = self.doc.toxml(encoding='utf-8')
        print(b.decode('utf-8'))

    @classmethod
    def print_error(cls, title, content):
        tem = AlfredXmlGenerator()
        tem.add_item(title, content, icon='error_icon')
        tem.print_xml()
