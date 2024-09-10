from flask import Flask, request, render_template  # 导入Flask框架
import random  # 导入random模
import re  # 导入re模块

# 创建服务端
app = Flask(__name__)

length = 16  # 混淆标识符的长度

# 定义查找字符串的函数
def find_str(text):
    res = []  # 用于存储提取的字符串和代码块
    # 定义正则表达式，匹配Lua中的字符串（方括号、双引号、单引号）
    p1 = r'\[\[(.*?)\]\]'  # 匹配方括号包围的字符串
    p2 = r'"(.*?[^\\])"'  # 匹配双引号包围的字符串
    p3 = r"'(.*?[^\\])'"  # 匹配单引号包围的字符串

    while True:  # 进入无限循环，直到手动退出
        m1 = re.search(p1, text)  # 在文本中搜索方括号字符串
        m2 = re.search(p2, text)  # 在文本中搜索双引号字符串
        m3 = re.search(p3, text)  # 在文本中搜索单引号字符串
        
        # 如果三者均未找到，则返回找到的结果和代码文本
        if not (m1 or m2 or m3):
            return res + [['code', text]]  # 返回已找到的字符串和剩余的代码文本
            
        # 找到匹配，并标记第几个匹配
        ms = [(i + 1, m) for i, m in enumerate([m1, m2, m3]) if m]  # 创建含序号的匹配列表
        m = min(ms, key=lambda x: x[1].start())  # 找到最先出现的匹配字符串
        num, m = m  # 获取匹配的编号和匹配对象
        quotes = {1: ['[[', ']]'], 2: ['"', '"'], 3: ["'", "'"]}[num]  # 根据匹配编号获取引号类型
        
        # 如果匹配之前有代码片段，则添加到结果中
        if m:
            if text[:m.start()]:  # 检查匹配前是否有代码
                res.append(['code', text[:m.start()]])  # 添加代码片段到结果
            
            # 添加匹配到的字符串到结果
            res.append(['str', quotes[0] + m.group(1) + quotes[1]])  # 存储提取的字符串
            text = text[m.end():]  # 更新剩余文本，去掉已处理部分

#Lua代码混淆
def obfuscate_lua_code(lua_code):
    ascii_letters = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(48, 58)]  # 创建字母和数字列表
    
    # 内部函数，用于生成随机混淆标识符
    def random_string():
        return '_0x' + ''.join(random.choice(ascii_letters) for _ in range(length))  # 生成随机字符串

    obfuscated_identifiers = {}  # 用于存储原标识符和混淆标识符的映射

    # 定义混淆标识符的具体实现
    def obfuscate_identifier(match):
        original_name = match.group(0)  # 获取匹配到的原始标识符
        start = match.start()  # 记录原标识符的开始位置
        end = match.end()  # 记录原标识符的结束位置
        
        # 检查混淆的条件
        if lua_code[start - 1:start] in ['.', ':']:  # 检查原标识符前是否有"."或":"
            return original_name  # 如果是，返回原标识符
        if lua_code[end:end + 1] in ['.', ':']:  # 检查标识符后是否有"."或":"
            return original_name  # 如果是，返回原标识符
        if original_name in lua_reserved_keywords:  # 检查是否为Lua保留关键字
            return original_name  # 如果是，返回原标识符
        if original_name in lua_standard_library:  # 检查是否为Lua标准库函数
            return original_name  # 如果是，返回原标识符
        if original_name in logi_standard_library:  # 检查是否为自定义标准库函数
            return original_name  # 如果是，返回原标识符
        if 'STRING_PROTECTED_' in original_name:  # 检查是否已被特殊标识符保护
            return original_name  # 如果是，返回原标识符
        if original_name in obfuscated_identifiers:  # 检查是否已有混淆版本
            return obfuscated_identifiers[original_name]  # 如果已混淆，返回混淆版本
        else:
            obfuscated_name = random_string()  # 否则，生成新的混淆标识符
            obfuscated_identifiers[original_name] = obfuscated_name  # 添加到映射字典
            return obfuscated_name  # 返回新的混淆标识符

    # Lua保留关键字和标准库
    lua_reserved_keywords = [
        "and", "break", "do", "else", "elseif", "end", "false", "for",
        "function", "if", "in", "local", "nil", "not", "or", "repeat",
        "return", "then", "true", "until", "while", "goto"
    ]

    lua_standard_library = [
        "basic", "_G", "_VERSION", "assert", "collectgarbage", "dofile",
        "error", "getmetatable", "ipairs", "load", "loadfile", "next",
        "pairs", "pcall", "print", "rawequal", "rawget", "rawlen", "rawset",
        "require", "select", "setmetatable", "tonumber", "tostring", "type",
        "warn", "xpcall"
    ]

    logi_standard_library = [
        "OnEvent", "GetMKeyState", "SetMKeyState", "Sleep", "OutputLogMessage",
        "GetRunningTime", "GetDate", "ClearLog", "PressKey", "ReleaseKey",
        "PressAndReleaseKey", "IsModifierPressed", "PressMouseButton",
        "ReleaseMouseButton", "PressAndReleaseMouseButton", "IsMouseButtonPressed",
        "MoveMouseTo", "MoveMouseWheel", "MoveMouseRelative", "MoveMouseToVirtual",
        "GetMousePosition", "OutputLCDMessage", "ClearLCD", "PlayMacro", "PressMacro",
        "ReleaseMacro", "AbortMacro", "IsKeyLockOn", "SetBacklightColor",
        "OutputDebugMessage", "SetMouseDPITable", "SetMouseDPITableIndex",
        "EnablePrimaryMouseButtonEvents", "SetSteeringWheelProperty",
        "SetMouseSpeed", "GetMouseSpeed", "IncrementMouseSpeed", "DecrementMouseSpeed"
    ]

    identifier_pattern = r'(?<![a-zA-Z_])' + r'[a-zA-Z_]\w*'  # 定义标识符的正则表达式
    obfuscated_code = re.sub(identifier_pattern, obfuscate_identifier, lua_code)  # 替换为混淆标识符

    return obfuscated_code  # 返回混淆后的代码

