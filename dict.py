# -*- coding: utf-8 -*-
from workflow import Workflow3, ICON_WEB, web
from workflow.notify import notify
from workflow.background import run_in_background, is_running
from concurrent import futures
import json
import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')


# http://dict.youdao.com/dictvoice?audio=hello
# http://dict.youdao.com/speech?audio=dog

YOUDAO_DEFAULT_KEYFROM = ('whyliam-wf-1', 'whyliam-wf-2', 'whyliam-wf-3',
                          'whyliam-wf-4', 'whyliam-wf-5', 'whyliam-wf-6',
                          'whyliam-wf-7', 'whyliam-wf-8', 'whyliam-wf-9',
                          'whyliam-wf-10', 'whyliam-wf-11')

YOUDAO_DEFAULT_KEY = (2002493135, 2002493136, 2002493137,
                      2002493138, 2002493139, 2002493140,
                      2002493141, 2002493142, 2002493143,
                      1947745089, 1947745090)

CMD = ('history', 'cleancache', 'cleanhistory')

ERRORCODE_DICT = {
    "101": "缺少必填的参数，出现这个情况还可能是et的值和实际加密方式不对应",
    "102": "不支持的语言类型",
    "103": "翻译文本过长",
    "104": "不支持的API类型",
    "105": "不支持的签名类型",
    "106": "不支持的响应类型",
    "107": "不支持的传输加密类型",
    "108": "appKey无效，注意不是应用密钥",
    "109": "batchLog格式不正确",
    "110": "无相关服务的有效实例",
    "111": "开发者账号无效",
    "113": "q不能为空",
    "201": "解密失败，可能为DES,BASE64,URLDecode的错误",
    "202": "签名检验失败",
    "203": "访问IP地址不在可访问IP列表",
    "205": "请求的接口与应用的平台类型不一致",
    "301": "辞典查询失败",
    "302": "翻译查询失败",
    "303": "服务端的其它异常",
    "401": "账户已经欠费",
    "411": "访问频率受限,请稍后访问",
    "412": "长请求过于频繁，请稍后访问",
    "500": "有道翻译失败"
}

ICON_DEFAULT = 'icons/icon.png'
ICON_PHONETIC = 'icons/icon_phonetic.png'
ICON_BASIC = 'icons/icon_basic.png'
ICON_WEB = 'icons/icon_web.png'
ICON_UPDATE = 'icons/icon_update.png'
ICON_ERROR = 'icons/icon_error.png'

QUERY_END = '/'
USE_CACHE = os.getenv('use_cache', '0').strip() == '1'
SHOW_EXPLAINS = os.getenv('show_simple_explains', '0') == '1'

wf = Workflow3(update_settings={
    'github_slug': 'chenjh16/chenjh16.workflows.youdao',
    'frequency': 7
})


def to_uni(str):
    if isinstance(str, unicode):
        return str
    return str.replace('%u', '\\u').decode('unicode_escape')


def is_english(query):
    if re.search(ur"[\u4e00-\u9fa5]+", query):
        return False
    return True


def store(file, data):
    with open(file, 'w') as fw:
        json.dump(data, fw, ensure_ascii=False)


def load(file):
    with open(file,'r') as f:
        data = json.load(f)
        return data

def get_translate_url(query):
    zhiyun_id = os.getenv('zhiyun_id', '').strip()
    zhiyun_key = os.getenv('zhiyun_key', '').strip()
    if zhiyun_id and zhiyun_key:
        # wf.logger.debug('using zhiyun id && key!')
        url = get_zhiyun_url(query, zhiyun_id, zhiyun_key)
    else:
        youdao_keyfrom = os.getenv('youdao_keyfrom', '').strip()
        youdao_key = os.getenv('youdao_key', '').strip()
        if not youdao_keyfrom or not youdao_key:
            import random
            i = random.randrange(0, 11, 1)
            youdao_keyfrom = YOUDAO_DEFAULT_KEYFROM[i]
            youdao_key = YOUDAO_DEFAULT_KEY[i]
        url = get_youdao_url(query, youdao_keyfrom, youdao_key)
    return url


def get_youdao_url(query, youdao_keyfrom, youdao_key):
    import urllib
    query = urllib.quote(str(query))
    url = 'http://fanyi.youdao.com/openapi.do?' + \
        'keyfrom=' + str(youdao_keyfrom) + \
        '&key=' + str(youdao_key) + \
        '&type=data&doctype=json&version=1.1&q=' + query
    return url


def get_zhiyun_url(query, zhiyun_id, zhiyun_key):
    import urllib
    import hashlib
    import uuid
    salt = uuid.uuid4().hex
    sign = hashlib.md5(zhiyun_id + query + salt + zhiyun_key).hexdigest()
    query = urllib.quote(str(query))
    url = 'https://openapi.youdao.com/api' + \
        '?appKey=' + str(zhiyun_id) + \
        '&salt=' + str(salt) + \
        '&sign=' + str(sign) + \
        '&q=' + query
    return url


