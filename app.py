# -*- coding: utf-8 -*-
import base64
import json
import os
import traceback

import openai
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

import utils

load_dotenv()
app = FastAPI()
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'


class TextPrompt(BaseModel):
    prompt: str


class ImageBase64Prompt(BaseModel):
    images: list[str]


class ImageGeneratePrompt(BaseModel):
    type: str
    prompt: str


client = openai.AsyncClient(
    api_key=os.getenv('API_KEY'),
    base_url=os.getenv('BASE_URL'),
)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.getenv('API_KEY')}'
}


@app.post("/api/aigc/generate/draft/text")
async def generate_draft_from_text(item: TextPrompt):
    messages = [
        {'role': 'system', 'content': '我将给你提供一段简要的提示，请你将这篇博文补充为现代社交网络风格的标题和内容供用户发布微博。'
                                      '标题不超过50字，内容不超过500字。'
                                      '如果用户输入的 prompt 不足以生成微博，则内容部分返回为null。'
                                      '不要加入#和标签，但可以多使用emoji字符。'
                                      '并且根据你生成的内容指定一个配图风格，Must be one of "vivid" or "natural".'
                                      '请你以以下的JSON格式返回: {"title": 标题, "content": 内容, "style": 风格}。'},
        {'role': 'user', 'content': item.prompt},
    ]

    try:
        response = await client.chat.completions.create(
            model='gpt-4-turbo',
            messages=messages,
            response_format={'type': 'json_object'}
        )

        result = response.choices[0].message.content
        return {
            'code': 0,
            'message': '',
            'data': json.loads(result)
        }

    except Exception as e:
        traceback.print_exception(e)
        return {
            'code': 1,
            'message': '',
        }


@app.post("/api/aigc/generate/draft/image")
async def generate_draft_from_image(item: ImageBase64Prompt):

    messages = [
        {'role': 'system', 'content': '我将给你提供一些博文中的图片，请你将这篇博文写为现代社交网络风格的标题和内容供用户发布微博。'
                                      '标题不超过50字，内容不超过500字。'
                                      '如果用户输入的图片不足以生成微博，则内容部分返回为null。'
                                      '不要加入带有 # 符号的标签，但可以多使用emoji字符。'
                                      '请你以以下的JSON格式返回: {"title": 标题, "content": 内容}。'},
        {'role': 'user',
         'content': [
             {
                 'type': 'image_url',
                 'image_url': {
                     'url': f'data:image/jpeg;base64,{utils.resize_image(image)}'
                 }
             }
             for image in item.images]
         },
    ]

    completion = await client.chat.completions.create(
        model='gpt-4-turbo',
        messages=messages,
        response_format={'type': 'json_object'},
    )

    result = json.loads(completion.choices[0].message.content)
    if result['content']:
        return {
            'code': 0,
            'message': '',
            'data': result,
        }

    return {
        'code': 1,
        'message': '',
    }


@app.post("/api/aigc/generate/image/text")
async def generate_image_from_text(item: ImageGeneratePrompt):
    try:
        response = await client.images.generate(
            model='dall-e-3',
            prompt=f'我需要你生成适合微博配图的图片，{'' if item.type == "natural" else '风格偏向日式动漫风格，'}'
                   f'需要生成的内容如下: {item.prompt}',
            size='1024x1024',
            quality='standard',
            n=1,
            style=item.type if item.type == 'vivid' or item.type == 'natural' else 'vivid',
            response_format='url'
        )
        return {
            'code': 0,
            'message': '',
            'data': response.data[0]
        }
    except Exception as e:
        traceback.print_exception(e)
        return {
            'code': 1,
            'message': ''
        }
