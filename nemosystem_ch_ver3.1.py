#!/usr/bin/env python
#-*-coding:utf-8 -*-
'''
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
'''
import datetime
import RPi.GPIO as GPIO
import time
'''
from ina219 import INA219
'''
import sys
'''
import schedule
'''
import pymysql

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)  ##PCB Signal Pin##
GPIO.output(13, GPIO.LOW) ##PCB Signal Default##
pcbsignal = False ##If PCB Signal HIGH, change to True.  If PCB Signal LOW, change to False

#FirebaseSetting
'''
cred = credentials.Certificate("/home/pi/Desktop/nemoaspts-firebase-adminsdk-brxci-825e589704.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
'''
'''
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

#mppmaintaincount
mppmaintain = 0


#link to DB
conn=pymysql.connect(host='localhost', user='root',password='1234',db='nemoltec',charset='utf8')
cur=conn.cursor()

'''
#When new day start, initialize daystart to 0
def initdaystart():
    global mppmaintain
    mppmaintain = 0
    print("Brand New Day!")
    
#Find new day time
schedule.every().day.at("00:00:00").do(initdaystart)
'''

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
            '''
            #Schedule module run
            schedule.run_pending()
            '''
        
            '''
            sunv = sunpanelvol.voltage()
            suni = sunpanelvol.current()
            sunp = sunpanelvol.power()
            sunshunt = sunpanelvol.shunt_voltage() 
            suncalv = sunshunt*24000.3855422
            
                        
            inverter1v = invertervol1.voltage()
            inverter1i = invertervol1.current()
            inverter1p = invertervol1.power()
            inverter1shunt = invertervol1.shunt_voltage() 
            inverter1calv = inverter1shunt*31.65 #must add Multplier value here
            
            inverter2v = invertervol2.voltage()
            inverter2i = invertervol2.current()
            inverter2p = invertervol2.power()
            inverter2shunt = invertervol2.shunt_voltage() 
            inverter2calv = inverter2shunt*31.65 #must add Multplier value here
            
            
            inverter3v = invertervol3.voltage()
            inverter3i = invertervol3.current()
            inverter3p = invertervol3.power()
            inverter3shunt = invertervol3.shunt_voltage() 
            inverter3calv = inverter3shunt*31.65 #must add Multplier value here
            
            
            
            
            
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
            print()
                        
            print(now)

            """
            ##For test
            mppmaintain +=1
            print("mppmaintain ++")
            print(mppmaintain)"""
            
            
            
            print()
            print()
            print()
            print()
            print()
            
            
            
            
            #Signal Control
            if(suncalv<200000) : #Result of 2 channel integral has to satisfy under 400V
                                 #WARNING : it can be over 400V because of Sensor accuracy
                GPIO.output(13, GPIO.HIGH) ##PCB Signal HIGH##
                print("PCB SIGNAL HIGH")
                pcbsignal = True
                print("pcbsignal = 1")
            else :
                GPIO.output(13, GPIO.LOW)
                print("PCB SIGNAL LOW")
                pcbsignal = False
                print("pcbsignal = 0")
                
            
            
            
            #When SunVoltage measured, if SunVoltage satisfy MPP range, mppmaintain count ++
            if(100000<suncalv) :
                mppmaintain +=1
                print("mppmaintain ++")
                print(mppmaintain)
            

            ##Send to Firebase
            doc_ref1 = db.collection('nemosystem').document('Collected_data')
            doc_ref1.set({
                'id' : "system1", 'time' : utc_now , 'sunvoltage' : suncalv, 'invertervoltage1' : inverter1calv , 'invertervoltage2' : inverter2calv ,
                'invertervoltage3' : inverter3calv , 'sunvoltage3' : 0 , 'sunvoltage4' : 0 , 'MPPtime' : mppmaintain, 'pcbsignal' : pcbsignal
                })
            '''
            sunvoltage=1
            inverter1calv=2
            inverter2calv=2
            suncalv=6
            inverter3calv=3
            MPPtime=4
            pcbsignal=True
            
            
            
            #Measure in 10 minutes            
            """time.sleep(600)
            
            """
            #Measure in 5seconds            
            time.sleep(5)
            
            #insert sql   
            sql="insert into nemosys(id,time,sunvoltage,invertervoltage1,invertervoltage2,invertervoltage3,MPPtime,pcbsignal) values('system1','"+utc_now.strftime("%H:%M:%S")+"','"+str(suncalv)+"mV','"+str(inverter1calv)+"mV','"+str(inverter2calv)+"mV','"+str(inverter3calv)+"mV','"+str(mppmaintain)+"','"+str(pcbsignal)+"')"
            cur.execute(sql)
            conn.commit()
            
except DeviceRangeError as e:
    print(e)
    
except KeyboardInterrupt:
    print("EXIT")
    conn.close()
    GPIO.cleanup()
        
finally :
    GPIO.cleanup()











