from foc_utils import *
import foc_utils

import time
class Direction:
    CW=1
    CCW=-1
    UNKNOWN = 0 
class Pullup:
    USE_INTERN=0x00
    USE_EXTERN=0x01

class Sensor:
    def __init__(self):
        self.min_elapsed_time = 0.000100; # default is 100 microseconds, or 10kHz
        # velocity calculation variables
        self.velocity=0.0
        self.angle_prev=0.0 # result of last call to getSensorAngle(), used for full rotations and velocity
        self.angle_prev_ts=0 # timestamp of last call to getAngle, used for velocity
        self.vel_angle_prev=0.0 # angle at last call to getVelocity, used for velocity
        self.vel_angle_prev_ts=0 # last velocity calculation timestamp
        self.full_rotations=0 # full rotation tracking
        self.vel_full_rotations=0 # previous full rotation value for velocity calculation
    def getMechanicalAngle(self):
        return self.angle_prev
    def getAngle(self):
        return self.full_rotations *foc_utils._2PI + self.angle_prev
    def getPreciseAngle(self):
        return self.full_rotations *foc_utils._2PI + self.angle_prev
    def getVelocity(self):
        Ts = (self.angle_prev_ts - self.vel_angle_prev_ts)*1e-9
        #print("TS: " ,Ts,"ts2",self.angle_prev_ts,"ts1",self.vel_angle_prev_ts  )

        if Ts < self.min_elapsed_time:
            return self.velocity #don't update velocity if Ts is too small
        #print("Ts > self.min_elapsed_time  TS= : " ,Ts)
        self.velocity = ((self.full_rotations - self.vel_full_rotations)*foc_utils._2PI + (self.angle_prev - self.vel_angle_prev) ) / Ts
        self.vel_angle_prev = self.angle_prev
        self.vel_full_rotations = self.full_rotations
        self.vel_angle_prev_ts = self.angle_prev_ts
        return self.velocity
    def getFullRotations(self):
        return self.full_rotations
    def update(self):
        val = self.getSensorAngle();
        self.angle_prev_ts = time.time_ns()
        d_angle = val - self.angle_prev
        #if overflow happened track it as full rotation
        if abs(d_angle) > (0.8*foc_utils._2PI):
            if d_angle>0:     
                self.full_rotations += -1
            else:
                self.full_rotations += 1
        self.angle_prev = val
    def needsSearch(self):
        return 0
    def getSensorAngle(self):
        print("sorry ,call this")
    def init(self):
        #initialize all the internal variables of Sensor to ensure a "smooth" startup (without a 'jump' from zero)
        self.getSensorAngle()# call once
        time.sleep_ms(1)
        self.vel_angle_prev = self.getSensorAngle() #call again
        self.vel_angle_prev_ts = time.time_ns()
        time.sleep_ms(1)
        self.getSensorAngle() #call once
        time.sleep_ms(1)
        self.angle_prev = self.getSensorAngle() # call again
        self.angle_prev_ts = time.time_ns()   
        #print(self.vel_angle_prev_ts,self.angle_prev_ts)

