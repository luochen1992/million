# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 16:55:04 2017

@author: Luo Jiacheng
"""
# -*- coding: utf-8 -*-
"""
手机屏幕截图的代码
"""
from io import BytesIO  
import requests
import multiprocessing
from word_utilities import parse_false,pre_process_question
from PIL import Image
from screenshot import screenshot
import cv2
import matplotlib.pyplot as plt
import numpy as np
from ocr import get_text_from_image,local_ocr
from bs4 import BeautifulSoup
from crawl import baidu_count, kwquery,jieba_initialize
import time
import jieba
from multiprocessing import Process
#import operator

from terminaltables import AsciiTable
import threading

class MyThread(threading.Thread):
    '''
    my thread could return results of thread
    '''
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


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
  
def lw(q):
    temp = np.sum(q,axis=1)
    max_pix = temp[0]
    for i in range(len(temp)):
        if temp[i]<max_pix:
            break
    q = q[i-10:,:].copy()
    for i in range(len(temp)):
        if temp[0-i]<max_pix:
            break
    q = q[:0-i+10,:].copy()
    
    temp = np.sum(q,axis=0)
    max_pix = temp[0]
    for i in range(len(temp)):
        if temp[i]<max_pix:
            break
    q = q[:,i-10:].copy()
    for i in range(len(temp)):
        if temp[0-i]<max_pix:
            break
    q = q[:,:0-i+20].copy()
    return q

def get_file_content(filePath):  
    with open(filePath, 'rb') as fp:  
        return fp.read()
    
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
#    print(text)
    return text

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

    return text

def parse_question_and_answer(text_list):
    question = ""
    start = 0
    for i, keyword in enumerate(text_list):
        question += keyword
        if "?" in keyword:
            start = i + 1
            break
    real_question = question.split(".")[-1]

    for char, repl in [("以下", ""), ("下列", "")]:
        # if real_question.startswith(char):
        real_question = real_question.replace(char, repl, 1)

    question, true_flag = parse_false(real_question)
    return true_flag, real_question, question, text_list[start:]


if __name__ == '__main__' :
#    multiprocessing.freeze_support() 
    #jieba_initialize()
    list_t = []
    

    s_shot = screenshot()
    s_shot.check_screenshot()
    results = []
    quizType = input('''please input quiz type:
        1:dabai
        2:xigua
        3:uc
        4:zhishichaoren
        5:wangyi
        6:chongdingdahui
        ''')
    quizType = int(quizType)
    while True:
#        time.sleep(0.5)  
        start = time.time()
        s_shot.pull_screenshot()
        img = cv2.imread('./autojump.png',0)    
#        img = Image.open('autojump.png').convert('L')
        hist_cv = np.bincount(img.ravel(),minlength=256)
        #hist_cv = cv2.calcHist([img],[0],None,[256],[0,256])
        #plt.plot(hist_cv)
        
    
        if sum(hist_cv[250:])>5e5:
            
            a = []
        #    cv2.waitKey(0)
        #    cv2.destroyAllWindows()
            print('''
            
            ready go!!!!
            '''
            )            
            
            if quizType ==1:
                q = img[360:1150,45:1035].copy()#dabai
            elif quizType ==2:
                q = img[285:1240,45:1035].copy()
            elif quizType == 3:
                q = img[330:1230,80:990].copy()#uc
            elif quizType ==4:
                q = img[290:1130,45:1035].copy()#zhishichaoren
            elif quizType ==5:
                q = img[400:1300,45:1035].copy()#wangyi
            else:
                q = img[280:1130,45:1035].copy()#chongdingdahui
            _,q = cv2.threshold(q,210,255,cv2.THRESH_BINARY) 
#            q = lw(q)
            q = Image.fromarray(q)  
            (x,y) = q.size
            q = q.resize((int(x*0.3),int(y*0.3)),Image.ANTIALIAS)
            
            fq = BytesIO()
            q.save(fq, format='PNG')
            b = get_text_from_image(fq.getvalue())
#            b = None
            #recognize
            if not b:
                print("text not recognize")
                
                q,a = local_ocr(q)
            else:
                true_flag, real_q, q, a = parse_question_and_answer(b)         
            if quizType in [1,3,5]:     
                for char, repl in [("A.", ""), ("B.", ""),("A:", ""), ("B:", ""),
                                   ("A:", ""), ("B:", ""),("C.", ""), ("C:", ""),
                                   ("A", ""),("B", ""), ("C", ""), ("c:", "")]:
                    for i,elem in enumerate(a):
                         elem = elem.replace(char, repl, 1)
                         a[i] = elem
            if quizType == 1:
                q = q[3:]
                
            tem = ' '.join(a)
            tem = tem.replace('\n','')
            red = url+q  
            zed = zhidaourl +q
            red111 = zhidaourl+q+" "+tem
            print(time.time()-start)
            t1 = MyThread(searchzhidao,args=(red111,a,))
            t2 = MyThread(search,args=(red,))
            t3 = MyThread(searchzhidao,args=(zed,a,))
            list_t = [t1,t2,t3]
            
            text = []
            
            for t in list_t:
                t.start()
            for t in list_t:
                t.join()
                print(t.get_result())
                text.append(t.get_result())
            text = '\n'.join(text)
            ##highlight keywords
            for elem in a:
                text = text.split(elem)
                _split_ = '\033[1;31;47m '+elem+'\033[0m ' 
                text = _split_.join(text)
            print(text)
            ##count answers
            for elem in a:
                print(elem+' : {}'.format(text.count(elem)))
#           
#            ans = kwquery(real_q)
#            print("~~~~~~~")
#            for a in ans:
#                print(a)
#            print("~~~~~~~")
            
#            summary = baidu_count(q, a, timeout=5)
#            summary_li = sorted(
#                summary.items(), key=operator.itemgetter(1), reverse=True)
#            data = [("选项", "同比")]
#            for a, w in summary_li:
#                data.append((a, w))
#            table = AsciiTable(data)
#            print(table.table)
    
#            print("*" * 72)
#            if true_flag:
#                print("肯定回答(**)： ", summary_li[0][0])
#                print("否定回答(  )： ", summary_li[-1][0])
#            else:
#                print("肯定回答(  )： ", summary_li[0][0])
#                print("否定回答(**)： ", summary_li[-1][0])
#            print("*" * 72)
    
            #        text = searchzhidao(zed)
    
    #            print(elem.text)
    #        line_seg = seg_sentence(text)
    #        print(text)
#            Image.fromarray(img).save(str(count)+'1q.jpg')
    #        cv2.imwrite(str(count),img)
    #        print(line_seg)
            enter = input("按Enter键开始，按ESC键退出...")
            if enter == chr(48):
                break
