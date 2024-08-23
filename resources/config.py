import os

current_file_dir = os.path.dirname(os.path.abspath(__file__))


class Config:
    INI_SECTION = 'default'
    INI_KEY_INSTALL_PATH = 'install_path'
    INI_KEY_DATA_PATH = 'data_path'
    INI_KEY_VER_PATH = 'last_ver_path'
    INI_KEY_SCREEN_SIZE = 'screen_size'
    INI_KEY_LOGIN_SIZE = 'login_size'
    PROJ_PATH = os.path.abspath(os.path.join(current_file_dir, '..'))
    PROJ_USER_PATH = fr'{PROJ_PATH}\user_files'
    PROJ_EXTERNAL_RES_PATH = fr'{PROJ_PATH}\external_res'
    ACC_DATA_JSON_PATH = fr'{PROJ_USER_PATH}\account_data.json'
    SETTING_INI_PATH = fr'{PROJ_USER_PATH}\setting.ini'
    MULTI_SUBPROCESS = fr'{PROJ_EXTERNAL_RES_PATH}\WeChatMultiple.exe'
    PROJ_ICO_PATH = fr'{PROJ_EXTERNAL_RES_PATH}\SunnyMultiWxMng.ico'
