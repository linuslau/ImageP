import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets


class CustomROI(pg.ROI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 添加四个边上的控制点
        self.addScaleHandle([0.5, 0], [0.5, 0.5])  # Bottom edge
        self.addScaleHandle([0.5, 1], [0.5, 0.5])  # Top edge
        self.addScaleHandle([0, 0.5], [0.5, 0.5])  # Left edge
        self.addScaleHandle([1, 0.5], [0.5, 0.5])  # Right edge

        # 添加四个顶点的虚拟控制点
        self.addScaleHandle([0, 0], [0, 0])  # Bottom-left corner
        self.addScaleHandle([0, 1], [0, 1])  # Top-left corner
        self.addScaleHandle([1, 0], [1, 0])  # Bottom-right corner
        self.addScaleHandle([1, 1], [1, 1])  # Top-right corner

        # 设置四条边的颜色为红色
        self.setPen('r')

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        action_row = menu.addAction("ROW Properties")
        action_measure = menu.addAction("Measure")
        action_invert = menu.addAction("Invert")

        action = menu.exec_(event.screenPos())
        if action == action_row:
            print("ROW Properties selected")
        elif action == action_measure:
            print("Measure selected")
        elif action == action_invert:
            print("Invert selected")

        event.accept()  # Prevent default context menu


pg.setConfigOptions(imageAxisOrder='row-major')

pg.mkQApp()
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('pyqtgraph example: Image Analysis')

# A plot area (ViewBox + axes) for displaying the image
p1 = win.addPlot(title="")

# Item for displaying image data
img = pg.ImageItem()
p1.addItem(img)

# Custom ROI for selecting an image region
roi = CustomROI([-8, 14], [6, 5])
p1.addItem(roi)
roi.setZValue(10)  # make sure ROI is drawn above image

# Isocurve drawing
iso = pg.IsocurveItem(level=0.8, pen='g')
iso.setParentItem(img)
iso.setZValue(5)

# Contrast/color control
hist = pg.HistogramLUTItem()
hist.setImageItem(img)
win.addItem(hist)

# Draggable line for setting isocurve level
isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
hist.vb.addItem(isoLine)
hist.vb.setMouseEnabled(y=False)  # makes user interaction a little easier
isoLine.setValue(0.8)
isoLine.setZValue(1000)  # bring iso line above contrast controls

# Another plot area for displaying ROI data
win.nextRow()
p2 = win.addPlot(colspan=2)
p2.setMaximumHeight(250)
win.resize(800, 800)
win.show()

# Generate image data
data = np.random.normal(size=(200, 100))
data[20:80, 20:80] += 2.
data = pg.gaussianFilter(data, (3, 3))
data += np.random.normal(size=(200, 100)) * 0.1
img.setImage(data)
hist.setLevels(data.min(), data.max())

# build isocurves from smoothed data
iso.setData(pg.gaussianFilter(data, (2, 2)))

# set position and scale of image
tr = QtGui.QTransform()
img.setTransform(tr.scale(0.2, 0.2).translate(-50, 0))

# zoom to fit image
p1.autoRange()


# Callbacks for handling user interaction
def updatePlot():
    global img, roi, data, p2
    selected = roi.getArrayRegion(data, img)
    p2.plot(selected.mean(axis=0), clear=True)


roi.sigRegionChanged.connect(updatePlot)
updatePlot()


def updateIsocurve():
    global isoLine, iso
    iso.setLevel(isoLine.value())


isoLine.sigDragged.connect(updateIsocurve)


def imageHoverEvent(event):
    """Show the position, pixel, and value under the mouse cursor."""
    if event.isExit():
        p1.setTitle("")
        return
    pos = event.pos()
    i, j = pos.y(), pos.x()
    i = int(np.clip(i, 0, data.shape[0] - 1))
    j = int(np.clip(j, 0, data.shape[1] - 1))
    val = data[i, j]
    ppos = img.mapToParent(pos)
    x, y = ppos.x(), ppos.y()
    p1.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %.3g" % (x, y, i, j, val))


# Monkey-patch the image to use our custom hover function.
img.hoverEvent = imageHoverEvent

if __name__ == '__main__':
    pg.exec()
