#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'celldict',
    version = '1.1.0',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/celldict',
    description = u'Python 文件型配置! 细胞字典, 简单高效安全的保存读取程序变量!',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["celldict"],
    install_requires = [
    ],
    entry_points={
        'console_scripts': [
        ],
    },
    package_data={
    },
)