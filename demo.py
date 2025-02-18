# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import webrepl
webrepl.start()
from machine import Pin,PWM
import math
import time
import PID

P=1

#AS5600_I2C=MagneticSensorI2CConfig_s()
#sensor = MagneticSensorI2C()
#sensor.init_config(AS5600_I2C)
#i2c = I2C(0,scl=Pin(22),sda=Pin(21),freq=400000)        
#sensor.init(i2c)



EN = Pin( 27 ,Pin.OUT)
EN.value(1)


timestamp = 0
zeroang = 0
voltage = 12
poles = 18
shaftangle = 0
targetvelocity = 6.28
timestampopen = 0
pwmA = PWM(Pin(7, Pin.OUT), 17000)
pwmB = PWM(Pin(8, Pin.OUT), 17000)
pwmC = PWM(Pin(9, Pin.OUT), 17000)




def constrain(a,low,high):
    if low < a < high:
        a = a
    elif a < low:
        a = low
    else:
        a = high
    return a
def electricalangle(SHAFTang,poles):
    return SHAFTang*poles
#def sensorelectricalangle():
    #return sensor.getSensorAngle()*7
def normalizeangle(Angle):
    a = math.fmod(Angle,2*math.pi)
    return a if a > 0 else (a+2*math.pi)
def setpwm(Ua,Ub,Uc):
    pwmA.duty(int(Ua/voltage*1023))
    pwmB.duty(int(Ub/voltage*1023))
    pwmC.duty(int(Uc/voltage*1023))
def setvoltage(Uq,El):
    El = normalizeangle (El)
    Ualpha = -Uq*math.sin(El)
    Ubeta = Uq*math.cos(El)
    Ua = Ualpha + 12 / 2
    Ub = (1.732051*Ubeta-Ualpha)/2+12/2
    Uc = (-Ualpha-1.732051*Ubeta)/2+12/2
    setpwm(Ua,Ub,Uc)
a=0
'''
def tolocation (angle,P):
    EN.value(1)
    target = angle*(2*math.pi)/360
    while 1:
        setvoltage (constrain(P*target-sensor.getAngle(),-6,6) ,0 ,sensorelectricalangle())
        if abs(target-sensor.getAngle()) <0.05:
            time.sleep_ms(100)
            EN.value(0)
            break
    return

def freezeat (angle,P):
    EN.value(1)
    target = angle*(2*math.pi)/360
    while 1:
        setvoltage (constrain(P*target-sensor.getAngle(),-6,6) ,0 ,sensorelectricalangle())
    return
'''
time.sleep(3)



while True:
    Ts = (time.ticks_us()- timestampopen)*0.000006
    if Ts < 0 :
        Ts = 0.001
    shaftangle = normalizeangle(shaftangle + targetvelocity* Ts)
    Uq = voltage/4
    setvoltage(Uq,electricalangle(shaftangle,poles))
    timestampopen = time.ticks_us()

        

    
    
    


  



