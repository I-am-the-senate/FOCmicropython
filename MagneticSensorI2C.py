from machine import I2C,Pin
import math
import time

from micropython import const
from ustruct import unpack, pack
from collections import namedtuple
from time import sleep

from Sensor import *

m12 = const((1<<12)-1)  #0xFFF
REGS=namedtuple('REGS','ZMCO ZPOS MPOS MANG CONF RAWANGLE ANGLE  STATUS AGC MAGNITUDE BURN')
r = REGS(0,1,3,5,7,0xc,0xe,0x0b,0x1a,0xb,0xff)
#You cant overwrite __attribute__ in micropython but you can use Descriptors
class RegDescriptor:
    "Read and write a bit field from a register"
    
    def __init__(self,reg,shift,mask,buffsize=2):
        "initialise with specific identifiers for the bit field"

        self.reg = reg
        self.shift = shift
        self.mask = mask
        self.buffsize = buffsize
        self.writeable = (r.ZMCO,r.ZPOS,r.MPOS,r.MANG,r.CONF,r.BURN)
        #NB the I2c object and the device name come from the main class via an object       
    def get_register(self,obj):
        "Read an I2C register"
        #cache those registers with values that will not change.
        #Dont bother caching bit fields.
        if self.reg in obj.cache:  
             return obj.cache[self.reg]
        #print ('reading now the actual device now')
            
        buff = obj.i2c.readfrom_mem(obj.chip_address,self.reg,self.buffsize)
  
        if self.buffsize == 2:
            v = unpack(">H",buff)[0]  #2 bytes big endian
        else:
            v = unpack(">B",buff)[0]
        #cache writeable values since they are the ones that will not change in useage    
        if self.reg in self.writeable:
            obj.cache[self.reg] = v         
        return v
        
    def __get__(self,obj,objtype):
        "Get the register then extract the bit field"
        v = self.get_register(obj)
        if self.reg == 11:
            print(self.reg,self.shift,self.mask)
        v >>= self.shift
        v &= self.mask
        return v
    
    def __set__(self,obj,value):
        "Insert a new value into the bit field of the old value then write it back"
        if not self.reg in self.writeable:
            raise AttributeError('Register is not writable')
        oldvalue = self.get_register(obj)
        #oldvalue <<= self.shift # get_register() does a shift, so we have to shift it back
        insertmask = 0xffff - (self.mask << self.shift) #make a mask for a hole
        oldvalue &= insertmask # AND a hole in the old value
        value &= self.mask # mask our new value in case it is too big
        value <<= self.shift
        oldvalue |= value  # OR the new value back into the hole
        if self.buffsize == 2:
            buff = pack(">H",oldvalue)
        else:
            buff = pack(">B",oldvalue)
            
        obj.i2c.writeto_mem(obj.chip_address,self.reg,buff) # write result back to the AS5600
        
        #must write the new value into the cache
        self.cache[self.reg] = oldvalue



class MagneticSensorI2CConfig_s:
    def __init__(self):
        self.chip_address = 0x36     
        self.bit_resolution = 12
        self.angle_register = 0x0C
        self.data_start_bit = 11

class MagneticSensorI2C(Sensor):
    def __init__(self):
        #super(MagneticSensorI2C,self).__init__()
        super().__init__()
        self.chip_address=0x36     
        self.lsb_used='' #!< Number of bits used in LSB register
        self.lsb_mask=''
        self.msb_mask=''       
        self.cpr=4096 #!< Maximum range of the magnetic sensor
        self.angle_register_msb='' #!< I2C angle register to read
        self.i2c=''
        
        self.writeable =(r.ZMCO,r.ZPOS,r.MPOS,r.MANG,r.CONF,r.BURN)
        self.cache = {} #cache register values
    RAWANGLE=  RegDescriptor(r.RAWANGLE,0,m12) 
    ANGLE   =  RegDescriptor(r.ANGLE,0,m12) #angle with various adjustments (see datasheet)

    def init_detail(self,_chip_address, _bit_resolution, _angle_register_msb, _bits_used_msb):
        
        self.chip_address = _chip_address
        #angle read register of the magnetic sensor
        self.angle_register_msb = _angle_register_msb
        #register maximum value (counts per revolution)
        self.cpr = pow(2, _bit_resolution)

        # depending on the sensor architecture there are different combinations of
        # LSB and MSB register used bits
        # AS5600 uses 0..7 LSB and 8..11 MSB
        # AS5048 uses 0..5 LSB and 6..13 MSB
        # used bits in LSB
        self.lsb_used = _bit_resolution - _bits_used_msb
        # extraction masks
        self.lsb_mask =( (2 << lsb_used) - 1 )
        self.msb_mask =( (2 << _bits_used_msb) - 1 )
     # MagneticSensorI2C class constructor
     # @param config  I2C config
    def init_config(self, config):
        self.chip_address = config.chip_address 
        # angle read register of the magnetic sensor
        self.angle_register_msb = config.angle_register
        # register maximum value (counts per revolution)
        self.cpr = pow(2, config.bit_resolution)
        bits_used_msb = config.data_start_bit - 7
        lsb_used = config.bit_resolution - bits_used_msb
        # extraction masks
        self.lsb_mask = (2 << lsb_used) - 1 
        self.msb_mask = (2 << bits_used_msb) - 1 

    #* sensor initialise pins #
    def init(self,_i2c):
        self.i2c=_i2c
        super().init()
  
    # implementation of abstract functions of the Sensor class
    #* get current angle (rad) #
    def getSensorAngle(self):
        return  ( self.getRawCount() / self.cpr) *2*math.pi
    # I2C functions
    #* Read one I2C register value #
    def read(self,angle_register_msb):
        return self.RAWANGLE
    # Function getting current angle register value
    # it uses angle_register variable
    def getRawCount(self):
        return self.read(self.angle_register_msb);




