import sys
import numpy as np
from mayavi import mlab

def render_volume(file_path):
    # File basic information
    dtype = np.float32
    dtype_size = np.dtype(dtype).itemsize

    # Read data file
    with open(file_path, 'rb') as f:
        f.seek(0, 2)  # Move to the end of the file
        file_size = f.tell()  # Get file size
        f.seek(0)  # Move to the beginning of the file

        # Calculate correct shape
        volume_size = 384  # Assuming the data is 384x384x384
        shape = (volume_size, volume_size, volume_size)
        print(f"Calculated shape: {shape}")

        # Load data
        data = np.fromfile(f, dtype=dtype).reshape(shape)

    # Normalize data
    data = (data - np.min(data)) / (np.max(data) - np.min(data))

    # Render 3D image with Mayavi
    mlab.figure(bgcolor=(1, 1, 1), size=(1800, 1300))

    # Render volume data
    mlab.contour3d(data, contours=[0.2, 0.5, 0.8], opacity=0.5, colormap='gray')

    # Add color bar with black text
    cbar = mlab.colorbar(title='Intensity', orientation='vertical')
    cbar.label_text_property.color = (0, 0, 0)

    # Show
    mlab.show()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'maotai_384x384x384.raw'  # Default filename
    render_volume(file_path)
