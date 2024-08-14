# -*- coding: utf-8 -*-
import base64
import io

from PIL import Image


def resize_image(base64_image: str) -> str:
    base64_image = base64_image.split(';base64,')[1]

    # 解码base64图片字符串
    image_data = base64.b64decode(base64_image)

    # 打开图片
    img = Image.open(io.BytesIO(image_data))

    # 获取图片尺寸
    width, height = img.size

    # 计算缩放比例
    max_size = 600
    if max(width, height) > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        img = img.resize((new_width, new_height))

    # 将图片转换为字节流
    output_buffer = io.BytesIO()
    img = img.convert('RGB')
    img.save(output_buffer, format='JPEG')

    # 获取缩小后图片的base64编码字符串
    resized_base64_image = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

    return resized_base64_image
