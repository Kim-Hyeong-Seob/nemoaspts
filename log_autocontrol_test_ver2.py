#!/usr/bin/env python
#-*-coding:utf-8 -*-
'''
--------------<Explain>--------------
[ver4.1] : prototype + log DB + csv export
'''


import datetime

import time

import sys

import schedule

import pymysql


#DB_Setting
conn=pymysql.connect(host='localhost', user='root',password='1234',db='nemoltec',charset='utf8')
cur=conn.cursor()

#Test variables
suncalv=0
inverter1calv=1
inverter2calv=2
inverter3calv=3
mppmaintain=4
pcbsignal=5




##csv export_SGH
def csvmake():
    yday = datetime.datetime.now()-datetime.timedelta(days=1)
    nowtime = yday.strftime('%Y-%m-%d')
    print(nowtime)
    csvsql = "select *  from nemosys where time like '"+nowtime+"%' into outfile '/tmp/"+nowtime+".csv' fields terminated by ',' enclosed by '\"' lines terminated by '\n'"
    cur.execute(csvsql)
    conn.commit()


    
    
#Initialize mpptime and csvmake at every 00:00:00 
scheduler1 = schedule.Scheduler()
scheduler1.every().day.at("17:34:00").do(csvmake)


try :      
        while 1 : 
        
            
            #Get Time UTC
            utc_now = datetime.datetime.utcnow()
            #Get Time Local
            now = datetime.datetime.now()

            print("now",now)
            print("utc_now",utc_now)

            #Every 4weeks from now
            agodays =now-datetime.timedelta(minutes=1)
            
            #PCB Signal Manual Control
            """
            GPIO.output(13,GPIO.HIGH)
            """
            
            #Schedule module run
            scheduler1.run_pending()

            #insert sql

            sql="insert into nemosys(id,time,`sunvoltage(mV)`,`invertervoltage1(mV)`,`invertervoltage2(mV)`,`invertervoltage3(mV)`,MPPtime,pcbsignal) values('system1','"+now.strftime("%Y-%m-%d %H:%M:%S")+"',"+str(suncalv)+","+str(inverter1calv)+","+str(inverter2calv)+","+str(inverter3calv)+","+str(mppmaintain)+","+str(pcbsignal)+")"
            cur.execute(sql)

            
            ##SGH_mariaDB datetime type can be calculated by [<=, == ... etc]
            '''
            deletesql="delete from nemosys where time <='"+agodays.strftime('%Y-%m-%d')+"'"
            '''
            deletesql="delete from nemosys where time <='"+agodays.strftime('%Y-%m-%d %H:%M:%S')+"'"
            cur.execute(deletesql)
            
            conn.commit()

            #Measure in 10 minutes            
            """time.sleep(600)
            
            """
            #Measure in 5seconds            
            time.sleep(5)

except KeyboardInterrupt:
    print("EXIT")
    conn.close()
finally :
    conn.close()