def get_web_data(query):
    url = get_translate_url(query)
    try:
        rt = web.get(url).json()
        return rt
    except:
        rt = {}
        rt['errorCode'] = "500"
        return rt


def get_with_cache(query, callfunc, key=None, use_chche=True):
    def wrapper():
        return callfunc(query)
    cquery = query.replace(' ', 'c') # any alphabet
    cquery = cquery.replace('-', 'd') # any alphabet
    cquery = cquery.replace('_', 'e') # any alphabet
    if cquery.isalnum():
        key = key.replace(' ', '}') # maybe better choice
        return wf.cached_data(key, wrapper, max_age=7776000) if use_chche else wrapper()
    else:
        return wrapper()


def add_translation(query, is_eng, rt):
    subtitle = '[Translate Result]'
    translations = rt["translation"]
    for title in translations:
        arg = [query, title, query, '', ''] if is_eng else \
            [query, title, title, '', '']
        arg = '$%'.join(arg)
        wf.add_item(title=title, subtitle=subtitle, arg=arg, \
            valid=True, icon=ICON_DEFAULT)


def add_phonetic(query, is_eng, rt):
    if u'basic' in rt.keys():
        if rt["basic"].get("phonetic"):
            title = ""
            if rt["basic"].get("us-phonetic"):
                title += ("[US: " + rt["basic"]["us-phonetic"] + "] ")
            if rt["basic"].get("uk-phonetic"):
                title += ("[UK: " + rt["basic"]["uk-phonetic"] + "] ")
            title = title if title else "[" + rt["basic"]["phonetic"] + "]"
            subtitle = '[Soundmark]'
            arg = [query, title, query, '', ''] if is_eng else \
                [query, title, '', query, '']
            arg = '$%'.join(arg)
            wf.add_item(title=title, subtitle=subtitle, arg=arg, \
                valid=True, icon=ICON_PHONETIC)


def add_explains(query, is_eng, rt):
    if u'basic' in rt.keys():
        for i in range(len(rt["basic"]["explains"])):
            title = rt["basic"]["explains"][i]
            subtitle = '[Simple Explains]'
            arg = [query, title, query, '', ''] if is_eng else \
                [query, title, '', title, '']
            arg = '$%'.join(arg)
            wf.add_item(title=title, subtitle=subtitle, arg=arg, \
                valid=True, icon=ICON_BASIC)


def add_web_translation(query, is_eng, rt):
    if u'web' in rt.keys():
        for i in range(len(rt["web"])):
            titles = rt["web"][i]["value"]
            for title in titles:
                subtitle = '[Online: ' + rt["web"][i]["key"] + ']'
                if is_eng:
                    key = ''.join(rt["web"][i]["key"])
                    arg = [query, title, key, '', '']
                else:
                    # value = ' '.join(rt["web"][i]["value"])
                    arg = [query, title, title, '', '']
                arg = '$%'.join(arg)
                wf.add_item(title=title, subtitle=subtitle, \
                    arg=arg, valid=True, icon=ICON_WEB)


def add_suggest_item(item):
    (suggest, explain) = item
    suggest = to_uni(suggest)
    arg = [suggest, explain, suggest, '', ''] if is_english(suggest) else \
        [suggest, explain, '', explain, '']
    arg = '$%'.join(arg)
    item = wf.add_item(title=suggest, subtitle=explain, \
        autocomplete=suggest + QUERY_END, arg=arg)
    item.add_modifier('alt', 'Press `return` to pronouncation (US).')
    item.add_modifier('cmd', 'Press `return` to pronouncation (UK).')
    item.add_modifier('ctrl', 'Press `return` to open web page.')


def add_history_item(item):
    (suggest, times, explain) = item
    suggest = to_uni(suggest)
    arg = [suggest, explain, suggest, '', ''] if is_english(suggest) else \
    [suggest, explain, '', explain, '']
    arg = '$%'.join(arg)
    item = wf.add_item(title=times + ' - ' + suggest, subtitle=explain, \
        autocomplete=suggest + QUERY_END, arg=arg)
    item.add_modifier('alt', 'Press `return` to pronouncation.')
    item.add_modifier('ctrl', 'Press `return` to open web page.')


def get_suggests(query):
    url = 'https://dsuggest.ydstatic.com/suggest.s?query=' + query
    res = web.get(url).text.encode()
    res = re.findall(r'%3E(\w+|(%u\w+)+)%3C', res)
    if len(res):
        res.pop() # pop the line of `关闭提示`
    res = [item for (item, _) in res]
    return res


