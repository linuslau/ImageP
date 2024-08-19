import numpy as np
from mayavi import mlab


def render_volume(file_path):
    # 文件基本信息
    dtype = np.float32
    dtype_size = np.dtype(dtype).itemsize

    # 读取数据文件
    with open(file_path, 'rb') as f:
        f.seek(0, 2)  # 移动到文件末尾
        file_size = f.tell()  # 获取文件大小
        f.seek(0)  # 移动到文件开头

        # 计算正确的形状
        volume_size = 384  # 由于之前讨论过，这个数据应该是384x384x384
        shape = (volume_size, volume_size, volume_size)
        print(f"Calculated shape: {shape}")

        # 加载数据
        data = np.fromfile(f, dtype=dtype).reshape(shape)

    # 数据归一化处理
    data = (data - np.min(data)) / (np.max(data) - np.min(data))

    # 使用Mayavi渲染3D图像
    mlab.figure(bgcolor=(1, 1, 1))

    # 渲染体数据
    mlab.contour3d(data, contours=[0.2, 0.5, 0.8], opacity=0.5, colormap='gray')

    # 添加颜色条
    mlab.colorbar(title='Intensity', orientation='vertical')

    # 显示
    mlab.show()


if __name__ == '__main__':
    file_path = 'maotai_384x384x384.raw'
    render_volume(file_path)
