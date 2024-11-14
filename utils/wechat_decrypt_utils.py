import binascii
import ctypes
import hashlib
import hmac
import os
import shutil
import struct
import sys
import time
from pathlib import Path

import psutil
import pymem
import win32api
from Crypto.Cipher import AES
from _ctypes import byref, sizeof, Structure
from win32con import PROCESS_ALL_ACCESS

from resources.config import Config
from utils.logger_utils import mylogger as logger

IV_SIZE = 16
HMAC_SHA1_SIZE = 20
cfg_file = os.path.basename(sys.argv[0]).split('.')[0] + '.ini'

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000
# 几种内存段可以写入的类型
MEMORY_WRITE_PROTECTIONS = {0x40: "PAGEEXECUTE_READWRITE", 0x80: "PAGE_EXECUTE_WRITECOPY", 0x04: "PAGE_READWRITE",
                            0x08: "PAGE_WRITECOPY"}

class MemoryBasicInformation(Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_uint32),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_uint32),
        ("Protect", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
    ]


# 第一步：找key -> 1. 判断可写
def is_writable_region(pid, address):  # 判断给定的内存地址是否是可写内存区域，因为可写内存区域，才能指针指到这里写数据
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    mbi = MemoryBasicInformation()
    mbi_pointer = byref(mbi)
    size = sizeof(mbi)
    success = ctypes.windll.kernel32.VirtualQueryEx(
        process_handle,
        ctypes.c_void_p(address),  # 64位系统的话，会提示int超范围，这里把指针转换下
        mbi_pointer,
        size)
    ctypes.windll.kernel32.CloseHandle(process_handle)
    if not success:
        return False
    if not success == size:
        return False
    return mbi.Protect in MEMORY_WRITE_PROTECTIONS


# 第一步：找key -> 2. 检验是否正确
def check_sqlite_pass(db_file, password):
    db_file = Path(db_file)
    if type(password) is str:  # 要是类型是string的，就转bytes
        password = bytes.fromhex(password.replace(' ', ''))
    with open(db_file, 'rb') as (f):
        salt = f.read(16)  # 开头的16字节做salt
        first_page_data = f.read(DEFAULT_PAGESIZE - 16)  # 从开头第16字节开始到DEFAULT_PAGESIZE整个第一页
    if not len(salt) == 16:
        logger.error(f"{db_file} read failed ")
        return False
    if not len(first_page_data) == DEFAULT_PAGESIZE - 16:
        logger.error(f"{db_file} read failed ")
        return False
    # print(f"{salt=}")
    # print(f"{first_page_data=}")
    key = hashlib.pbkdf2_hmac('sha1', password, salt, DEFAULT_ITER, KEY_SIZE)
    mac_salt = bytes([x ^ 58 for x in salt])
    mac_key = hashlib.pbkdf2_hmac('sha1', key, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, digestmod='sha1')
    hash_mac.update(first_page_data[:-32])
    for update_func in [
        lambda: hash_mac.update(struct.pack('=I', 1)),
        lambda: hash_mac.update(bytes(ctypes.c_int(1))),
    ]:
        hash_mac_copy = hash_mac.copy()  # 复制 hash_mac，避免每次循环修改原 hash_mac
        update_func()  # 执行 update 操作

        if hash_mac_copy.digest() == first_page_data[-32:-12]:
            logger.info(f"{db_file}, valid password Success")
            return True  # 匹配成功，返回 True

    logger.warning(f'{db_file}, valid password Error')
    return False  # 所有尝试失败，返回 False


