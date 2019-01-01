# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 16:21:49 2018

@author: junhua
"""

import mysql.connector

'''
mysql连接配置
'''
mydb_cfg={'host':'127.0.0.1',
          'user':'root',
          'password':'',
          'port':3306,
          'database':'jd',
          'charset':'utf8mb4'}

def GetMySqlConn():
    try:
        conn=mysql.connector.connect(**mydb_cfg)
        return conn
    except mysql.connector.Error as e:
        print('connect error'+e)
    return None

import pymysql.cursors
'''
获得Mysql连接
'''
def GetPyMysql():
    return pymysql.connect(mydb_cfg['host'],
                           mydb_cfg['user'],
                           mydb_cfg['password'],
                           mydb_cfg['database'],
                           port=mydb_cfg['port'],
                           charset=mydb_cfg['charset']
                           #,
                           #cursorclass=pymysql.cursors.DictCursor
                           )
'''
记录获取数据的时间
'''    
def InsertMiaoshaMain(conn,timestamp):
    sql_cmd='insert into miaosha_main(`timestamp`) values(%(ct)s)'
    param={'ct':timestamp}
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql_cmd,param)
            
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as e:
            print('insert main error'+str(e))
'''
秒杀时间段
'''    
def InsertMiaoshaContent(conn,main_id,timeitem):
    sql_cmd='insert into miaosha_content(main_id,`day_time`) values(%(id)s,%(time)s)'
    param={'id':main_id,'time':timeitem}
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql_cmd,param)
            
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as e:
            print('insert main error'+str(e))
'''
秒杀商品项目
'''            
def InsertMiaoshaItem(conn,time_id,item,img):
    sql_cmd='insert into miaosha_item(time_id,title,now_price,del_price,href,imgsrc,img) values(%(time_id)s,%(title)s,%(now_price)s,%(del_price)s,%(href)s,%(imgsrc)s,%(img)s)'
    param={}
    param['time_id']=time_id
    param['title']=item['title']
    price=item['now']
    #if(price[0]):
    #price=float(price[1:])
    param['now_price']=price
    #price=item['del']
    #if(price[0:1]=='￥'):
    #price=item['del']
    param['del_price']=item['del']
    param['href']=item['href']
    param['imgsrc']=item['imgsrc']
    param['img']=img
    #print(param)
    #return 
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql_cmd,param)
            
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as e:
            print('insert main error'+str(e))

'''
下载图片
'''            
import urllib
def GetImage(url):
    try:
        response=urllib.request.urlopen(url)
        if response==None:
            return None
        msg=response.info()
        if(msg.get_content_type().find('image/')!=-1):
            return response.read()
        return None
    except:
        return None
'''
插入所有数据
'''    
def InsertMiaosha(conn,msinfo):
    main_id=InsertMiaoshaMain(conn,msinfo['ct'])
    for d in msinfo['data']:
        time_id=InsertMiaoshaContent(conn,main_id,d['title'])
        for i in d['items']:
            img=GetImage(i['imgsrc'])
            InsertMiaoshaItem(conn,time_id,i,img)
    