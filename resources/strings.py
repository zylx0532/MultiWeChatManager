class Strings:
    DEFAULT_AVATAR_BASE64 = "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7EVH/aUvt+VU6KAL41F+5FTR3qn7zCsqigDdSZG+62afWHHM0f3TV63vgcB2oAvUUgcOAR3paACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKmqGpqAIn6mkpX6mkoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiqt5cBEKjrj1oAZdXWMquQQazXcuSSc5oclySaSgAooooAKKKKACiiigAoyR0oooAuW14UOGJI6CtNDkA1gVoWVzjIPc45NAGhRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFTVDU1AET9TSUr9TSUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFADZH2IT6DNY9xJ5smeOnar19LsG3P3hWXQAUUUUAFFFFABRRRQAUUUUAFFFFABTkOHU+hptFAG1ay+bHnjrjipqy7GXDhM9TWpQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFTVDU1AET9TSUr9TSUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFB6GikP3T9KAMq+k3uPYVVqWY5eoqACiiigAooooAKKKKACiiigAooooAKKKKAJbc7JlPoa2Yn3oDWEnDg1s2ZzADQBNRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVNUNTUARP1NJSv1NJQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUjfcP0paQ9D9KAMF/vn60lSSDDn61HQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVsWP8Ax6rWQOorZs/+PZaAJqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACg9D9KKKAMa5TDioKvajHh1+lUaACiiigAooooAKKKKACiiigAooooAKKKKAHxDMgHvWzbjEIFZNquZ0+tbKDAxQAtFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABU1Q1NQBE/U0lK/U0lABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQBWvIt6E+grIrfcZBHqMVlXluY3JAOMdaAKtFFFABRRRQAUUUUAFFFFABRRRQAUUVLDG0jjAOM80AW7CLIDnsfStCmRRiNMCn0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABU1Q1NQBE/U0lK/U0lABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVFcRCSMjHJqWigDDljMblT2qOtW7tg6EgDJPWstwUJB7HFACUUUUAFFFFABRRRQAUUUUAKBk1qWdv5YJI68iobO2ycsAQRxWiBgCgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooACAayr2LYS3qa1ap6iMxj60AZdFFFABRRRQAUUUUAFS28fmSYqKrmnD99n2oA0o0CIB7U6iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKpai48sAdc1alkWNMmsm5mMjnk4zxQBBRRRQAUUUUAFFFFABVuwfE2D0xVSnxuYzkHFAG7RUNtMsoA5yBzmpqACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKmqGpqAIn6mkpX6mkoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKY8qp3H50APqGa4WIHvj0qpNfE5AHUY4NU3dmPJNAEk1yZScEgE9KgoooAKKKKACiiigAooooAKKKKAJI5WjPBNaVveLJgY9uayaUEjoaAN/I9aKyYbxo8AjPPc1oxXCyAZIBPbNAEtFGQaKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoopCcdaAFpryKn3jiq016iZAJzjjiqMty8mctwaALc99jOwqaoyStIcn1zxUdFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUqOUORSUUAX4b5hgNtAAq7HMknRgaw6kjneP7pxQBuUVRhvh0djnPHFXEkVxkUAOooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKACignFU7m8CZUDPvQBYluFiGTzzjis2a8Z/ulh+NQSSM5JyeTTKAFJJ6nNJRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFTxXLRkZZsemagooA17e6WTAwc4zzVkHNYAJHQ1etrzHBHtyaANGikDg9CKWgAooooAKKKKACiiigAooooAKKKKACiiigAqaoamoAifqaSlfqaSgAooooAKKKKACiiigAooooAKKKKACiiigCpezbAV45FZZJJyat6l/r/wAKp0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQBfsrgj5Tjk1o1iW/wDrk+tbdABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABU1Q1NQBE/U0lK/U0lABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAGXqX+vH0qnVzUgfPz7VToAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigB8H+uT61u1iW4PnL9a26ACiiigAooooAKKKKACiiigAooooAKKKKACpqhqagCJ+ppKV+ppKACiiigAooooAKKKKACiiigAooooAKKKKAK1zbiQE98YrOe3cHAVj+FbVFAGH5En9xvyo8iT+435VuUUAYfkSf3G/KjyJP7jflW5RQBh+RJ/cb8qPIk/uN+VblFAGH5En9xvyo8iT+435VuUUAYfkSf3G/KjyJP7jflW5RQBh+RJ/cb8qPIk/uN+VblFAGH5En9xvyo8iT+435VuUUAYfkSf3G/KjyJP7jflW5RQBh+RJ/cb8qPIk/uN+VblFAGH5En9xvyo8iT+435VuUUAYfkSf3G/KjyJP7jflW5RQBh+RJ/cb8qPIk/uN+VblFAGH5En9xvyo8iT+435VuUUAYfkSf3G/KlFvJ/cb8q26KAKNra45Ocg5q9RRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVNUNTUARP1NJSv1NJQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFTVDU1AET9TSUr9TSUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABU1Q1NQBE/U0lK/U0lABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVNUNTUARP1NJSv1NJQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFTVDU1AET9TSUr9TSUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABU1Q1NQBE/U0lK/U0lABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVNUNTUARP1NJU3p9BRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENFTUUAQ0VNRQBDRU1FAENTUU1vvH60Af/2Q=="
    WINDOW_TITLE = "设置路径"
    INSTALL_PATH_LABEL = "微信安装路径："
    DATA_PATH_LABEL = "数据存储路径："
    DLL_PATH_LABEL = "WeChatWin.dll路径："
    GET_BUTTON_TEXT = "获取"
    CHOOSE_PATH_BUTTON_TEXT = "选择路径"
    OK_BUTTON_TEXT = "确定"
    ERROR_DIALOG_TITLE = "错误"
    INVALID_INSTALL_PATH_ERROR = "请选择WeChat.exe文件"
    INVALID_DATA_PATH_ERROR = "该路径不是有效的存储路径，可以在微信设置中查看存储路径"
    INVALID_DLL_PATH_ERROR = "请选择wechatwin.dll文件"
    PATHS_VALIDATION_ERROR = "请确保所有路径都已正确设置"
    DEFAULT_AVATAR_URL = ("https://wx.qlogo.cn/mmhead/ver_1"
                          "/O9MB5YR9xFDtibDkS8TSaicgL12fVQgjlAGoWhaS4fOia3hUvgNZxicHas"
                          "TuvKk6o9zGGuOZ6Z0ibITkGrjKOmB3rzvhPwvDXZ7RksA8lpIeLybQ/132")
