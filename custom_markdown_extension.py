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
                # Create a new div for centering
                center_div = SubElement(element, 'div')
                center_div.set('class', 'image-container')
                
                # Create figure inside the centering div
                figure = SubElement(center_div, 'figure')
                caption = SubElement(figure, 'figcaption')
                caption.text = child.get('alt')
                
                # Move the image into the figure
                element.remove(child)
                figure.insert(0, child)
            else:
                self.process_element(child)

class FigureExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(FigureTreeprocessor(md), 'figure', 15)

def makeExtension(**kwargs):
    return FigureExtension(**kwargs)
