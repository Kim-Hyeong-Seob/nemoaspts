#!/usr/bin/env python
#-*-coding:utf-8 -*-
'''
--------------<Explain>--------------
[ver4.4] : prototype(no serial algorithm) + log DB + csv export + log DB maintain 4week
+ csv export in every 1 day to [/tmp]
'''

import datetime
import RPi.GPIO as GPIO
import time
from ina219 import INA219
import sys

import schedule

import pymysql

import spidev

#Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 60


GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.OUT)  ##PCB Signal Pin##
GPIO.output(15, GPIO.LOW) ##PCB Signal Default##
pcbsignal = 0 ##If PCB Signal HIGH, change to 1.  If PCB Signal LOW, change to 0

#DB_Setting
conn=pymysql.connect(host='localhost', user='root',password='1234',db='nemolt',charset='utf8')
cur=conn.cursor()


#SunPanelVoltage
sunpanelvol = INA219(shunt_ohms=0.1,
             max_expected_amps=3.1,
             address=0x40)

sunpanelvol.configure(voltage_range=sunpanelvol.RANGE_32V,
              gain=sunpanelvol.GAIN_AUTO,
              bus_adc=sunpanelvol.ADC_128SAMP,
              shunt_adc=sunpanelvol.ADC_128SAMP)

#mppmaintaincount
Development = 0


#When new day start, initialize daystart to 0
def initdaystart():
    global Development
    Development = 0
    print("Brand New Day!")

##csv export_SGH
def csvmake():
    yday = datetime.datetime.now()-datetime.timedelta(days=1)
    nowtime = yday.strftime('%Y-%m-%d')
    print(nowtime)
    csvsql = "select *  from test where time like '"+nowtime+"%' into outfile '/tmp/"+nowtime+".csv' fields terminated by ',' enclosed by '\"' lines terminated by '\n'"
    cur.execute(csvsql)
    conn.commit()

def ReadChannel():
    channel=0
    adc= spi.xfer([1,(8+ channel)<<4,0])
    data = ((adc[1] & 3) << 8 ) + adc[2]
    return data

def ConvertCurrent(data,places):
    current=((data * 5) /float(1023)-2.5)/0.066
    current = round (current,places)
    return current

def Current():
    Current_list = []
    seconds =(datetime.datetime.now()+datetime.timedelta(seconds=2)).second
    while seconds != datetime.datetime.now().second:
        current_level = ReadChannel()
        current_current = ConvertCurrent(current_level,2)
        Current_list.append(current_current)
    
    if(max(Current_list)<0.2):
        print("err")
    else :
        print("ok")


#Find new day time
schedule.every().day.at("00:00:00").do(initdaystart)
##csv export time_SGH
schedule.every().day.at("00:00:00").do(csvmake)

schedule.every(10).minutes.do(Current)
try :      
        while 1 : 
        
            
            #Get Time UTC
            utc_now = datetime.datetime.utcnow()
            #Get Time Local
            now = datetime.datetime.now()


            
            #PCB Signal Manual Control
            """
            GPIO.output(15,GPIO.HIGH)
            """
            
            #Schedule module run
            schedule.run_pending()
        
        
        
            sunv = sunpanelvol.voltage()
            suni = sunpanelvol.current()
            sunp = sunpanelvol.power()
            sunshunt = sunpanelvol.shunt_voltage() 
            suncalv = sunshunt*24000.3855422
                        
            #Console Display
            print ("--------------SunPanelVoltage-------------")
            print ("Bus Voltage : %.3f V" % sunv)
            print ("Bus Current : %.3f mA" % suni)
            print ("Shunt Voltage : %.3f mV" % sunshunt)
            print ("POWER : %.3f mW" % sunp)
            print ("Calculated Voltage : %.3f mV" % suncalv)
            print()
                                   
            print(now)           
            
            print()
            print()
            print()
            print()
            print()

            #insert sql

            sql="insert into test(id,time,suncalv,Development,pcbsignal) values('system1','"+now.strftime("%Y-%m-%d %H:%M:%S")+"',"+str(suncalv)+","+str(Development)+","+str(pcbsignal)+")"
            cur.execute(sql)
            
            ##SGH_delete log DB in 4 weeks
            agodays =now-datetime.timedelta(weeks=4)
            deletesql="delete from test where time <='"+agodays.strftime('%Y-%m-%d %H:%M:%S')+"'"
            cur.execute(deletesql)
            
            conn.commit()

            #Signal Control
            if(suncalv<150000) : #Result of 2 channel integral has to satisfy under 400V
                                 #WARNING : it can be over 400V because of Sensor accuracy
                GPIO.output(15, GPIO.HIGH) ##PCB Signal HIGH##
                print("PCB SIGNAL HIGH")
                pcbsignal = 1
                print("pcbsignal = 1")
            else :
                GPIO.output(15, GPIO.LOW)
                print("PCB SIGNAL LOW")
                pcbsignal = 0
                print("pcbsignal = 0")

            #When SunVoltage measured, if SunVoltage satisfy MPP range, mppmaintain count ++
            if(750000<suncalv) :
                Development +=1
                print("mppmaintain ++")
                print(Development)
            
            
            #Measure in 10 minutes            
            """time.sleep(600)
            
            """
            #Measure in 5seconds            
            time.sleep(5)
            
        
except DeviceRangeError as e:
    print(e)
    
except KeyboardInterrupt:
    print("EXIT")
    GPIO.cleanup()
    conn.close()
finally :
    GPIO.cleanup()
    conn.close()











