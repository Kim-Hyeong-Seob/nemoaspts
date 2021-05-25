#!/usr/bin/env python
#-*-coding:utf-8 -*-
'''
--------------<Explain>--------------
[ver4.4] : prototype(no serial algorithm) + log DB + csv export + log DB maintain 4week
+ csv export in every 1 day to [/tmp]
'''

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

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
GPIO.output(15, GPIO.HIGH) ##PCB Signal Default Must Be HIGH!!##
pcbsignal = 0 ##If PCB Signal HIGH, change to 1.  If PCB Signal LOW, change to 0

#FirebaseSetting
cred = credentials.Certificate("/home/pi/nemoaspts-firebase-adminsdk-brxci-78896493bf.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

#DB_Setting
conn=pymysql.connect(host='localhost', user='root',password='1234',db='nemolt',charset='utf8')
cur=conn.cursor()







#SunPanelVoltage
sunpanelvol = INA219(shunt_ohms=0.1,
             max_expected_amps=3.1,
             address=0x40)

#InverterVoltage1
invertervol1 = INA219(shunt_ohms=0.1,
             max_expected_amps=3.1,
             address=0x41)

#InverterVoltage2
invertervol2 = INA219(shunt_ohms=0.1,
             max_expected_amps=3.1,
             address=0x44)

#InverterVoltage3
invertervol3 = INA219(shunt_ohms=0.1,
             max_expected_amps=3.1,
             address=0x45)


sunpanelvol.configure(voltage_range=sunpanelvol.RANGE_32V,
              gain=sunpanelvol.GAIN_AUTO,
              bus_adc=sunpanelvol.ADC_128SAMP,
              shunt_adc=sunpanelvol.ADC_128SAMP)
'''
invertervol1.configure(voltage_range=invertervol1.RANGE_32V,
              gain=invertervol1.GAIN_AUTO,
              bus_adc=invertervol1.ADC_128SAMP,
              shunt_adc=invertervol1.ADC_128SAMP)

invertervol2.configure(voltage_range=invertervol2.RANGE_32V,
              gain=invertervol2.GAIN_AUTO,
              bus_adc=invertervol2.ADC_128SAMP,
              shunt_adc=invertervol2.ADC_128SAMP)

invertervol3.configure(voltage_range=invertervol3.RANGE_32V,
              gain=invertervol3.GAIN_AUTO,
              bus_adc=invertervol3.ADC_128SAMP,
              shunt_adc=invertervol3.ADC_128SAMP)
              '''

  
#Global Calculated Sun Voltage
suncalv = 0

#Generation Check 
Dev_Current = 0
Development = 0
Current_list = []
Max_Current = 0

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
    global Dev_Current
    global Development
    global Current_list
    global Max_Current
    
    Current_list = []
    seconds =(datetime.datetime.now()+datetime.timedelta(seconds=2)).second
    while seconds != datetime.datetime.now().second:
        current_level = ReadChannel()
        current_current = ConvertCurrent(current_level,2)
        Current_list.append(current_current)
    
    if(Max_Current<1.5 and suncalv<145000):   
        Dev_Current = 10
    elif(Max_Current<1.5 and suncalv>145000):
        Dev_Current = 0
        print("err")
        #first 20 seconds for ready to run can be displayed as Err.
    elif (Max_Current>1.5 and suncalv>110000) :
        print(Max_Current)
        Dev_Current = 10
        Development += 1
        print("ok")    
   

    
#Find new day time
schedule.every().day.at("00:00:00").do(initdaystart)
##csv export time_SGH
schedule.every().day.at("00:00:00").do(csvmake)


#Generation Check Function in every 1 min.
schedule.every(3).seconds.do(Current)
try :      
        while 1 : 
        
            
            #Get Time UTC
            utc_now = datetime.datetime.utcnow()
            #Get Time Local
            now = datetime.datetime.now()


            
            #PCB Signal Manual Control
            """
            GPIO.output(13,GPIO.HIGH)
            """
            
            #Schedule module run
            schedule.run_pending()
        
        
        
            sunv = sunpanelvol.voltage()
            suni = sunpanelvol.current()
            sunp = sunpanelvol.power()
            sunshunt = sunpanelvol.shunt_voltage() 
            suncalv = sunshunt*32000.3855422
            

            '''            
            inverter1v = invertervol1.voltage()
            inverter1i = invertervol1.current()
            inverter1p = invertervol1.power()
            inverter1shunt = invertervol1.shunt_voltage() 
            inverter1calv = inverter1shunt*220 #must add Multplier value here
            
            inverter2v = invertervol2.voltage()
            inverter2i = invertervol2.current()
            inverter2p = invertervol2.power()
            inverter2shunt = invertervol2.shunt_voltage() 
            inverter2calv = inverter2shunt*220 #must add Multplier value here
            
            
            inverter3v = invertervol3.voltage()
            inverter3i = invertervol3.current()
            inverter3p = invertervol3.power()
            inverter3shunt = invertervol3.shunt_voltage() 
            inverter3calv = inverter3shunt*220 #must add Multplier value here
            '''
            
            
            
            
            
            #Send to Firebase - For Test
            """
            a=a+1;
            b=b+1;
            c=c+1;
            d=d+1;
            
            doc_ref1 = db.collection('nemosystem').document('Collected_data')
            doc_ref1.set({
                'id' : "system1", 'time' : utc_now , 'sunvoltage' : a, 'invertervoltage1' : b , 'invertervoltage2' : c , 'invertervoltage3' : d ,
                'sunvoltage3' : a , 'sunvoltage4' : b , 'MPPtime' : 0
                })"""
            

        
            #Console Display
            print ("--------------SunPanelVoltage-------------")
            print ("Bus Voltage : %.3f V" % sunv)
            print ("Bus Current : %.3f mA" % suni)
            print ("Shunt Voltage : %.3f mV" % sunshunt)
            print ("POWER : %.3f mW" % sunp)
            print ("Calculated Voltage : %.3f mV" % suncalv)
            print()
            
            '''
            print ("--------------Inverter1 Voltage-------------")
            print ("Bus Voltage : %.3f V" % inverter1v)
            print ("Bus Current : %.3f mA" % inverter1i)
            print ("Shunt Voltage : %.3f mV" % inverter1shunt)
            print ("POWER : %.3f mW" % inverter1p)
            print ("Calculated Voltage : %.3f mV" % inverter1calv)
            print()
            
            print ("--------------Inverter2 Voltage-------------")
            print ("Bus Voltage : %.3f V" % inverter2v)
            print ("Bus Current : %.3f mA" % inverter2i)
            print ("Shunt Voltage : %.3f mV" % inverter2shunt)
            print ("POWER : %.3f mW" % inverter2p)
            print ("Calculated Voltage : %.3f mV" % inverter2calv)
            print()
            
            print ("--------------Inverter3 Voltage-------------")
            print ("Bus Voltage : %.3f V" % inverter3v)
            print ("Bus Current : %.3f mA" % inverter3i)
            print ("Shunt Voltage : %.3f mV" % inverter3shunt)
            print ("POWER : %.3f mW" % inverter3p)
            print ("Calculated Voltage : %.3f mV" % inverter3calv)
            '''

            print()
                        
            print(now)

            """
            ##For test
            mppmaintain +=1
            print("mppmaintain ++")
            print(mppmaintain)"""
            
            
            print('-------------------------------')
            print('Generation Time ',Development)
            print()
            print()
            print()
            print()


            #insert sql
            if (len(Current_list)!=0) :
              sql="insert into test (id,time,suncalv,Development,pcbsignal,current) values('system1','"+now.strftime("%Y-%m-%d %H:%M:%S")+"',"+str(suncalv)+","+str(Development)+","+str(pcbsignal)+","+str(Max_Current)+")"
              cur.execute(sql)
            else :
              sql="insert into test (id,time,suncalv,Development,pcbsignal) values('system1','"+now.strftime("%Y-%m-%d %H:%M:%S")+"',"+str(suncalv)+","+str(Development)+","+str(pcbsignal)+")"
              cur.execute(sql)
            
            
            
            
            ##SGH_delete log DB in 4 weeks
            agodays =now-datetime.timedelta(weeks=4)
            deletesql="delete from test where time <='"+agodays.strftime('%Y-%m-%d %H:%M:%S')+"'"
            cur.execute(deletesql)
            
            conn.commit()
            
            
            
            
            
            #Signal Control
            if(suncalv<310000) : #Result of 2 channel integral has to satisfy under 300V
                                 #WARNING : it can be over 300V because of Sensor accuracy
                GPIO.output(15, GPIO.HIGH) ##PCB Signal HIGH##
                print("PCB SIGNAL HIGH")
                pcbsignal = 1
                print("pcbsignal = 1")
            else :
                GPIO.output(15, GPIO.LOW)
                print("PCB SIGNAL LOW")
                pcbsignal = 0
                print("pcbsignal = 0")
                
            

            
            
            ##Send to Firebase
            doc_ref1 = db.collection('nemosystem').document('Collected_data')
            
                
                
            if (len(Current_list)!=0) :
              doc_ref1.set({
                'id' : "system1", 'time' : utc_now , 'sunvoltage' : suncalv, 'invertervoltage1' : Dev_Current , 'invertervoltage2' : 10 ,
                'invertervoltage3' : 10, 'MPPtime' : Development , 'pcbsignal' : pcbsignal, 'max_current' : Max_Current
                })
            else :
              doc_ref1.set({
                  'id' : "system1", 'time' : utc_now , 'sunvoltage' : suncalv, 'invertervoltage1' : Dev_Current , 'invertervoltage2' : 10 ,
                  'invertervoltage3' : 10, 'MPPtime' : Development , 'pcbsignal' : pcbsignal
                  })
                      
            
            
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











