import os
import time
from datetime import datetime

import psutil

import functions.func_setting as func_get_path
import utils.json_utils as json_utils
from resources.config import Config
from utils import process_utils


def wrap_text(text, max_width):
    """
    将文本按指定宽度换行，并且对超过这个长度的进行分两行处理，两行长度尽量相等
    :param text: 要处理的文本
    :param max_width: 每行最大字符数
    :return: 处理后的文本
    """
    wrapped_text = ""

    # 对每一段进行处理
    for i in range(0, len(text), max_width):
        segment = text[i:i + max_width]

        if len(segment) > max_width:
            # 如果段落的长度超过了一半，则将其均分成两行
            middle = (len(segment) + 1) // 2
            wrapped_text += segment[:middle] + "\n" + segment[middle:] + "\n"
        else:
            # 如果长度小于等于max_width // 2，直接添加并换行
            wrapped_text += segment + "\n"

    return wrapped_text.strip()  # 移除最后的换行符


def get_config_status(account):
    data_path = func_get_path.get_wechat_data_path()
    if not data_path:
        return "无法获取配置路径"

    config_path = os.path.join(data_path, "All Users", "config", f"{account}.data")
    if os.path.exists(config_path):
        mod_time = os.path.getmtime(config_path)
        date = datetime.fromtimestamp(mod_time)
        return f"{date.month}-{date.day} {date.hour:02}:{date.minute:02}"
    else:
        return "无配置"


class AccountManager:
    def __init__(self, account_data_file):
        self.account_data_file = account_data_file
        self.account_data = json_utils.load_json_data(self.account_data_file)

    def get_account_list(self):
        def get_files_by_pid_thread(process_id):
            db_paths = []  # 初始化空列表，用于存储符合条件的路径
            try:
                # 获取指定进程的内存映射文件路径
                for f in psutil.Process(process_id).memory_maps():
                    # 将路径中的反斜杠替换为正斜杠
                    normalized_path = f.path.replace('\\', '/')
                    # 检查路径是否以 data_path 开头
                    if normalized_path.startswith(data_path):
                        # 如果条件符合，将路径添加到列表中
                        db_paths.append(f.path)
            except psutil.AccessDenied:
                print(f"无法访问进程ID为 {process_id} 的内存映射文件，权限不足。")
            except psutil.NoSuchProcess:
                print(f"进程ID为 {process_id} 的进程不存在或已退出。")
            except Exception as e:
                print(f"发生意外错误: {e}")
            print(f"┌———通过内存获取进程{process_id}所有文件，已用时：{time.time() - start_time:.4f}秒")
            if db_paths:  # 如果存在匹配的文件路径
                db_file = db_paths[0]  # 取第一个匹配的文件路径
                print(db_file)
                path_parts = db_file.split(os.path.sep)
                try:
                    wxid_index = path_parts.index(os.path.basename(data_path)) + 1
                    wxid = path_parts[wxid_index]
                    wechat_processes.append((wxid, process_id))
                    logged_in_wxids.add(wxid)
                    print(f"└———获取进程{process_id}对应账号{wxid}，已用时：{time.time() - start_time:.4f}秒")
                    return logged_in_wxids
                except ValueError:
                    pass

        start_time = time.time()
        data_path = func_get_path.get_wechat_data_path()
        if not data_path:
            return None, None, None

        wechat_processes = []
        logged_in_wxids = set()

        pids = process_utils.get_process_ids_by_name("WeChat.exe")
        print(f"wechat_processes: {wechat_processes}")
        print(f"读取到微信所有进程，用时：{time.time() - start_time:.4f} 秒")
        # if len(pids) != 0:
        #     pool = ThreadPoolExecutor(max_workers=len(pids) + 1)
        #     pool.map(get_files_by_pid_thread, pids)
        for pid in pids:
            get_files_by_pid_thread(pid)
        print(f"完成判断进程对应账号，用时：{time.time() - start_time:.4f} 秒")

        # 获取文件夹并分类
        excluded_folders = {'All Users', 'Applet', 'Plugins', 'WMPF'}
        folders = set(
            folder for folder in os.listdir(data_path)
            if os.path.isdir(os.path.join(data_path, folder))
        ) - excluded_folders
        logged_in = list(logged_in_wxids & folders)
        not_logged_in = list(folders - logged_in_wxids)

        print("logged_in", logged_in)
        print("not_logged_in", not_logged_in)
        print(f"完成账号分类，用时：{time.time() - start_time:.4f} 秒")

        # 更新数据
        self.account_data = json_utils.load_json_data(Config.ACC_DATA_JSON_PATH)
        pid_dict = dict(wechat_processes)
        for acc in logged_in + not_logged_in:
            if acc not in self.account_data:
                self.account_data[acc] = {"note": ""}
            self.account_data[acc]["pid"] = pid_dict.get(acc)

        json_utils.save_json_data(self.account_data_file, self.account_data)
        print(f"完成记录账号对应pid，用时：{time.time() - start_time:.4f} 秒")

        return logged_in, not_logged_in, wechat_processes

    def update_note(self, account, note):
        self.account_data = json_utils.load_json_data(Config.ACC_DATA_JSON_PATH)
        if account not in self.account_data:
            self.account_data[account] = {}
        self.account_data[account]["note"] = note
        json_utils.save_json_data(self.account_data_file, self.account_data)

    def get_account_display_name(self, account):
        note = self.account_data.get(account, {}).get("note", None)
        nickname = self.account_data.get(account, {}).get("nickname", None)
        alias = self.account_data.get(account, {}).get("alias", None)
        if note:
            display_name = f"{note}"
        elif nickname:
            display_name = f"{nickname}"
        elif alias:
            display_name = f"{alias}"
        else:
            display_name = f"{account}"

        return wrap_text(display_name, 10)

    def get_account_note(self, account):
        return self.account_data.get(account, {}).get("note", "")

    def get_account_nickname(self, account):
        return self.account_data.get(account, {}).get("nickname", "")


if __name__ == '__main__':
    pass
    # account_manager = AccountManager("./account_data.json")
    # print(account_manager.account_data_file)
    # json_utils.save_json_data(account_manager)
    # print(account_manager.account_data)
    # print(account_manager.get_account_list())
