
import os
import uuid
import pickle
import traceback
from datetime import datetime

class CellDict():
    """ 文件型字典 """
    def __init__(self, name, version_record=3):
        """
        文档:
            初始化

        参数:
            name : str
                数据集名称
            version_record : int or None (default: 3)
                版本记录
                每次修改会保留上次记录, version_record设置保存的记录数量, 设置为None保留全部记录(根据数据大小会占用硬盘)
        """

        self.name = name
        self.version_record = version_record

        self.cell_path = os.path.join(".CellDict", self.name)

        # 初始化
        self._init_path()

    def _init_path(self):
        """ 初始化路径 """
        if not os.path.isdir(self.cell_path):
            os.makedirs(self.cell_path)

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
        value_path = os.path.join(self.cell_path, key)
        if not os.path.isdir(value_path):
            raise FileNotFoundError("记录路径不存在!")

        if version == "last":
            version = 0
        elif version == "former":
            version = -1

        value_file_path_list = sorted(os.listdir(value_path), reverse=True)

        try:
            value_file_name = value_file_path_list[version]
        except IndexError:
            print("已经有的版本:\n{0}".format(value_file_path_list))
            raise IndexError("获取的版本不存在!")

        try:
            value_file_path = os.path.join(value_path, value_file_name)
            with open(value_file_path, "rb") as frb:
                value = pickle.load(frb)
        except Exception as err:
            print("读取数据错误!")
            traceback.print_exc()
            print(err)
            raise err

        return value

    def get_all(self, key):
        """
        文档:
            获取key下所有数据

        参数:
            key : str
                数据名称
        返回:
            返回数据字典
        """
        value_path = os.path.join(self.cell_path, key)
        if not os.path.isdir(value_path):
            raise FileNotFoundError("记录路径不存在!")

        value_file_name_list = sorted(os.listdir(value_path), reverse=True)

        data_dict = {}
        for value_file_name in value_file_name_list:
            try:
                value_file_path = os.path.join(value_path, value_file_name)
                with open(value_file_path, "rb") as frb:
                    value = pickle.load(frb)
            except Exception as err:
                print("读取数据错误!")
                traceback.print_exc()
                print(err)
            else:
                data_dict[value_file_name] = value

        return data_dict

    def set(self, key, value, version_record="Default"):
        """
        文档:
            存储数据

        参数:
            key : str
                名称
            value : all type
                数据
            version_record : int or None or "Default" (default: "Default")
                版本记录
                每次修改会保留上次记录, version_record设置保存的记录数量, 设置为None保留全部记录(根据数据大小会占用硬盘)
                默认为 "Default" 会使用系统 self.version_record
        """
        value_path = os.path.join(self.cell_path, key)
        if not os.path.isdir(value_path):
            os.makedirs(value_path)

        file_name = "{0}_{1}".format(datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'), uuid.uuid1())
        value_file_path = os.path.join(value_path, file_name)

        # 保存文件
        try:
            with open(value_file_path, "wb") as fwb:
                pickle.dump(value, fwb)
        except Exception as err:
            traceback.print_exc()
            print(err)
            raise(ValueError("保存数据失败!"))

        # 清理过时文件
        if version_record == "Default":
            version_record = self.version_record
        if version_record:
            value_file_path_list = sorted(os.listdir(value_path), reverse=True)
            need_del_file_name_list = value_file_path_list[version_record:]
            for need_del_file_name in need_del_file_name_list:
                need_del_file_path = os.path.join(value_path, need_del_file_name)
                os.remove(need_del_file_path)
