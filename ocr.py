#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 12:29:59 2018

@author: luo
"""
from aip import AipOcr
import pytesseract
import re

def get_text_from_image(image_dat, api_version=0, timeout=3):
        
    options = {  
      'detect_direction': 'true',  
      'language_type': 'CHN_ENG',  
    }      
        
    APP_ID = '10673219'  
    API_KEY = 'p2jshxcHhyzDrqRBQrns9qy0'  
    SECRET_KEY = 'BO0LTCsCq1fB3zC1D9IdVZmBr9wfoRVe'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY) 
    client.setConnectionTimeoutInMillis(timeout * 1000)
    if api_version == 1:
        result = client.basicAccurate(image_dat, options)
    else:
        result = client.basicGeneral(image_dat, options)
    if "error_code" in result:
        print("baidu api error: ", result["error_msg"])
        return ""
    return [words["words"] for words in result["words_result"]]

def local_ocr(img):
    text=pytesseract.image_to_string(img,lang='chi_sim' )  
    text = text.replace(' ','')
    Q_pat = re.compile('\.(.*?)\n\n',re.DOTALL)
    A_pat = re.compile('\n\n(.*?)\n\n(.*?)\n\n(.*)',re.DOTALL)
    a = []
    try:
        q = Q_pat.search(text).group(1)
    except:
        q = text
    
    
    for i in range(3):
        try:
            a.append(A_pat.search(q).group(i+1).strip())
        except:
            pass
    text = (q,a)
    return text