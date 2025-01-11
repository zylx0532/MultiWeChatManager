import ctypes
import sys
import time
from ctypes import wintypes

import win32api
import tkinter as tk
import win32gui
import win32con
import uiautomation as auto
import pygetwindow as gw
import comtypes.client

from utils.logger_utils import mylogger as logger

# set coinit_flags (there will be a warning message printed in console by pywinauto, you may ignore that)
sys.coinit_flags = 2  # COINIT_APARTMENTTHREADED
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto import Application

# 定义一些必要的 Windows API 函数和结构
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

EnumChildWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

# 定义常量：窗口显示状态
SW_HIDE = 0  # 隐藏窗口
SW_SHOWNORMAL = 1  # 恢复窗口（普通显示）
SW_SHOWMINIMIZED = 2  # 最小化窗口
SW_SHOWMAXIMIZED = 3  # 最大化窗口

# 加载 user32.dll 动态库
user32 = ctypes.WinDLL("user32", use_last_error=True)

# 定义 Windows API 函数
FindWindow = user32.FindWindowW
FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindow.restype = wintypes.HWND

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, wintypes.INT]
ShowWindow.restype = wintypes.BOOL

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL

"""hwnd获取"""


def get_a_hwnd_by_title(window_title):
    """
    根据窗口标题查找窗口句柄。
    :param window_title: 窗口标题
    :return: 窗口句柄 (HWND)
    """
    hwnd = FindWindow(None, window_title)
    if hwnd == 0:
        raise ValueError(f"窗口 '{window_title}' 未找到。")
    return hwnd


def get_hwnd_list_by_class_and_title(class_name, window_title=None):
    def enum_wnd_callback(hwnd, results):
        # 获取窗口的类名和标题
        if win32gui.IsWindowVisible(hwnd):
            curr_class_name = win32gui.GetClassName(hwnd)
            curr_window_title = win32gui.GetWindowText(hwnd)
            # 仅匹配类名，若window_title不为空则继续匹配标题
            if curr_class_name == class_name and (window_title is None or curr_window_title == window_title):
                results.append(hwnd)

    hwnd_list = []
    win32gui.EnumWindows(enum_wnd_callback, hwnd_list)
    return hwnd_list


def get_hwnd_list_by_pid_and_class(pid, target_class_name):
    def enum_windows_callback(hwnd, _lParam):
        # 获取窗口所属的进程 ID
        process_id = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

        # 检查是否是目标进程的窗口
        if process_id.value == pid:
            class_name = ctypes.create_unicode_buffer(256)
            GetClassName(hwnd, class_name, 256)

            # 检查窗口类名是否匹配
            if class_name.value == target_class_name:
                hwnd_list.append(hwnd)
        return True

    hwnd_list = []
    EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    return hwnd_list


def wait_open_to_get_hwnd(class_name, timeout=30, title=None):
    """等待指定类名的窗口打开，并返回窗口句柄"""
    end_time = time.time() + timeout
    while time.time() < end_time:
        hwnd = win32gui.FindWindow(class_name, title)
        if hwnd:
            return hwnd  # 返回窗口句柄
        time.sleep(0.5)
    return None  # 未找到窗口，返回 None


"""hwnd内部控件获取"""