def add_explained_item(suggest, suggests_with_explains):
    simple_explains = ''
    rt = get_with_cache(to_uni(suggest), get_web_data, to_uni(suggest), USE_CACHE)
    errorCode = str(rt.get("errorCode"))
    if errorCode == "0":
        if u'basic' in rt.keys():
            for explain in rt["basic"]["explains"]:
                simple_explains += explain + '; '
    suggests_with_explains.append((suggest, simple_explains))    


def get_explained_suggests(suggests):
    suggests_with_explains = []
    if SHOW_EXPLAINS:
        def get_item_wrapper(suggest):
            return add_explained_item(suggest, suggests_with_explains)
        executor = futures.ThreadPoolExecutor(max_workers=4)
        tasks = [executor.submit(get_item_wrapper, suggest) for suggest in suggests]
        futures.wait(tasks)
    else:
        suggests_with_explains = [(suggest, '') for suggest in suggests]
    return suggests_with_explains


HISTORY_JSON='history.log'
TEMP_JSON='temp_history.log'


def show_history_list():
    if os.path.isfile(HISTORY_JSON):
        datum = load(HISTORY_JSON)
        # wf.logger.debug('items: ' + str(datum.items()))
        explained_datum = get_explained_suggests([a for (a, _) in datum.items()])
        items = [(a, str(datum[a]), b) for (a, b) in explained_datum]
        sorted_items = sorted(items, lambda x, y: cmp(x[1], y[1]), reverse=True)
        # wf.logger.debug('history: ' + str(sorted_items))
        map(add_history_item, sorted_items)
    else:
        item = wf.add_item('No history!')
        item.add_modifier('alt', '')
        item.add_modifier('ctrl', '')


def save_to_history_list(query):
    data = {'query':query}
    store(TEMP_JSON, data)
    run_in_background('save_history', ['/usr/bin/python', \
        wf.workflowfile('savehistory.py')])


def main(wf):
    wf.logger.debug("main begin!")
    if wf.update_available:
        wf.add_item(title='New version available',
                subtitle='Action this item to install the update',
                autocomplete='workflow:update', icon=ICON_UPDATE)
    query = wf.args[0]
    if query.startswith('>'): # commands
        icmd = query.replace('>', '')
        if icmd.endswith('<'):
            icmd = icmd.replace('<', '')
            if icmd == 'history':
                show_history_list()
        else:
            for cmd in CMD:
                if cmd.startswith(icmd):
                    if cmd == 'history':
                        item = wf.add_item(title=cmd, subtitle='Show history with frequency.', \
                            autocomplete='>history<')
                    elif cmd == 'cleancache':
                        arg = ['', '', '', '', cmd]
                        arg = '$%'.join(arg)
                        item = wf.add_item(title=cmd, subtitle='Clean the offline cache.', \
                            arg=arg, valid=True)
                    elif cmd == 'cleanhistory':
                        arg = ['', '', '', '', cmd]
                        arg = '$%'.join(arg)
                        item = wf.add_item(title=cmd, subtitle='Clean the history list.', \
                            arg=arg, valid=True)
                    item.add_modifier('alt', '')
                    item.add_modifier('ctrl', '')
    elif query.endswith(QUERY_END): # translate
        query = query.strip().replace("\\", "").replace('/', '')
        if not isinstance(query, unicode):
            query = query.decode('utf8')
        
        rt = get_with_cache(query, get_web_data, query, USE_CACHE)
        errorCode = str(rt.get("errorCode"))

        if ERRORCODE_DICT.has_key(errorCode):
            arg = ['', '', '', '', 'error']
            arg = '$%'.join(arg)
            wf.add_item(
                title=errorCode+" "+ERRORCODE_DICT[errorCode],
                subtitle='', arg=arg,
                valid=True, icon=ICON_ERROR)
        elif errorCode == "0":
            is_eng = is_english(query)
            add_translation(query, is_eng, rt)
            add_phonetic(query, is_eng, rt)
            add_explains(query, is_eng, rt)
            add_web_translation(query, is_eng, rt)
            save_to_history_list(query)
        else:
            title = 'No result!'
            subtitle = 'Please try other web dict...'
            arg = [query, ' ', ' ', ' ']
            arg = '$%'.join(arg)
            wf.add_item(
                title=title, subtitle=subtitle, arg=arg, \
                valid=True, icon=ICON_DEFAULT)
    else: # autocomplete
        query = query.strip()
        suggests = get_with_cache(query, get_suggests, query + '}', USE_CACHE)
        if not len(suggests):
            suggests.append(query)
        explained_suggests = get_explained_suggests(suggests)
        sorted_suggests = sorted(explained_suggests, \
            lambda x, y: cmp(x[0], y[0]))
        map(add_suggest_item, sorted_suggests)
    wf.send_feedback()


if __name__ == '__main__':
    sys.exit(wf.run(main))