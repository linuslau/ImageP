import numpy as np
from mayavi import mlab
import matplotlib.pyplot as plt

# 渲染体数据
def render_volume(file_path):
    # 读取体数据
    with open(file_path, 'rb') as f:
        dtype = np.float32
        dtype_size = np.dtype(dtype).itemsize
        f.seek(0, 2)  # 移动到文件末尾
        file_size = f.tell()
        shape = (384, 384, 384)
        f.seek(0)
        data = np.fromfile(f, dtype=dtype).reshape(shape)

    # 阈值处理，只保留显著的形状部分
    threshold_value = 0.02  # 根据实际情况调整阈值
    data[data < threshold_value] = 0  # 抑制小于阈值的噪声

    # 使用灰度图显示
    src = mlab.pipeline.scalar_field(data)
    mlab.pipeline.iso_surface(src, contours=[data.max() * 0.5], opacity=1.0)
    mlab.pipeline.volume(src, vmin=data.min(), vmax=data.max())

    mlab.show()

# 调用渲染函数
render_volume('maotai_384x384x384.raw')
