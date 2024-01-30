import os
import uuid
import time
import pickle
import shutil
import threading
import traceback
from datetime import datetime, timedelta

class CellDict():
    """ 文件型字典 """
    def __init__(self, name="cellname", version_record=3, root_path=".CellDict"):
        """
        文档:
            初始化 CellDict

            并发支持:
                线程安全 √
                    同进程不同对象任意读写.
                进程安全 ×
                    多进程同时写不安全,可能数据被覆盖.
                    一进程写其他进程读安全.
        参数:
            name : str (default: "cellname")
                数据集名称
            version_record : int or None (default: 3)
                版本记录
                每次修改会保留上次记录, 设置 version_record 保存的记录数量, 设置为None保留全部记录(根据数据大小会占用硬盘)
            root_path : str (default: ".CellDict")
                设置数据根目录
        """
        self.name = name
        self.version_record = version_record

        self._init_path(root_path)
        self._init_lock()

    """ 魔术方法 """
    def __getitem__(self, key):
        """
        文档:
            通过 cell[key] 获取值
        参数:
            key : str
                键
        返回:
            返回键对应的最新值
        """
        return self.get(key)

    def __setitem__(self, key, value):
        """
        文档:
            通过 cell[key] = value 设定值
        参数:
            key : str
                键
            value : any type
                值
        """
        self.set(key, value)

    def __delitem__(self, key):
        """
        文档:
            通过 del cell[key] 删除数据
        参数:
            key : str
                键
        """
        self.delete(key)

    """ 系统函数 """
    def _init_path(self, root_path):
        """ 初始化路径 """
        self.cell_path = os.path.join(root_path, self.name)
        if not os.path.isdir(self.cell_path):
            os.makedirs(self.cell_path)

    def _init_lock(self):
        """ 初始化锁 """
        try:
            os._celldict_lock
        except AttributeError:
            os._celldict_lock = {}

        abspath = os.path.abspath(self.cell_path)
        try:
            self._lock = os._celldict_lock[abspath]
        except KeyError:
            self._lock = os._celldict_lock[abspath] = threading.Lock()

    def _read_pickle(self, path):
        """ 读取 pickle 文件 """
        with open(path, "rb") as frb:
            return pickle.load(frb)

    def _write_pickle(self, path, data):
        """ 写入 pickle 文件 """
        with open(path, "wb") as fwb:
            pickle.dump(data, fwb)

    """ 用户函数 """
    def get(self, key, version="last"):
        """
        文档:
            获取数据

        参数:
            key : str
                键
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

        注意:
            这个函数可以支持确定的 key 下多进程访问, 出错会尝试再次读取
        """
        self._lock.acquire()
        try:
            # 检查目录
            value_path = os.path.join(self.cell_path, key)
            if not os.path.isdir(value_path):
                raise KeyError("{0} not found!".format(key))

            # 获取索引
            if version == "last":
                version = 0
            elif version == "former":
                version = -1

            start_time = time.time()
            while True:
                try:
                    # 每次读写都重新扫描文件计算文件路径
                    value = self._read_pickle(os.path.join(value_path, sorted(os.listdir(value_path), reverse=True)[version]))
                except (EOFError, FileNotFoundError) as err: # 其他进程正在写入
                    time.sleep(0.1)
                    if time.time() - start_time > 6:
                        raise err
                except IndexError as err:
                    err.args = ("获取的版本不存在!", )
                    raise err
                else:
                    # 读取成功
                    break

            return value
        finally:
            self._lock.release()

    def getall(self, key):
        """
        文档:
            获取key下所有历史版本数据 (不常用)

        参数:
            key : str
                键
        返回:
            返回数据字典
        注意:
            不支持多进程访问, 较易出错
        """
        self._lock.acquire()
        try:
            value_path = os.path.join(self.cell_path, key)
            if not os.path.isdir(value_path):
                raise KeyError("{0} not found!".format(key))

            value_file_name_list = sorted(os.listdir(value_path), reverse=True)

            data_dict = {}
            for value_file_name in value_file_name_list:
                try:
                    value_file_path = os.path.join(value_path, value_file_name)
                    value = self._read_pickle(value_file_path)
                except Exception as err:
                    print("读取数据错误!")
                    traceback.print_exc()
                    print(err)
                else:
                    data_dict[value_file_name] = value

            return data_dict
        finally:
            self._lock.release()

    def set(self, key, value, version_record="Default"):
        """
        文档:
            存储数据

        参数:
            key : str
                键
            value : any type
                值
            version_record : int or None or "Default" (default: "Default")
                版本记录
                每次修改会保留上次记录, version_record设置保存的记录数量, 设置为None保留全部记录(根据数据大小会占用硬盘)
                默认为 "Default" 会使用系统 self.version_record
        """
        self._lock.acquire()
        try:
            value_path = os.path.join(self.cell_path, key)
            if not os.path.isdir(value_path):
                os.makedirs(value_path)

            file_name = "{0}_{1}".format(datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'), uuid.uuid1())
            value_file_path = os.path.join(value_path, file_name)

            # 保存文件
            try:
                self._write_pickle(value_file_path, value)
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
                    try:
                        os.remove(need_del_file_path)
                    except (FileNotFoundError, PermissionError):
                        # 多进程同时写入清理过时文件可能会冲突
                        pass
        finally:
            self._lock.release()

    def keys(self, reverse=False):
        """
        文档:
            返回键值列表
        参数:
            reverse : bool (default: False)
                排序方向
        """
        self._lock.acquire()
        try:
            return sorted(os.listdir(self.cell_path), reverse=reverse)
        finally:
            self._lock.release()

    def delete(self, key):
        """
        文档:
            删除数据
        参数:
            key : str
                键
        """
        self._lock.acquire()
        value_path = os.path.join(self.cell_path, key)
        try:
            shutil.rmtree(value_path)
        except FileNotFoundError:
            return False
        else:
            return True
        finally:
            self._lock.release()

class CellTable():
    """
    简易的文件型表数据类.
    主键为 int 数字
    """
    def __init__(self, name, root_path=".CellTable"):
        """
        文档:
            初始化 CellTable

            并发支持:
                线程安全 √
                    同进程不同对象任意读写.
                进程安全 ×
                    多进程同时写不安全.
                    一进程写其他进程读安全.
            注意:
                进程并发虽然不安全, 但是支持读写分离的应用场景, 读写不冲突.

        参数:
            name : str
                表名称
            root_path : str (default: ".CellDict)
                设置数据根目录
        """
        self.name = name

        self._init_path(root_path)
        self._init_lock()
        self._init_primary_key()

    """ 魔术方法 """
    def __getitem__(self, items):
        """
        文档:
            通过 table[...] 的方式获取值
        参数:
            # 可以使用的方式有下面几种
            items : int or str
                table[key] 获取单个 id 值
            items : [x, y, ..]
                table[2, 6] 获取多个 id 值
            items : [start:end:step]
                table[start:end:step] 通过 slice 取值
            items : [datetime : hour 0 minute 0 second 0 microsecond 0]
                table[datetime] 获取 datetime 自然日内插入的数据值
            items : [datetime : hour 16 minute 0 second 0 microsecond 0]
                table[datetime] 获取 datetime CN 期货 上个夜盘日20点 到 当日16点 交易日内插入的数据
            items : [start datetime : end datetime]
                table[start datetime : end datetime] 获取 start datetime 至 end datetime 内插入的数据
        注意:
            使用日期获取数据是根据 `修改时间` 而不是 `创建时间`.
        返回:
            返回取到的值
        """
        if isinstance(items, int):
            # table[key]
            if items >= 0:
                return self.get(items)
            else:
                return self.get(self.keys()[items])
        elif isinstance(items, tuple):
            # table[2, 6]
            return [self.get(key) for key in items]
        elif isinstance(items, datetime):
            if items.hour == 0 and items.minute == 0 and items.second == 0 and items.microsecond == 0:
                # 获取 datetime 自然日内插入的数据值
                start_date = items
                end_date = items + timedelta(days=1) # 当日零点到第二日零点
                keys = self._get_keys(start_date, end_date)
                return [self.get(key) for key in keys]
            elif items.hour == 16 and items.minute == 0 and items.second == 0 and items.microsecond == 0:
                # 获取 datetime CN 期货 上个夜盘日20点 到 当日16点 交易日内插入的数据
                if items.weekday() == 0: # 周一
                    start_date = items - timedelta(days=3) # 周五 16 点
                else:
                    start_date = items - timedelta(days=1) # 前一日 16 点
                start_date = start_date.replace(hour=20) # 20 点
                end_date = items
                keys = self._get_keys(start_date, end_date)
                return [self.get(key) for key in keys]
            else:
                raise ValueError("参数错误!")
        elif isinstance(items, slice):
            if isinstance(items.start, datetime) and isinstance(items.stop, datetime):
                # 获取 start datetime 至 end datetime 内插入的数据
                start_date = items.start
                end_date = items.stop
                keys = self._get_keys(start_date, end_date)
                return [self.get(key) for key in keys]
            else:
                # table[start:end:step]
                return [self.get(key) for key in self.keys()[items]]
        else:
            raise ValueError("参数错误!")

    def __setitem__(self, key, value):
        """
        文档:
            通过 table[key] = value 设定值
        参数:
            key : str
                键
            value : any type
                值
        """
        self.set(key, value)

    def __delitem__(self, key):
        """
        文档:
            通过 del table[key] 删除数据
        参数:
            key : str
                键
        """
        self.delete(key)

    """ 系统函数 """
    def _init_path(self, root_path):
        """ 初始化路径 """
        self.cell_path = os.path.join(root_path, self.name) # 根路径
        self.cell_data_path = os.path.join(self.cell_path, "data") # 数据路径
        self.cell_modify_path = os.path.join(self.cell_path, "modify") # 修改记录路径
        self.cell_delete_path = os.path.join(self.cell_path, "delete") # 删除记录路径

        if not os.path.isdir(self.cell_path):
            os.makedirs(self.cell_path)
        if not os.path.isdir(self.cell_data_path):
            os.makedirs(self.cell_data_path)
        if not os.path.isdir(self.cell_modify_path):
            os.makedirs(self.cell_modify_path)
        if not os.path.isdir(self.cell_delete_path):
            os.makedirs(self.cell_delete_path)

    def _init_lock(self):
        """ 初始化锁 """
        try:
            os._celltable_lock
        except AttributeError:
            os._celltable_lock = {}

        self._abspath = os.path.abspath(self.cell_path)
        try:
            self._lock = os._celltable_lock[self._abspath]
        except KeyError:
            self._lock = os._celltable_lock[self._abspath] = threading.RLock()

    @property
    def primary_key(self):
        """ 全局主键 """
        return os._celltable_primary_key[self._abspath]

    def _init_primary_key(self):
        """ 初始化主键 """
        # 下一次写入的键值
        self._lock.acquire()
        try:
            try:
                os._celltable_primary_key
            except AttributeError:
                os._celltable_primary_key = {}

            try:
                self.primary_key # 尝试获取全局主键
            except KeyError:
                # 获取不到计算主键
                keys = self.keys()
                if keys:
                    primary_key = keys[-1] + 1
                else:
                    primary_key = 0
                os._celltable_primary_key[self._abspath] = primary_key
        finally:
            self._lock.release()

    def _read_pickle(self, path):
        """ 读取 pickle 文件 """
        with open(path, "rb") as frb:
            return pickle.load(frb)

    def _write_pickle(self, path, data):
        """ 写入 pickle 文件 """
        with open(path, "wb") as fwb:
            pickle.dump(data, fwb)

    def _plus_main_key(self):
        """ 自增主键 """
        os._celltable_primary_key[self._abspath] += 1

    def _get_keys(self, start_date, end_date):
        """ 获取一个时间段内的键值 """
        filter_keys = []
        start_timestamp = start_date.timestamp()
        end_timestamp = end_date.timestamp()
        for key in os.listdir(self.cell_data_path):
            data_file_path = os.path.join(self.cell_data_path, key) # 文件路径
            mdatetime = os.path.getmtime(data_file_path) # 获取修改时间
            if start_timestamp <= mdatetime <= end_timestamp:
                filter_keys.append(key)

        return sorted(map(int, filter_keys), key=int)

    """ 用户函数 """
    def add(self, value):
        """
        文档:
            添加一条记录
        参数:
            value : any type
                记录的数据
        """
        self._lock.acquire()
        try:
            self._write_pickle(os.path.join(self.cell_data_path, str(self.primary_key)), value)
            return self.primary_key
        finally:
            self._plus_main_key()
            self._lock.release()

    def set(self, key, value):
        """
        文档:
            设置或修改记录
        参数:
            key : str or int
                键
            value : any type
                记录的数据
        """
        self._lock.acquire()
        try:
            data_file_path = os.path.join(self.cell_data_path, str(key)) # 文件数据路径
            modify_file_path = os.path.join(self.cell_modify_path, str(key)) # 文件修改记录路径

            if os.path.isfile(data_file_path): # 如果老文件在

                mtime = os.path.getmtime(data_file_path) # 获取修改时间
                old_value = self._read_pickle(data_file_path) # 老文件信息

                # 老的修改信息列表
                try:
                    old_modify_info_list = self._read_pickle(modify_file_path)
                except FileNotFoundError:
                    old_modify_info_list = []

                old_modify_info_list.append([mtime, old_value]) # 添加修改记录信息

                self._write_pickle(modify_file_path, old_modify_info_list) # 保存修改记录文件

            self._write_pickle(data_file_path, value) # 保存数据文件
        finally:
            self._lock.release()

    def get(self, key):
        """
        文档:
            查询记录
        参数:
            key : str or int
                键
        返回:
            返回键对应的值
        """
        self._lock.acquire()
        try:
            start_time = time.time()
            while True:
                try:
                    return self._read_pickle(os.path.join(self.cell_data_path, str(key)))
                except (EOFError, FileNotFoundError) as err: # 其他进程正在写入 或 不存在
                    time.sleep(0.1)
                    if time.time() - start_time > 1:
                        raise KeyError(key)
        finally:
            self._lock.release()

    def delete(self, key):
        """
        文档:
            删除记录
        参数:
            key : str or int
                键
        """
        self._lock.acquire()
        try:
            data_file_path = os.path.join(self.cell_data_path, str(key)) # 文件数据路径
            delete_file_path = os.path.join(self.cell_delete_path, str(key)) # 文件删除记录路径

            if os.path.isfile(data_file_path): # 如果老文件在

                mtime = os.path.getmtime(data_file_path) # 获取修改时间
                old_value = self._read_pickle(data_file_path) # 老文件信息

                # 老的修改信息列表
                try:
                    old_delete_info_list = self._read_pickle(delete_file_path)
                except FileNotFoundError:
                    old_delete_info_list = []

                old_delete_info_list.append([mtime, time.time(), old_value]) # 添加删除记录信息

                self._write_pickle(delete_file_path, old_delete_info_list) # 保存修改记录文件

            try:
                os.remove(data_file_path) # 删除数据文件
            except FileNotFoundError:
                return False
            else:
                return True
        finally:
            self._lock.release()

    def keys(self, reverse=False):
        """
        文档:
            返回键值列表 (int)
        参数:
            reverse : bool (default: False)
                排序方向
        """
        self._lock.acquire()
        try:
            return sorted(map(int, os.listdir(self.cell_data_path)), reverse=reverse)
        finally:
            self._lock.release()

    def values(self):
        """
        文档:
            返回值列表
        """
        return [self.get(key) for key in self.keys()]

    def keys_values(self):
        """
        文档:
            返回 keys : values 字典
        """
        return {key : self.get(key) for key in self.keys()}