# 第一步：拷贝数据库文件和找key
def copy_db_and_get_acc_key_by_pid(pid, account):
    logger.info("遍历微信内存，去暴力找key......")
    phone_types = [b'android\x00', b'iphone\x00']
    try:
        pm = pymem.Pymem()
        pm.open_process_from_id(pid)
        p = psutil.Process(pid)
        version_info = win32api.GetFileVersionInfo(p.exe(), '\\')  # type: ignore
        version = (
            f"{win32api.HIWORD(version_info['FileVersionMS'])}."  # type: ignore
            f"{win32api.LOWORD(version_info['FileVersionMS'])}."  # type: ignore
            f"{win32api.HIWORD(version_info['FileVersionLS'])}."  # type: ignore
            f"{win32api.LOWORD(version_info['FileVersionLS'])}"  # type: ignore
        )
        logger.info(f"wechat version：{version}, wechat pid: {pid}")

        targetdb = [f.path for f in p.open_files() if f.path[-11:] == 'MicroMsg.db']
        logger.info(f"找到MicroMsg：{targetdb}")

        if len(targetdb) < 1:
            sys.exit(-1)
        else:
            # 将数据库文件拷贝到项目
            usr_dir = Config.PROJ_USER_PATH
            file_mm = usr_dir + rf"\{account}\{account}_MicroMsg.db"
            if not os.path.exists(os.path.dirname(file_mm)):
                os.makedirs(os.path.dirname(file_mm))
            shutil.copyfile(targetdb[0], file_mm)

        misc_dbs = [f.path for f in p.open_files() if f.path[-7:] == 'Misc.db']
        if len(misc_dbs) < 1:
            logger.error("没有找到微信当前打开的数据文件，是不是你的微信还没有登录？？")
            sys.exit(-1)

        db_file = misc_dbs[0]  # 在wechat.exe打开文件列表里面，找到最后文件名是Misc.db的，用这个做db_file,做校验
        logger.info(f"db_file:{db_file}")
        min_entrypoint = min([m.EntryPoint for m in pm.list_modules() if
                              m.EntryPoint is not None])  # 遍历wechat载入的所有模块（包括它自己），找到所有模块最小的入口地址
        min_base = min([m.lpBaseOfDll for m in pm.list_modules() if
                        m.lpBaseOfDll is not None])  # 遍历wechat载入的所有模块（包括它自己），找到所有模块最小的基址
        min_address = min(min_entrypoint, min_base)  # 找到wechat最低的内存地址段
        # mylog.info(f"min_address:{min_address:X}")
        phone_addr = None
        for phone_type in phone_types:
            res = pm.pattern_scan_module(phone_type, "WeChatWin.dll",
                                         return_multiple=True)  # 只在 WeChatWin.dll 这个模块的内存地址段中去寻找电话类型的地址
            if res:
                phone_addr = res[-1]  # 地址选搜到的最后一个地址
                break
        if not phone_addr:
            # mylog.error(f"没有找到电话类型之一的关键字{phone_types}")
            sys.exit(-1)
        logger.info(f"phone_addr:{phone_addr:X}")
        # key_addr=pm.pattern_scan_all(hex_key)
        i = phone_addr  # 从找到的电话类型地址，作为基址，从后往前进行查找
        key = None
        str_key = None
        logger.info(f"正在从电话类型基址的附近查找……")
        end_time = time.time() + 5
        k = 0

        # 判断操作系统位数，只需执行一次
        if phone_addr <= 2 ** 32:  # 如果是32位
            is_32bit = True
            logger.info(f"使用32位寻址去找key")
        else:  # 如果是64位
            is_32bit = False
            logger.info(f"使用64位寻址去找key")

        while i > min_address:
            # j 的数列：-1,2,-3,4,-5...
            k = k + 1
            j = (k if k % 2 != 0 else -k)
            i += j
            if is_32bit:
                key_addr_bytes = pm.read_bytes(i, 4)  # 32位寻址下，地址指针占4个字节，找到存key的地址指针
                key_addr = struct.unpack('<I', key_addr_bytes)[0]
            else:
                key_addr_bytes = pm.read_bytes(i, 8)  # 64位寻址下，地址指针占8个字节，找到存key的地址指针
                key_addr = struct.unpack('<Q', key_addr_bytes)[0]
            if not is_writable_region(pm.process_id, key_addr):  # 要是这个指针指向的区域不能写，那也跳过
                continue

            key = pm.read_bytes(key_addr, 32)
            logger.info(f"i={i},key_addr={key_addr},key={key}")
            if check_sqlite_pass(db_file, key):
                # 到这里就是找到了……
                str_key = binascii.hexlify(key).decode()
                logger.info(f"found key pointer addr:{i:X}, key_addr:{key_addr:X}")
                logger.info(f"str_key:{str_key}")
                logger.info(f"查找用时：{time.time() + 5 - end_time:.4f}秒")
                return str_key
            else:
                key = None
            if time.time() > end_time:
                logger.info(f"超时了")
                break
        if not key:
            logger.error("没有找到key")
            return
    except Exception as e:
        logger.error(f"has some exception {e}")


