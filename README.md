# CellDict

**Python 基于 `Pickle` 的高效变量保存读取!**

简洁快速的保存和读取变量, 方便的版本控制.

## 安装

    pip install -U celldict

## 简介

`CellDict` 用于快速保存 Python 变量到文件, `shelve` 包也有类似的功能, 但是 `shelve` 在持续不断的写入数据的时候有概率造成数据丢失, 而 `CellDict` 根据文件夹区分 `Key`, 所以更加安全, 且支持版本控制.

## 使用
```
from celldict import CellDict

# 数据集名称为 "dataname", 修改记录保存三次
cell = CellDict("dataname", version_record=3, root_path=".CellDict")

# 保存数据
cell.set("data1", 1)
cell.set("data2", "Hello CellDict!")

# 读取数据
cell.get("data1")
cell.get("data2")

# 记录多次并读取需要版本的数据
cell.set("data1", 2)
cell.set("data1", 3)
# 只记录 3 次, 第一次记录的 1 会被丢弃
cell.set("data1", 4)

# 最新记录 4
cell.get("data1", "last")
# 最旧记录 2
cell.get("data1", "former")

# 按索引读取
cell.get("data1", 0) # 4
cell.get("data1", 1) # 3
cell.get("data1", 2) # 2

cell.get("data1", -1) # 2
cell.get("data1", -2) # 3
cell.get("data1", -3) # 4

# 读取所有版本数据
cell.getall("data1")

# 获取数据所有 keys
cell.keys() # ['data1', 'data2']

# 删除数据 out True or False
cell.delkey("data2")
```
