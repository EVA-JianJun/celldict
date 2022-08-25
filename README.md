# CellDict

**Python 文件型配置! 细胞字典, 简单高效安全的保存读取程序变量!**

方便高效的把程序数据变量保存为文件, 高效快速的读取, 且可以进行版本控制.

## 安装

    pip install -U celldict

## 简介

`CellDict` 主要用于保存程序中的一些变量, 或者一些配置, 程序下次重启的时候可以快速的读取这些变量, 实现的方式很简单, 就直接 `pickle` 保存读取, 有个类似的包 `shelve` 也有这个功能, 但是 `shelve` 在持续不断的写入数据的时候有概率会造成数据丢失,所以才有了 `CellDict` 这个包, 因为实现的很简单, 所以很安全, 且我为 `CellDict` 加了版本控制的功能, 一些重要的变量可以用版本控制保存过时的信息.

## 例子
```
    from celldict import CellDict

    # 数据集名称为 "name", 修改记录保存三次
    cell = CellDict("name", version_record=3)

    cell.set("data1", 1)
    cell.set("data2", "Hello CellDict!")

    # out 1
    cell.get("data1")
    # out "Hello CellDict!"
    cell.get("data2")

    # version参数控制获取数据的版本
    def get(self, key, version="last"):
        """
        文档:
            获取数据

        参数:
            key : str
                数据名称
            version : str or int  (default: "last")
                序号获取的版本, 默认获取最新的
                    str:
                        "last"     : 最新记录
                        "former"   : 最旧记录
                    int:
                        0   :   最新记录
                        1   :   次新记录
                        2   :   第三新记录
                        ..
                        n   :   第n-1新记录

                        -1  :   最旧记录
                        -2  :   次旧记录
                        ..
                        -n  :   第n旧记录
        返回:
            返回数据
        """
```
