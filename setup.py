#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'celldict',
    version = '2.0.0',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/celldict',
    description = u'Python 简洁快速的保存和读取变量, 方便的版本控制!',
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