# 代码混淆的主函数
def obfuscate_code(lua_code):
    lst = find_str(lua_code)  # 使用find_str函数提取字符串
    str_list = [i[1] for i in lst if i[0] == 'str']  # 获取所有提取的字符串
    lst_copy = lst.copy()  # 复制提取结果
    i = 1  # 初始化字符串计数器
    for j in range(len(lst_copy)):
        if lst_copy[j][0] == 'str':  # 检查元素是否是字符串
            lst_copy[j][1] = 'STRING_PROTECTED_' + str(i)  # 更改字符串为保护形式
            i += 1  # 计数器递增

    lst_copy = ''.join([i[1] for i in lst_copy])  # 合并所有已处理结果
    lst_copy = re.sub(r'--.*', '', lst_copy)  # 移除注释
    lst_copy = re.sub(r'\n\s*\n', '\n', lst_copy)  # 移除多余空行
    lst_copy = re.sub(r'\s+', ' ', lst_copy)  # 合并多个空格为一个
    lst_copy = re.sub(r'\n', '', lst_copy)  # 移除换行符，格式化代码

    lst_copy = obfuscate_lua_code(lst_copy)  # 对代码进行混淆处理

    # 恢复字符串的原始形式
    for i in range(len(str_list) - 1, -1, -1):  # 逆序替换，以防干扰
        lst_copy = lst_copy.replace('STRING_PROTECTED_' + str(i + 1), str_list[i])  # 替换回原字符串
    return lst_copy  # 返回最终的混淆代码

# 处理网页请求
@app.route('/', methods=['GET', 'POST'])  # 允许GET和POST请求
def index():
    obfuscated_code = ''  # 初始化混淆后的代码为空字符串
    if request.method == 'POST':  # 如果是POST请求
        lua_code = request.form.get('LuaPaste')  # 获取表单中的Lua代码
        obfuscated_code = obfuscate_code(lua_code)  # 调用混淆函数处理代码

    return render_template('index.html', obfuscated_code=obfuscated_code)  # 渲染模板文件，返回混淆后的代码

# 启动服务端
if __name__ == '__main__':
    app.run(debug=True)  # 以调试模式运行Flask应用