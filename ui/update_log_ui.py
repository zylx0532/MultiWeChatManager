import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk

from functions import func_update, subfunc_file
from resources import Config, Strings
from utils import handle_utils, file_utils


class UpdateLogWindow:
    def __init__(self, master, old_versions, new_versions=None):
        self.master = master
        master.title("版本日志" if not new_versions else "发现新版本")

        window_width = 600
        window_height = 500
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 禁用窗口大小调整
        master.resizable(False, False)

        # 移除窗口装饰并设置为工具窗口
        master.overrideredirect(True)
        master.overrideredirect(False)
        master.attributes('-toolwindow', True)

        main_frame = ttk.Frame(master, padding="5")
        main_frame.pack(fill="both", expand=True)

        # 更新日志(标题)
        log_label = ttk.Label(main_frame, text="更新日志", font=("", 11))
        log_label.pack(anchor='w', pady=(10, 0))

        print("显示更新日志")

        if not os.path.exists(Config.VER_ADAPTATION_JSON_PATH):
            config_data = subfunc_file.fetch_config_data()
        else:
            print("本地版本对照表存在，读取中...")
            try:
                with open(Config.VER_ADAPTATION_JSON_PATH, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except Exception as e:
                print(f"错误：读取本地 JSON 文件失败: {e}，尝试从云端下载")
                config_data = subfunc_file.fetch_config_data()
                print(f"从云端下载了文件：{config_data}")
                raise RuntimeError("本地 JSON 文件读取失败")

        # 创建一个用于放置滚动文本框的框架
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(pady=(5, 0), fill=tk.BOTH, expand=True)

        # 创建滚动条
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建不可编辑且可滚动的文本框
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("", 10), height=6, bg=master.cget("bg"),
                                yscrollcommand=scrollbar.set, bd=0, highlightthickness=0)

        # 需要显示新版本
        if new_versions:
            try:
                newest_version = file_utils.get_newest_full_version(new_versions)
                print(newest_version)
                newest_ver_url = config_data["update"][newest_version]["urls"]["default"]
                bottom_frame = ttk.Frame(main_frame)
                bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
                cancel_button = ttk.Button(bottom_frame, text="以后再说",
                                           command=lambda: self.master.destroy())
                cancel_button.pack(side=tk.RIGHT)
                download_button = ttk.Button(bottom_frame, text="下载新版",
                                             command=partial(self.show_download_window, file_urls=[newest_ver_url]))
                download_button.pack(side=tk.RIGHT)

                # 说明
                information_label = ttk.Label(
                    bottom_frame,
                    text="发现新版本，是否下载？"
                )
                information_label.pack(side=tk.RIGHT, pady=(5, 0))

                self.log_text.insert(tk.END, "新版本：\n")
                for v in new_versions:
                    self.log_text.insert(tk.END, v + "：\n")
                    self.log_text.insert(tk.END, "\n".join(config_data["update"][v]["logs"]))
                    self.log_text.insert(tk.END, "\n\n")
                self.log_text.insert(tk.END, "\n\n旧版本：\n")
            except Exception as e:
                print(e)
                messagebox.showerror("错误", f"发生错误：{e}")

        try:
            for v in old_versions:
                self.log_text.insert(tk.END, v + "：\n")
                self.log_text.insert(tk.END, "\n".join(config_data["update"][v]["logs"]))
                self.log_text.insert(tk.END, "\n\n")
        except Exception as e:
            print(e)
            messagebox.showerror("错误", f"发生错误：{e}")

        # 设置文本框为不可编辑
        self.log_text.config(state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 配置滚动条
        scrollbar.config(command=self.log_text.yview)

    def show_download_window(self, file_urls, download_path=None):
        if download_path is None:
            download_path = os.path.join(tempfile.mkdtemp(), "temp.zip")

        download_window = tk.Toplevel(self.master)
        download_window.title("下载更新")
        handle_utils.center_window(download_window)

        global progress_var, progress_bar
        progress_var = tk.StringVar(value="开始下载...")
        tk.Label(download_window, textvariable=progress_var).pack(pady=10)

        progress_bar = ttk.Progressbar(download_window, orient="horizontal", length=200, mode="determinate")
        progress_bar.pack(pady=10)

        close_and_update_btn = tk.Button(download_window, text="关闭并更新",
                                         command=partial(self.close_and_update, tmp_path=download_path))
        close_and_update_btn.pack(pady=10)
        close_and_update_btn.config(state="disabled")

        # 开始下载文件（多线程）
        t = threading.Thread(target=func_update.download_files,
                             args=(file_urls, download_path, self.update_progress,
                                   lambda: close_and_update_btn.config(state="normal")))
        t.start()

    def update_progress(self, idx, total_files, downloaded, total_length):
        percentage = (downloaded / total_length) * 100 if total_length else 0
        progress_var.set(f"下载文件 {idx + 1}/{total_files}: {percentage:.2f}% 完成")
        progress_bar['value'] = percentage
        self.master.update_idletasks()

    def close_and_update(self, tmp_path):
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            current_version = subfunc_file.get_app_current_version()
            install_dir = os.path.dirname(exe_path)

            update_exe_path = os.path.join(Config.PROJ_EXTERNAL_RES_PATH, 'update.exe')
            new_update_exe_path = os.path.join(os.path.dirname(tmp_path), 'update.exe')
            try:
                shutil.copy(update_exe_path, new_update_exe_path)
                print(f"成功将 {update_exe_path} 拷贝到 {new_update_exe_path}")
            except Exception as e:
                print(f"拷贝文件时出错: {e}")

            subprocess.Popen([new_update_exe_path, current_version, install_dir],
                             creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS)

# if __name__ == "__main__":
#     root = tk.Tk()
#     update_log_window = UpdateLogWindow(root, 'old')
#     root.mainloop()