def get_widget_center_pos_by_hwnd_and_possible_titles(main_hwnd, possible_child_title, control_type="Button"):
    """获取指定控件中点的相对位置"""
    try:
        start_time = time.time()
        # 连接到应用程序窗口
        app = Application(backend="uia").connect(handle=main_hwnd)
        print(f"连接到应用程序窗口耗时：{time.time() - start_time:.4f}秒")
        # 获取主窗口对象
        main_window = app.window(handle=main_hwnd)
        print(f"获取主窗口对象耗时：{time.time() - start_time:.4f}秒")
        for t in possible_child_title:
            try:
                # 查找 "进入微信" 按钮
                wechat_button = main_window.child_window(title=t, control_type=control_type)
                print(f"查找按钮耗时：{time.time() - start_time:.4f}秒")
                if wechat_button.exists():
                    # 获取主窗口的矩形区域（绝对位置）
                    main_window_rect = main_window.rectangle()
                    print(f"获取主窗口矩形区域耗时：{time.time() - start_time:.4f}秒")
                    # 获取按钮的矩形区域（绝对位置）
                    button_rect = wechat_button.rectangle()
                    print(f"获取按钮矩形区域耗时：{time.time() - start_time:.4f}秒")
                    # 计算按钮相对于主窗口的相对位置
                    relative_x = button_rect.left - main_window_rect.left
                    relative_y = button_rect.top - main_window_rect.top
                    relative_center_x = button_rect.mid_point().x - main_window_rect.left
                    relative_center_y = button_rect.mid_point().y - main_window_rect.top
                    print(f"计算按钮相对位置耗时：{time.time() - start_time:.4f}秒")

                    print(f"相对于主窗口的左上角位置: ({relative_x}, {relative_y})")
                    print(f"相对于主窗口的中心位置: ({relative_center_x}, {relative_center_y})")
                    return relative_center_x, relative_center_y
                else:
                    print(f"未找到，耗时：{time.time() - start_time:.4f}秒")
                    print(f"Button '{t}' not found!")
                    continue
            except Exception as e:
                logger.error(e)
    except Exception as ex:
        logger.error(ex)
    return None, None


# 方法 1: 使用 uiautomation
def find_widget_with_uiautomation(hwnd, title, _control_type="Button"):
    auto.SetGlobalSearchTimeout(0.5)
    try:
        # 获取窗口对象
        window = auto.ControlFromHandle(hwnd)
        for t in title:
            try:
                # 查找控件
                widget = window.Control(searchDepth=10, Name=t)
                if widget:
                    rect = widget.BoundingRectangle
                    main_rect = window.BoundingRectangle
                    center_x = (rect.left + rect.right) // 2 - main_rect.left
                    center_y = (rect.top + rect.bottom) // 2 - main_rect.top
                    return center_x, center_y
            except Exception as ex:
                print(ex)
        return None, None
    except Exception as e:
        print(f"uiautomation error: {e}")
        return None, None


# 方法 2: 使用 win32gui
def find_widget_with_win32(hwnd, titles, _control_type="Button"):
    def callback(child_hwnd, result):
        child_title = win32gui.GetWindowText(child_hwnd)
        print(child_hwnd, child_title)
        for title in titles:
            print(title)
            if title in child_title:
                result.append(child_hwnd)
                break  # 找到匹配的标题后跳出循环

    try:
        child_windows = []
        win32gui.EnumChildWindows(hwnd, callback, child_windows)
        if child_windows:
            button_hwnd = child_windows[0]
            # 获取按钮和主窗口位置
            button_rect = win32gui.GetWindowRect(button_hwnd)
            main_rect = win32gui.GetWindowRect(hwnd)
            center_x = (button_rect[0] + button_rect[2]) // 2 - main_rect[0]
            center_y = (button_rect[1] + button_rect[3]) // 2 - main_rect[1]
            return center_x, center_y
        return None, None
    except Exception as e:
        print(f"win32gui error: {e}")
        return None, None


# 方法 3: 使用 pygetwindow (仅适用于简单窗口标题匹配)  （：确实）
def find_widget_with_pygetwindow(hwnd, title, _control_type="Button"):
    if hwnd is None:
        pass
    for t in title:
        print(t)
        try:
            windows = gw.getWindowsWithTitle(t)
            if windows:
                window = windows[0]
                rect = window._rect
                center_x = rect.center.x - rect.left
                center_y = rect.center.y - rect.top
                return center_x, center_y
        except Exception as e:
            print(f"pygetwindow error: {e}")
            continue
    return None, None


