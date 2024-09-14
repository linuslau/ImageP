import asyncio
import time

async def process_image_async(image_data):
    print("process_image_async enter")
    if image_data is None:
        raise ValueError("Image data is None. Cannot perform inversion.")

    inverted_image = 255 - image_data  # 简单地取反处理，假设是灰度图像
    print("process_image_async processed")
    return inverted_image