# 第二步：解密
def decrypt_db_file_by_str_key_res(db_file_path, str_key_res):
    logger.info("正在对数据库解密......")
    print("成功获取key，正在对数据库解密...")
    sqlite_file_header = bytes("SQLite format 3", encoding='ASCII') + bytes(1)  # 文件头
    str_key = bytes.fromhex(str_key_res.replace(' ', ''))

    with open(db_file_path, 'rb') as f:
        blist = f.read()
    logger.info(f"数据库文件长度：{len(blist)}")

    salt = blist[:16]  # 微信将文件头换成了盐
    key = hashlib.pbkdf2_hmac('sha1', str_key, salt, DEFAULT_ITER, KEY_SIZE)  # 获得Key
    logger.info(f"str_key={str_key}, salt={salt}, key={key}")

    first = blist[16:DEFAULT_PAGESIZE]  # 丢掉salt
    mac_salt = bytes([x ^ 0x3a for x in salt])
    mac_key = hashlib.pbkdf2_hmac('sha1', key, mac_salt, 2, KEY_SIZE)
    logger.info(f"key={key}, mac_salt={mac_salt}, mac_key={mac_key}")

    hash_mac = hmac.new(mac_key, digestmod='sha1')  # 用第一页的Hash测试一下
    hash_mac.update(first[:-32])
    for update_func in [
        lambda: hash_mac.update(struct.pack('=I', 1)),
        lambda: hash_mac.update(bytes(ctypes.c_int(1))),
    ]:
        hash_mac_copy = hash_mac.copy()  # 先复制 hash_mac，避免每次循环修改原 hash_mac
        update_func()  # 执行 update 操作
        if hash_mac_copy.digest() == first[-32:-12]:
            logger.info(f'Correct Password: {mac_key}')
            break
    else:
        logger.info(f'Correct Password: {mac_key}')
        raise RuntimeError(f'Wrong Password: {mac_key}')

    print("解密成功，数据库写入解密后的内容...")
    blist = [blist[i:i + DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE, len(blist), DEFAULT_PAGESIZE)]
    # print(blist)

    new_db_file_path = None

    if os.path.exists(db_file_path):
        logger.info(f"数据库源：{db_file_path}")
        if os.path.isdir(db_file_path):
            pass
        elif os.path.isfile(db_file_path):
            index = db_file_path.rfind("\\")
            origin = db_file_path[index + 1:]
            new_db_file_path = db_file_path.replace(origin, "edit_" + origin)
    else:
        logger.error(db_file_path, "不存在")
        raise FileNotFoundError('db文件已经不存在！')

    with open(new_db_file_path, 'wb') as f:
        f.write(sqlite_file_header)  # 写入文件头
        t = AES.new(key, AES.MODE_CBC, first[-48:-32])
        f.write(t.decrypt(first[:-48]))
        f.write(first[-48:])
        for i in blist:
            t = AES.new(key, AES.MODE_CBC, i[-48:-32])
            f.write(t.decrypt(i[:-48]))
            f.write(i[-48:])

    logger.info(f"写入成功：{new_db_file_path}")
    os.remove(db_file_path)


# 使用pid进行数据库解密
def decrypt_acc_and_copy_by_pid(pid, account):
    # 获取pid对应账号的wechat key
    str_key = copy_db_and_get_acc_key_by_pid(pid, account)
    if str_key is None:
        return "超时，获取key失败"
    str_key_res = ' '.join([str_key[i:i + 2] for i in range(0, len(str_key), 2)])
    usr_dir = Config.PROJ_USER_PATH
    file_mm = usr_dir + rf"\{account}\{account}_MicroMsg.db"
    logger.info(f"copied file:{file_mm}")
    logger.info(f"str_key={str_key},str_key_res={str_key_res}")

    try:
        decrypt_db_file_by_str_key_res(file_mm, str_key_res)
    except Exception as e:
        logger.error(e)
        return "解密数据库失败"
