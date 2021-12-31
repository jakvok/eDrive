#!/usr/bin/python3

import time, serial
import lxml.etree as et

class Config:
    '''
    Parental class. All inherited classes inherite basic configuration
    and methods for communication.
    '''
    def __init__(self, cfile='./config.xml') -> None:
        xml = et.parse(cfile)   # read configuration from config xml file
        for node in xml.iter():
            if node.tag == 'com_port':
                self.port = node.text   # comport for serial communication
            if node.tag == 'master_mask':
                self.master_mask = node.text
            if node.tag == 'testing':   # testing mode yes/no
                if node.text == 'True':
                    self.test = True
                else:
                    self.test = False
            if node.tag == 'test_port': # source input file for testing
                self.test_port = node.text

    def exchangeData(self, device, command, nr_bytes):
        '''
        Method for exchange data thru bus.
        Sends command to slave device and returns answer.
        Input: str() address of device, int() command number code, int() count of expected bytes
        Output: list() of single bytes() 
        '''
        result = []
        try:
            if not self.test:
                with serial.Serial(self.port, 2400, timeout = 10) as ser:
                    ser.flushInput() #clean serial input
                    # string of device address+command retyped to bytes string and sent to serial bus
                    ser.write(bytes(device + chr(command), 'utf-8'))
                    time.sleep(1)
                    picaxe = ser.readline() # read line of bytes from bus
            else:
                with open(self.test_port, 'r', encoding='utf-8') as ser:
                    time.sleep(1)
                    picaxe = bytes(ser.readline(), 'utf-8') # offline; read line from the test file and retype to bytes sequence
            for n in range(len(picaxe)): #iterate thru given sequence of bytes and searching bytes come after 'mask'
                x = chr(picaxe[n]) + chr(picaxe[n+1]) + chr(picaxe[n+2]) + chr(picaxe[n+3])
                if x == self.master_mask: # if 'mask' found, append next bytes to return list
                    try:
                        for a in range(nr_bytes):
                            result.append(picaxe[n+4+a])
                    except IndexError:
                        print('Too short message.')
                    break
            #print('dataExchange():',result)
            return result
        except serial.SerialException as e:
            print('exchangeData:', e)
            print(type(e).__name__)
        except FileNotFoundError as e:
            print('exchangeData:', e)
            print(type(e).__name__)

    def sendData(self, device, command):
        pass


class Temperature(Config):
    '''
    Class represents temperature of the sensor at the device.
    At Picaxe08M hardware one device has two sensors, measurement at each sensor has it's own command.
    Args: str() device name, int() command nr., str() config file
    '''
    def __init__(self, device, command, cfile='./config.xml') -> None:
        super().__init__(cfile)
        self.device = device
        self.command = command
        xml = et.parse(cfile)   # read configuration from config xml file
        for node in xml.iter():
            if node.tag == 'temperature':
                self.output = node[0].text   # output file
                self.test_output = node[1].text # test file output

    def measure(self, repeat=5):
        '''
        Method returns temperature value from sensor.
        Input: int() number of measure repeat
        Output: +-float() temperature averange value from <repeat-2> count 
        '''
        if repeat < 3:
            print('Min. <repeat> value=3')
            return False
        temperatures = []
        for _ in range(repeat):
            datas = self.exchangeData(self.device, self.command, 2)
            x = self.__alignByte(datas[0]) + self.__alignByte(datas[1]) #make one str() which represents sequence of bits from input values
            temperature = 0
            p = 6
            for n in range(5,16): # sum of each bit powers according by its position 
                temperature += int(x[n])*2**p
                p = p - 1
            if x[4] == '1': # if the fifth bit is 1, temperature is negative
                temperature -= 128
            temperatures.append(temperature)
        temperatures = sorted(temperatures)
        # cut min/max values, make averange and round
        return round((sum(temperatures[1:(repeat-1)]))/(repeat-2),1) 

    def __alignByte(self, intbyte):
        '''
        Returns 8-chars string, which is binary representation of int value input
        examples: alignByte(11) -> '00001011'
                alignByte(36) -> '00100100'
        '''
        return '0' * (8-len(str(bin(intbyte))[2:])) + str(bin(intbyte))[2:]




'''
temp = Temperature('p001', 81)

print(temp.port)
print(temp.master_mask)
print(temp.test)
print(temp.test_port)
print(temp.output)
print(temp.test_output)

print(temp.measure())
'''