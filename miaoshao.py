# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 10:51:06 2018

@author: junhua
"""
from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
from pymongo import MongoClient

class MongoDb:
    def __init__(self):
        self.conn=MongoClient('localhost',27017)
        self.db=self.conn.jd
        self.mstable=self.db.miaosha
    
    def insert(self,ms):
        ms['ct']=time.time()
        self.mstable.insert_one(ms)
class MiaoshaNow:
    def __init__(self,browser):
        self.browser=browser
        #self.db=MongoDb()
    
    def spider(self):
        ms={}
        self.scrollToEnd()
        ms['timeline']=self.getMiaoshaTimeline()
        #ms['curitems']=self.getMiaoshaList()
        timelines=self.browser.find_element_by_class_name('timeline_list')
        lis=timelines.find_elements_by_tag_name('li')
        mswill=[]
        try:
            #del lis[0]
            first=True
            #得到每个时间段的数据
            for li in lis:
                title=li.find_element_by_class_name('timeline_item_link_skew_time').text
                if first:
                    first=False
                else:
                    self.switchToTime(li)
                    print(title)
                    WebDriverWait(self.browser,30).until(EC.presence_of_element_located((By.CLASS_NAME,"seckill_mod_goods")))
                self.scrollToEnd()
                mswill.append({'title':title,'items':self.getMiaoshaList()})
        except:
            print('error')
        finally:
            ms['data']=mswill
        #self.db.insert(ms)
        return ms
    #得到当前秒杀所有时间端
    def getMiaoshaTimeline(self):
        timelines=self.browser.find_element_by_class_name('timeline_list')
        lis=timelines.find_elements_by_tag_name('li')
        timelines=[]
        for li in lis:
            texttime=li.find_element_by_class_name('timeline_item_link_skew_time')
            timeitem={}
            timeitem['time']=texttime.text
            link=li.find_element_by_class_name('timeline_item_link')
            timeitem['inprogress']=link.get_attribute('data-inprogress')
            timelines.append(timeitem)
        return timelines
    '''
    关闭到期的窗口
    '''
    def closeDialog(self):
        try:
            tolook=self.browser.find_element_by_class_name('skdialog_a')
            actions=ActionChains(self.browser)
            actions.move_to_element(tolook)
            actions.click(tolook)
            actions.perform()
        except NoSuchElementException:
            #没有对话框
            return None
        
    def switchToTime(self,timeitem):
        actions=ActionChains(self.browser)
        actions.move_to_element(timeitem)
        actions.click(timeitem)
        actions.perform()
    '''
    滚动窗口到底部，因为数据是分屏下载的，只有慢慢滚动到底部才能全部下载
    浏览器逐步加载商品项目，得到图片地址。
    '''        
    def scrollToEnd(self):
        #获得当前窗口高度
        ret=self.browser.execute_script("return document.body.scrollHeight")
        total=0
        while(True):
            innerHeight=self.browser.execute_script("return window.innerHeight")
            
            print(ret)
            while(total<ret):
                self.browser.execute_script("window.scrollTo(0, "+str(total)+"+window.innerHeight);")
                #等待3秒
                time.sleep(2)
                total=total+innerHeight
                #print(total)
            #滚动后会重新加载
            ret1=self.browser.execute_script("return document.body.scrollHeight")
           
            if(ret1<=ret):
                break
            ret=ret1
    #得到当前时间段的秒杀清单
    def getMiaoshaList(self):
        #得到所有秒杀清单
        goods=self.browser.find_elements_by_class_name('seckill_mod_goods')
        if(goods==None):
            return None
        goodsList=[]
        for good in goods:
            item=self.getMiaoshaItem(good);
            if(item==None):
                break
            goodsList.append(item)
        return goodsList;

    def getMiaoshaItem(self,good):
        item={}
        #得到图片链接部分
        a=good.find_element_by_xpath('.//a')
        #链接目标
        item['href']=a.get_attribute('href')
        #得到图片
        img=a.find_element_by_xpath('.//img')
        #图片地址
        item['imgsrc']=img.get_attribute('src')
        h4=a.find_element_by_class_name('seckill_mod_goods_title')
        item['title']=h4.text
        if(len(item['title'])==0):
            return None
        #得到文字部分
        try:
            div=good.find_element_by_xpath('.//div')
        except NoSuchElementException:
            #print("min item")
            self.getmiaoshaoItemMin(a,item)
            return item
        span=div.find_element_by_xpath('.//span')
        span=span.find_element_by_xpath('.//span')
        #原价格
        try:
            item['del']=span.find_element_by_class_name('seckill_mod_goods_price_pre').text
        except NoSuchElementException:
            #print('no del:'+item['title'])
            item['del']=None
        if(item['del']==None):
            #没有显示原价，用JD plus代替
            try:
                item['del']=span.find_element_by_class_name('seckill_mod_goods_plus_jdpr').text
            except NoSuchElementException:
                print('no del:'+item['title'])
            
        #当前价格
        price_now=span.find_element_by_class_name('seckill_mod_goods_price_now')
        #价格前的符合
        em=price_now.find_element_by_tag_name('em')
        #价格
        nowtext=price_now.text
        #把当前价格的人民币符号删除
        item['_$']=em.text
        item['now']=nowtext#[len(em.text):]
        return item
    def getmiaoshaoItemMin(self,a,item):
        try:
            item['del']=a.find_element_by_class_name('seckill_mod_goods_price_pre').text
        except NoSuchElementException:
            item['del']=''
        #当前价格
        price_now=a.find_element_by_class_name('seckill_mod_goods_price_now')
        #价格前的符合
        em=price_now.find_element_by_tag_name('em')
        #价格
        nowtext=price_now.text
        #把当前价格的人民币符号删除
        item['_$']=em.text
        item['now']=nowtext#[len(em.text):]
        
def getFirefox():
    return  webdriver.Firefox()
def openJDMiaosha():
    browser=webdriver.Firefox()
    browser.get('https://miaosha.jd.com/')
    miaosha=MiaoshaNow(browser)
    items=miaosha.spider()
    mg=MongoDb()
    mg.insert(items)
    mg.conn.close()
    browser.quit()
    #关闭浏览器
    #browser.quit()