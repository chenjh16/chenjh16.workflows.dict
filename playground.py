from workflow import web
import re

# https://dsuggest.ydstatic.com/suggest.s?query=%E4%BD%A0&keyfrom=dict2.index.suggest&o=form&rn=10&h=0&le=eng
url = 'https://dsuggest.ydstatic.com/suggest.s?query=%E4%BD%A0' 
url = 'https://dsuggest.ydstatic.com/suggest.s?query=brighn' 
res = web.get(url).text.encode()
slist = re.findall(r'%3E(\w+|(%u\w+)+)%3C', res)
# slist.pop()
slist = [suggest.decode('unicode_escape') for (suggest, nouse) in slist]
print slist

s = slist.pop()
s = s.replace('%', '\\')
print s.decode('unicode_escape')

s = '\u6253\u8d4f'
print s.decode('unicode_escape')

s = '%u6253%u8d4f'
print s
s = s.replace('%', '\\')
print s