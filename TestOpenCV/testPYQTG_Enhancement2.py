import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from PIL import Image


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

		action_row.triggered.connect(self.showRowPropertiesDialog)
		action_measure.triggered.connect(self.showMeasureDialog)
		action_invert.triggered.connect(self.invertImage)

		menu.exec_(event.screenPos())
		event.accept()  # Prevent default context menu

	def showRowPropertiesDialog(self):
		dialog = QtWidgets.QDialog()
		dialog.setWindowTitle("ROW Properties")

		layout = QtWidgets.QFormLayout()

		labels = ["Property 1", "Property 2", "Property 3", "Property 4", "Property 5"]
		self.inputs = []

		for label in labels:
			input_field = QtWidgets.QLineEdit()
			layout.addRow(QtWidgets.QLabel(label), input_field)
			self.inputs.append(input_field)

		buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
		button_box = QtWidgets.QDialogButtonBox(buttons)
		button_box.accepted.connect(dialog.accept)
		button_box.rejected.connect(dialog.reject)

		layout.addRow(button_box)
		dialog.setLayout(layout)

		if dialog.exec_():
			values = [input_field.text() for input_field in self.inputs]
			print("Accepted with values:", values)
		else:
			print("Cancelled")

	def showMeasureDialog(self):
		if img.image is None or self is None:
			return

		# Get the bounding box of the ROI in image coordinates
		roi_coords = self.getArraySlice(img.image, img)
		if roi_coords is None:
			QtWidgets.QMessageBox.warning(None, "Measure", "Could not determine ROI coordinates.")
			return

		(slice_x, slice_y), _ = roi_coords
		region = img.image[slice_x, slice_y]

		if region.size == 0:
			QtWidgets.QMessageBox.warning(None, "Measure", "Selected region is empty.")
			return

		area = region.size
		mean_val = np.mean(region)
		min_val = np.min(region)
		max_val = np.max(region)

		dialog = QtWidgets.QDialog()
		dialog.setWindowTitle("Measure")

		layout = QtWidgets.QFormLayout()

		layout.addRow(QtWidgets.QLabel("Area:"), QtWidgets.QLabel(str(area)))
		layout.addRow(QtWidgets.QLabel("Mean:"), QtWidgets.QLabel(str(mean_val)))
		layout.addRow(QtWidgets.QLabel("Min:"), QtWidgets.QLabel(str(min_val)))
		layout.addRow(QtWidgets.QLabel("Max:"), QtWidgets.QLabel(str(max_val)))

		buttons = QtWidgets.QDialogButtonBox.Ok
		button_box = QtWidgets.QDialogButtonBox(buttons)
		button_box.accepted.connect(dialog.accept)

		layout.addRow(button_box)
		dialog.setLayout(layout)
		dialog.exec_()

	def invertImage(self):
		if img.image is not None:
			inverted_image = 255 - img.image  # 简单地取反处理，假设是灰度图像
			img.setImage(inverted_image)


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
roi = CustomROI([50, 50], [100, 100])  # 设置 ROI 的默认位置和大小
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

# Load the image data
image_path = 'boats.jpg'  # Ensure boats.jpg is in the current directory
image = Image.open(image_path)
data = np.array(image)

# Convert to grayscale if necessary
if data.ndim == 3:
	data = np.mean(data, axis=2).astype(np.uint8)

# Flip the image vertically to correct the upside-down issue
data = np.flipud(data)

img.setImage(data)
hist.setLevels(data.min(), data.max())

# build isocurves from smoothed data
iso.setData(pg.gaussianFilter(data, (2, 2)))

# set position and scale of image
tr = QtGui.QTransform()
img.setTransform(tr.scale(1.0, 1.0))  # 设置缩放比例以显示图像的真实大小

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