# 方法 4: 使用 Windows Automation API (UIAutomationCore)（：问题较大，择日再看吧）
def find_widget_with_uia(hwnd, title, _control_type="Button"):
    try:
        uia = comtypes.client.CreateObject('UIAutomationClient.CUIAutomation')
        element = uia.ElementFromHandle(hwnd)
        for t in title:
            print(t)
            try:
                condition = uia.CreatePropertyCondition(30005, title)  # 30005: Name 属性
                widget = element.FindFirst(2, condition)  # 2: 搜索范围为子控件
                if widget:
                    button_rect = widget.CurrentBoundingRectangle
                    main_rect = element.CurrentBoundingRectangle
                    center_x = (button_rect.left + button_rect.right) // 2 - main_rect.left
                    center_y = (button_rect.top + button_rect.bottom) // 2 - main_rect.top
                    return center_x, center_y
            except Exception as e:
                print(f"uiautomation error: {e}")
                continue
    except Exception as e:
        print(f"UIAutomation error: {e}")
    return None, None


def get_child_hwnd_list_of_(parent_hwnd):
    """
    获取指定父窗口句柄下的所有子窗口句柄。

    :param parent_hwnd: 父窗口句柄
    :return: 子窗口句柄列表
    """
    child_handles = []

    def enum_child_windows_proc(hwnd, _lParam):
        child_handles.append(hwnd)
        return True

    # 定义回调函数类型
    enum_proc = EnumChildWindowsProc(enum_child_windows_proc)

    # 调用 EnumChildWindows 来获取所有子窗口
    ctypes.windll.user32.EnumChildWindows(parent_hwnd, enum_proc, 0)

    return child_handles


def list_child_windows(hwnd):
    def callback(child_hwnd, _):
        child_title = win32gui.GetWindowText(child_hwnd)
        print(f"子窗口句柄: {child_hwnd}, 标题: {child_title}")

    win32gui.EnumChildWindows(hwnd, callback, None)


"""hwnd信息"""


def get_hwnd_details_of_(hwnd):
    """通过句柄获取窗口的尺寸和位置"""
    w = HwndWrapper(hwnd)
    if w.handle == hwnd:
        # print(f"{w.handle}")
        return {
            "window": w,
            "class": win32gui.GetClassName(w.handle),
            "handle": w.handle,
            "title": w.window_text(),
            "top": w.rectangle().top,
            "left": w.rectangle().left,
            "width": w.rectangle().width(),
            "height": w.rectangle().height()
        }

    return None  # 如果没有找到匹配的窗口句柄，返回 None


"""通过hwnd操作"""


def do_click_in_wnd(hwnd, cx, cy):
    """
    在窗口中的相对位置点击鼠标，可以后台
    :param hwnd: 句柄
    :param cx: 相对横坐标
    :param cy: 相对纵坐标
    :return: 无
    """
    long_position = win32api.MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
    print(f"要点击的handle：{hwnd}")
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)  # 模拟鼠标按下
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)  # 模拟鼠标弹起
    print(f"模拟点击按钮")


def minimize_window(hwnd):
    """
    最小化窗口。
    :param hwnd: 窗口句柄
    """
    ShowWindow(hwnd, SW_SHOWMINIMIZED)


def maximize_window(hwnd):
    """
    最大化窗口。
    :param hwnd: 窗口句柄
    """
    ShowWindow(hwnd, SW_SHOWMAXIMIZED)


def restore_window(hwnd):
    """
    恢复窗口。
    :param hwnd: 窗口句柄
    """
    ShowWindow(hwnd, SW_SHOWNORMAL)


def hide_window(hwnd):
    """
    隐藏窗口。
    :param hwnd: 窗口句柄
    """
    ShowWindow(hwnd, SW_HIDE)


def is_window_visible(hwnd):
    """
    检查窗口是否可见。
    :param hwnd: 窗口句柄
    :return: True/False
    """
    return bool(IsWindowVisible(hwnd))


