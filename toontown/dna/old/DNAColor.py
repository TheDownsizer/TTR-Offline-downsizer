from .DNAPropertyElement import DNAPropertyElement
from .DNAParser import *
from panda3d.core import *

class DNAColor(DNAPropertyElement):
    TAG = 'color'

    def __init__(self, r="1", g="1", b="1", a="1"):
        DNAPropertyElement.__init__(self)

        self.color = (float(r) * 1.0, float(g) * 1.0, float(b) * 1.0, float(a))

    def _apply(self, parent):
        parent.setColorScale(self.color)

registerElement(DNAColor)
