import logging
import math
import time
import smbus


logger = logging.getLogger(__name__)

"""
def get_i2c_device(address, i2c, i2c_bus):
    # Helper method to get a device at the specified address from the I2C bus.
    # If no i2c bus is specified (i2c param is None) then the default I2C bus
    # for the platform will be used.
    if i2c is not None:
        return i2c.get_i2c_device(address)
    else:
        import Adafruit_GPIO.I2C as I2C
        if i2c_bus is None:
            return I2C.get_i2c_device(address)
        else:
            return I2C.get_i2c_device(address, busnum=i2c_bus)
"""

class PWM(object):
    # Registers/etc.
    __MODE1              = 0x00
    __MODE2              = 0x01
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALL_LED_ON_L       = 0xFA
    __ALL_LED_ON_H       = 0xFB
    __ALL_LED_OFF_L      = 0xFC
    __ALL_LED_OFF_H      = 0xFD

    # Bits
    __RESTART            = 0x80
    __SLEEP              = 0x10
    __ALLCALL            = 0x01
    __INVRT              = 0x10
    __OUTDRV             = 0x04


#    @classmethod
#    def softwareReset(cls, i2c=None, i2c_bus=None):
#        "Sends a software reset (SWRST) command to all the servo drivers on the bus"
#        general_call_i2c = smbus.SMBUS(i2c_bus)
#        general_call_i2c.writeRaw8(0x06)        # SWRST

    def __init__(self, address=0x40, debug=False, i2c=None, i2c_bus=None):
        self.i2c = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        logger.debug("Reseting PCA9685 MODE1 (without SLEEP) and MODE2")
        self.setAllPWM(0, 0)
        self.write(self.__MODE2, self.__OUTDRV)
        self.write(self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)                             # wait for oscillator
        mode1 = self.read(self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
        self.write(self.__MODE1, mode1)
        time.sleep(0.005)                             # wait for oscillator

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.i2c.write_byte_data(self.address, reg, value)
        logger.debug("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.i2c.read_byte_data(self.address, reg)
        logger.debug("I2C: Device 0x%X returned 0x%X from reg 0x%X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        logger.debug("Setting PWM frequency to %d Hz" % freq)
        logger.debug("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        logger.debug("Final pre-scale: %d" % prescale)
        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
        self.read(self.__MODE1)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)

    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.write(self.__ALL_LED_ON_L, on & 0xFF)
        self.write(self.__ALL_LED_ON_H, on >> 8)
        self.write(self.__ALL_LED_OFF_L, off & 0xFF)
        self.write(self.__ALL_LED_OFF_H, off >> 8)        
        

if __name__ == "__main__":
    pwm = PWM(0x40, debug=False)
    pwm.setPWMFreq(50)
    pwm.setDutycycle(0,50)
    pwm.setLevel(1,0)
    pwm.setLevel(2,0)
    pwm.setDutycycle(5,50)
    pwm.setLevel(3,0)
    pwm.setLevel(4,0)