def bring_hwnd_next_to_left_of_hwnd2(hwnd1, hwnd2):
    """
    将窗口1移动到窗口2的左侧。
    :param hwnd1: 窗口1句柄
    :param hwnd2: 窗口2句柄
    """
    # 获取窗口1和窗口2的矩形位置
    window1_rect = win32gui.GetWindowRect(hwnd1)  # (left, top, right, bottom)
    window2_rect = win32gui.GetWindowRect(hwnd2)
    # print(window1_rect, window2_rect)

    # 计算窗口1的新位置
    new_x = window2_rect[0] - (window1_rect[2] - window1_rect[0])  # 窗口1的左上角 x 坐标

    # 移动窗口1到计算后的新位置
    win32gui.SetWindowPos(
        hwnd1,
        win32con.HWND_TOP,  # 保持窗口在最上层
        new_x,
        window1_rect[1],
        0,
        0,
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE  # 不改变Z顺序，不激活窗口
    )


def wait_hwnd_close(hwnd, timeout=30):
    """等待指定窗口句柄的窗口关闭"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if win32gui.IsWindow(hwnd) == 0:  # 检查窗口是否存在
            return True
        time.sleep(0.5)
    return False


"""通过class操作"""


def close_by_wnd_class(wnd_class):
    login_window = win32gui.FindWindow(wnd_class, None)
    if login_window:
        win32gui.PostMessage(login_window, win32con.WM_CLOSE, 0, 0)


def hide_all_by_wnd_classes(wnd_classes):
    """
    根据窗口类名隐藏所有匹配的窗口
    :param wnd_classes: 窗口类名列表
    :return: 无
    """
    for class_name in wnd_classes:
        try:
            hwnd = win32gui.FindWindow(class_name, None)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)  # 隐藏窗口
                time.sleep(0.1)  # 短暂延时避免过快查找
        except Exception as ex:
            logger.error(ex)


def close_all_by_wnd_classes(wnd_classes):
    """
    根据窗口类名关闭所有匹配的窗口
    :param wnd_classes: 窗口类名列表
    :return: 无
    """
    if wnd_classes is None:
        return
    if len(wnd_classes) == 0:
        return
    for class_name in wnd_classes:
        try:
            while True:
                hwnd = win32gui.FindWindow(class_name, None)
                if hwnd:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    time.sleep(0.5)  # 等待窗口关闭
                else:
                    print(f"已清理所有{class_name}窗口！")
                    break
        except Exception as ex:
            logger.error(ex)


"""tk窗口相关"""


def bring_tk_wnd_to_center(wnd, width=None, height=None):
    if not isinstance(wnd, (tk.Tk, tk.Toplevel)):
        raise ValueError("wnd 必须是 Tk 或 Toplevel 窗口实例")

    if width is None:
        width = wnd.winfo_width()
    if height is None:
        height = wnd.winfo_height()
    x = (wnd.winfo_screenwidth() // 2) - (width // 2)
    y = int(wnd.winfo_screenheight() // 2.15) - int(height // 2.15)
    wnd.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def bring_tk_wnd_to_left(wnd, width=None, height=None):
    if not isinstance(wnd, (tk.Tk, tk.Toplevel)):
        raise ValueError("wnd 必须是 Tk 或 Toplevel 窗口实例")

    if width is None:
        width = wnd.winfo_width()
    if height is None:
        height = wnd.winfo_height()
    x = 0
    y = wnd.winfo_y()
    wnd.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def bring_tk_wnd_to_front(root, wnd, use_delay=True):
    if not isinstance(wnd, (tk.Tk, tk.Toplevel)):
        raise ValueError("wnd 必须是 Tk 或 Toplevel 窗口实例")

    if use_delay:
        root.after(200, lambda: wnd.lift())
        root.after(300, lambda: wnd.attributes('-topmost', True))
        root.after(400, lambda: wnd.attributes('-topmost', False))
        root.after(500, lambda: wnd.focus_force())
    else:
        wnd.lift()
        wnd.attributes('-topmost', True)
        wnd.attributes('-topmost', False)
        wnd.focus_force()


if __name__ == '__main__':
    pass

