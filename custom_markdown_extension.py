from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from xml.etree.ElementTree import SubElement

class FigureTreeprocessor(Treeprocessor):
    def run(self, root):
        self.process_element(root)
        return root

    def process_element(self, element):
        children = list(element)
        for child in children:
            if child.tag == 'img':
                figure = SubElement(element, 'figure')
                element.remove(child)
                figure.append(child)
                caption = SubElement(figure, 'figcaption')
                caption.text = child.get('alt')
            else:
                self.process_element(child)

class FigureExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(FigureTreeprocessor(md), 'figure', 15)

def makeExtension(**kwargs):
    return FigureExtension(**kwargs)
