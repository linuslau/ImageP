import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import os

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = pg.mkQApp("ImageView Example")

# Create window with ImageView widget
win = QtWidgets.QMainWindow()
win.resize(500, 500)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('pyqtgraph example: ImageView')

# Load RAW data in little-endian format (assuming 384x384x384, 32-bit float)
file_path = "maotai_384x384x384.raw"
if os.path.exists(file_path):
    # Load the data as little-endian 32-bit float
    data = np.fromfile(file_path, dtype='<f4').reshape((384, 384, 384))
    
    # Display the data in ImageView, specifying time values for the third dimension
    imv.setImage(data, xvals=np.arange(data.shape[0]))
    
    # Force the update of the time axis
    imv.timeLine.setValue(0)
else:
    print(f"File {file_path} does not exist.")

if __name__ == '__main__':
    pg.exec()
