# CellDict

**基于 `Pickle` 的高效便捷变量保存读取!**

简洁快速的保存和读取变量, 方便的版本控制.

## 安装

    pip install -U celldict

## 简介

`celldict` 由 `CellDict` 和 `CellTable` 两个类构成.

`CellDict` 是文件型的 Key-value 数据结构, 支持版本控制, 支持多线程读写并发, 支持多进程读写与只读模式.

`CellTable` 是文件型的表数据结构, 支持不规整数据, 支持修改删除操作记录, 支持多线程读写并发, 支持多进程读写与只读模式.

## CellDict
```
from celldict import CellDict

# 数据集名称为 "dataname", 修改记录保存三次
cdict = CellDict("dataname", version_record=3, root_path=".CellDict")

# 保存数据
cdict.set("key", "value")
cdict.set("Hello", "world")
cdict["test"] = "any data"

# 读取数据
cdict.get("key")
cdict["test"]

# 删除数据 成功返回 True
cdict.delete("test")
del cdict["test"]

# 获取 keys
cdict.keys()

# 多版本控制
# version_record=3 修改记录保存三次
cdict.set("test", 1) # 最旧版本 被覆盖
cdict.set("test", 2) # 覆盖后的最旧记录
cdict.set("test", 3)
cdict.set("test", 4) # 最新版本记录

# 读取最新记录 4
cdict.get("test", "last")
# 读取最旧记录 2
cdict.get("test", "former")

# 按索引读取
cdict.get("test", 0) # 4
cdict.get("test", 1) # 3
cdict.get("test", 2) # 2
cdict.get("test", -1) # 2
cdict.get("test", -2) # 3
cdict.get("test", -3) # 4

# 读取所有版本数据
cdict.getall("test")
```

## CellTable
```
from celldict import CellTable

ctable = CellTable("dataname", root_path=".CellTable")

# 增加一条记录, 返回保存的主键
ctable.add("Hello World!") # 0
ctable.add([1, 2, 3, 4]) # 1
..
ctable.add("any data") # n

# 读取对应键值的数据
ctable.get(0) # "Hello World!"
ctable[1] # [1, 2, 3, 4]
ctable[2] # "any data"

# 读取指定键值的数据返回列表
ctable[0, 2] # ["Hello World!", "any data"]

# 通过切片获取值, 索引为键值
ctable[1:] # [[1, 2, 3, 4], 'any data']

# 通过时间取值
from datetime import datetime
# 获取 datetime 日期内插入的数据, 时分秒为零
key = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
ctable[key] # ['Hello World!', [1, 2, 3, 4], 'any data']
# 获取时间间隔内插入的数据
start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
end = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
ctable[start : end]

# 修改值, 修改记录保存在 modify 文件夹中
ctable.set(2, "modify data")
ctable[2] = "modify data"

# 删除值, 删除记录保存在 delete 文件夹中
ctable.delete(2)
del ctable[2]
```

`CellTable` 优势在于对数据结构没有限制, 可以方便的拓展和去除数据, 且不需要写sql语句, 效率也比 sqlite 高, 使用起来也很方便.