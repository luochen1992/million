# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 16:55:04 2017

@author: Luo Jiacheng
"""
# -*- coding: utf-8 -*-
"""
手机屏幕截图的代码
"""
import requests
import subprocess
import os
import sys
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from bs4 import BeautifulSoup
import re
import time
import jieba
from multiprocessing import Process
#from aip import AipOcr  
import json  
dr = re.compile(r'<[^>]+>',re.S)
Q_pat = re.compile('\.(.*?)\n\n',re.DOTALL)
A_pat = re.compile('\n\n(.*?)\n\n(.*?)\n\n(.*)',re.DOTALL)
#A2_pat =  re.compile('\n\n(.*?)\n\n',re.DOTALL)
#A3_pat = re.compile('\n\n(.*?)\n\n',re.DOTALL)

# SCREENSHOT_WAY 是截图方法，经过 check_screenshot 后，会自动递减，不需手动修改
SCREENSHOT_WAY = 3

url = 'http://www.baidu.com/s?wd='
zhidaourl = 'https://zhidao.baidu.com/search?word='


headers = {
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
}
def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]  
    return stopwords  
def seg_sentence(sentence):  
    sentence_seged = jieba.cut(sentence.strip())  
    stopwords = stopwordslist('stop.txt')  
    outstr = ''  
    for word in sentence_seged:  
        if word not in stopwords:  
            if word != '\t':  
                outstr += word  
                outstr += " "  
    return outstr  

def pull_screenshot():
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREENSHOT_WAY
    if 1 <= SCREENSHOT_WAY <= 3:
        process = subprocess.Popen(
            'adb shell screencap -p',
            shell=True, stdout=subprocess.PIPE)
        binary_screenshot = process.stdout.read()
        if SCREENSHOT_WAY == 2:
            binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
        elif SCREENSHOT_WAY == 1:
            binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
        f = open('autojump.png', 'wb')
        f.write(binary_screenshot)
        f.close()
    elif SCREENSHOT_WAY == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png')


def check_screenshot():
    """
    检查获取截图的方式
    """
    global SCREENSHOT_WAY
    if os.path.isfile('autojump.png'):
        try:
            os.remove('autojump.png')
        except Exception:
            pass
    if SCREENSHOT_WAY < 0:
        print('暂不支持当前设备')
        sys.exit()
    pull_screenshot()
    try:
        Image.open('./autojump.png').load()
        print('采用方式 {} 获取截图'.format(SCREENSHOT_WAY) )
    except Exception:
        SCREENSHOT_WAY -= 1
        
def lw(q):
    temp = np.sum(q,axis=1)
    for i in range(len(temp)):
        if temp[i]<252450:
            break
    q = q[i+3:,:].copy()
    for i in range(len(temp)):
        if temp[0-i]<252450:
            break
    q = q[:0-i+3,:].copy()
    
    temp = np.sum(q,axis=0)
    max_pix = temp[0]
    for i in range(len(temp)):
        if temp[i]<max_pix:
            break
    q = q[:,i+3:].copy()
    for i in range(len(temp)):
        if temp[0-i]<max_pix:
            break
    q = q[:,:0-i+3].copy()
    return q

def get_file_content(filePath):  
    with open(filePath, 'rb') as fp:  
        return fp.read()
def baidu():
        
    options = {  
      'detect_direction': 'true',  
      'language_type': 'CHN_ENG',  
    }      
        
    APP_ID = '10673219'  
    API_KEY = 'p2jshxcHhyzDrqRBQrns9qy0'  
    SECRET_KEY = 'BO0LTCsCq1fB3zC1D9IdVZmBr9wfoRVe'
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)  
    result = aipOcr.basicGeneral(get_file_content('./autojump.png'), options)  
    print(json.dumps(result).decode("unicode-escape"))

def search(url):
    text = []
    r = requests.get(url,headers=headers)
    soup = r.text.encode(r.encoding) 
    soup = BeautifulSoup(soup,'html.parser')
#    BBB = soup.find_all('div',attrs={'class':'c-abstract'})
    BBB = soup.find_all('div',attrs={'class':'c-border'})
    for elem in BBB:
       text+=elem.text
    text = ''.join(text)
    if BBB != []:
        text = text.replace('  ','')
        text = text.replace('\t','')
        text = text.replace('\n',' ')
        text = text.replace('  ',' ')
        text = text.replace(' ','\n')
        
        
        print('\n'+text)
#    return text

def searchzhidao(url,a):
    
    text = []
    r = requests.get(url,headers=headers)
    soup = r.text.encode(r.encoding) 
    soup = BeautifulSoup(soup,'html.parser')
    BBB = soup.find_all('dd',attrs={'class':'dd answer'})
    for elem in BBB:
        if u"不知道" in elem.text:
            continue
        
        text+=elem.text+'\n\n'
        
    text = ''.join(text)
    print(text)
    for elem in a:
        print(elem+' : {}'.format(text.count(elem)))

#def readpic(q):
#    pytesseract.image_to_string(q,lang='chi_sim')  
    
check_screenshot()
count = 0
while True:
    time.sleep(0.3)    
    pull_screenshot()
    img = cv2.imread('./autojump.png',0)
    #img = Image.open('./autojump.png').convert('L')
    hist_cv = np.bincount(img.ravel(),minlength=256)
    #hist_cv = cv2.calcHist([img],[0],None,[256],[0,256])
    #plt.plot(hist_cv)
    if sum(hist_cv[251:])>6e5:
        a = []
    #    cv2.waitKey(0)
    #    cv2.destroyAllWindows()
        print('''
           
        ready go!!!!
        '''
        )
#        q = img[250:1210,45:1035].copy()
        q = img[280:570,45:1035].copy()#zhishichaoren
#        q = img[250:650,45:1035].copy()#baiwanyingxiong
#        q = img[270:550,45:1035].copy()#chongdinqgdahui
#        _,q = cv2.threshold(q,210,255,cv2.THRESH_BINARY) 
#        q = lw(q)
#        hist_q = np.bincount(q.ravel(),minlength=256)
        
        q = Image.fromarray(q)  
        (x,y) = q.size
        q = q.resize((int(x*0.5),int(y*0.5)), Image.ANTIALIAS)

#        start = time.time()
        q=pytesseract.image_to_string(q,lang='chi_sim')  
#        end = time.time()
#        print(end-start)
        q = q.replace('\n','')
        q = q.replace(' ','')  
        
 

        red = url+q
        zed = zhidaourl +q

        p1 = Process(target=search, args=(red,))
        p2 = Process(target=searchzhidao, args=(zed,a))
        p2.start()
        p2.join()
        p1.start()
        p1.join()
        
#        text = searchzhidao(zed)

#            print(elem.text)
#        line_seg = seg_sentence(text)
#        print(text)
        Image.fromarray(img).save(str(count)+'q.jpg')
        count+=1
#        cv2.imwrite(str(count),img)
#        print(line_seg)
        
        time.sleep(8.5) 
        
#        print(text.count(a1))
#        print(text.count(a2))   
#        print(text.count(a3))   
#        dd = dr.sub('',soup.text)
#        print(dd)
