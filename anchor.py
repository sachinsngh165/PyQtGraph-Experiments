import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
class Anchor(pg.ItemGroup):
    """Graphics item that anchors its position to the coordinate system inside
    a view box.
    """
    def __init__(self, view, pos, x=True, y=True):
        pg.ItemGroup.__init__(self)
        self.view = view
        self.anchorPos = pg.Point(pos)
        self.anchorAxes = (x, y)
        view.sigRangeChanged.connect(self.updatePosition)
    
    def updatePosition(self):
        pos = self.pos()
        anchorPos = self.parentItem().mapFromScene(self.view.mapViewToScene(self.anchorPos))
        x, y = self.anchorAxes
        if x:
            pos.setX(anchorPos.x())
        if y:
            pos.setY(anchorPos.y())
        self.setPos(pos)

app = pg.QtGui.QApplication([])
plt = pg.plot()

# Anchor doesn't draw anything, it just tracks a position in the viewbox
anchor = Anchor(plt.plotItem.vb, [0, 0], x=False, y=True)
anchor.setParentItem(plt.plotItem)

# Attach any shape to the anchor
marker = pg.QtGui.QGraphicsEllipseItem(-10, -10, 20, 20)
marker.setPos(0, 20)
marker.setPen(pg.mkPen('y', width=3))
marker.setParentItem(anchor)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()