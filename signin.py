import requests
import re
import os
import ba
import bs
import urllib.parse as urlparse
from urllib.parse import parse_qs
import random
import pas
from bs4 import BeautifulSoup
import pytools
import pickle

#os.environ['REQUESTS_CA_BUNDLE'] = '/sdcard/HttpCanary/certs/HttpCanary.pem'
username=os.getenv('username')
password=os.getenv('password')
if os.getenv('captcha')=='true':
  password='wrong'
frppw=os.getenv('pw')
host=os.getenv('host')
html="""\
<p><a href="http://raspberrypi.lan/Meow-Chat/">本地网络</a></p>
<p><a href="%s/Meow-Chat/">远程网络</a></p>\
"""%host

s = requests.Session()
try:
  with open('cookies.txt','rb') as f:
    s.cookies.update(pickle.load(f))
except FileNotFoundError:
  print('FileNotFoundError')
s.headers.update({'user-agent': 'Mozilla/5.0 (Linux; Android 10; ONEPLUS A3010 Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36'})
s.get('https://klpbbs.com/')
def login(code,auth,hash,update,rcapurl):
  with s.get('https://klpbbs.com/member.php?mod=logging&action=login&mobile=2') as web:
    text=web.text
    #print(text)
    if '现在将转入登录前页面' in text:
      return
    loginhash=re.search('(?<=loginhash=)([^\"]*)',text).group()
    formhash=re.search('(?<=<input type=\"hidden\" name=\"formhash\" id=\"formhash\" value=\')([^\']*)',text).group()
  with s.post('https://klpbbs.com/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=%s&handlekey=loginform&inajax=1'%(loginhash),data={'formhash':formhash,'fastloginfield':'username','cookietime':'31104000','username':username,'password':password,'questionid':0,'auth':auth,'seccodehash':hash,'seccodeverify':code}) as web:
    text=web.text
    soup=BeautifulSoup(text,features='lxml')
    rep=soup.dt.p.text
    print(rep)
    if '请输入验证码后继续登录' in text:
      #print(text)
      capurl=re.search("(?<=succeedhandle_loginform\(')([^\']*)",text).group()
      capurl='https://klpbbs.com/'+capurl
      #print(capurl)
      with s.get(capurl) as web:
        text=web.text
        cap=re.search('(?<=<img src=")(misc.php\?mod=seccode[^\"]*)',text).group()
        cap=cap.replace('amp;','')
        cap='https://klpbbs.com/'+cap
        with s.get(cap,headers={'referer':capurl}) as pic:
          content=pic.content
          #print(content)
          pas.pas(host,frppw)
          ba.send(content)
          pytools.jmail('苦力怕签到','需要验证码',html,html=True)
          rcode=bs.receive('请输入验证码')
          parsed=urlparse.urlparse(capurl)
          rauth=parse_qs(parsed.query)['auth'][0]
          #rauth=rauth.replace('+','/')
          parsed=urlparse.urlparse(cap)
          rhash=parse_qs(parsed.query)['idhash'][0]
          update=parse_qs(parsed.query)['update'][0]
          login(rcode,rauth,rhash,update,capurl)
    elif '验证码填写错误' in text:
      idhash='S'+str(random.randint(100, 999))
      with s.get('https://klpbbs.com/misc.php?mod=seccode&update=%s&idhash=%s&mobile=2'%(update,idhash),headers={'referer':rcapurl}) as pic:
        content=pic.content
        ba.send(content)
        rcode=bs.receive('请输入验证码')
        login(rcode,auth,idhash,update,rcapurl)
login('','','',0,'')
with s.get('https://klpbbs.com/') as web:
  text=web.text
  formhash=re.search('(?<=formhash=)([^\&]*)',text).group()
a=s.get('https://klpbbs.com/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash=%s'%(formhash)).text
print(a)

with open('cookies.txt','wb') as f:
  pickle.dump(s.cookies, f)
