#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:05:41 2018

@author: luo
"""
import subprocess
import os
import sys
from PIL import Image
class screenshot(object):
    def __init__(self):
        self.SCREENSHOT_WAY = 3
    def pull_screenshot(self):
        """
        获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
        可根据效率及适用性由高到低排序
        """
        
        if 1 <= self.SCREENSHOT_WAY <= 3:
            process = subprocess.Popen(
                'adb shell screencap -p',
                shell=True, stdout=subprocess.PIPE)
            binary_screenshot = process.stdout.read()
            if self.SCREENSHOT_WAY == 2:
                binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
            elif self.SCREENSHOT_WAY == 1:
                binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
            f = open('autojump.png', 'wb')
            f.write(binary_screenshot)
            f.close()
        elif self.SCREENSHOT_WAY == 0:
            os.system('adb shell screencap -p /sdcard/autojump.png')
            os.system('adb pull /sdcard/autojump.png')
    
    
    def check_screenshot(self):
        """
        检查获取截图的方式
        """
        if os.path.isfile('autojump.png'):
            try:
                os.remove('autojump.png')
            except Exception:
                pass
        if self.SCREENSHOT_WAY < 0:
            print('暂不支持当前设备')
            sys.exit()
        self.pull_screenshot()
        try:
            Image.open('./autojump.png').load()
            print('采用方式 {} 获取截图'.format(self.SCREENSHOT_WAY) )
        except Exception:
            self.SCREENSHOT_WAY -= 1

