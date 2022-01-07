#!/usr/bin/python3

import time, serial
import lxml.etree as et
import sys, os

class Config:
    '''
    Parental class. All inherited classes inherite basic configuration
    and methods for communication.
    '''
    def __init__(self) -> None:
        # recognize used OS and setting app directory
        if 'linux' in sys.platform:
            home = os.path.join(os.getenv('HOME'), '.eDrive')
        elif 'win32' in sys.platform:
            home = os.path.join(os.getenv('APPDATA'), 'Roaming', 'eDrive')
        else:
            raise OSError('Not supported OS.')
        try:
            # create app directory when not exists
            if not os.path.exists(home):
                os.mkdir(home)
        except:
            print('Home directory {} creation failed.'.format(home))
            raise PermissionError
        cfile = os.path.join(home, 'config.xml') # setting configuration file
        try:
            xml = et.parse(cfile)   # parse configuration from config xml file
            for node in xml.iter():
                if node.tag == 'com_port':
                    self.port = node.text   # read comport for serial communication
                if node.tag == 'master_mask':
                    self.master_mask = node.text #read master's bus identification mask
                if node.tag == 'testing':   # read testing mode yes/no
                    if node.text == 'True':
                        self.test = True
                    else:
                        self.test = False
                if node.tag == 'test_port': #read name of source input file for testing
                    self.test_port = os.path.join(home, node.text)
                if node.tag == 'error_log': #read name log errors file
                    self.errlog = os.path.join(home, node.text)
        except:
            ''' 
            When reading config file failed, create new one with default configuration
            and set object attributes.
            '''
            config = et.Element('configuration')
            # testing mode yes/no
            testing = et.SubElement(config, 'testing')
            testing.text = 'False'
            self.test = False
            # comport for serial communication, depending on OS
            com_port = et.SubElement(config, 'com_port')
            if 'linux' in sys.platform:
                com_port.text = '/dev/ttyUSB0'
                self.port = '/dev/ttyUSB0'
            else:
                com_port.text = self.port = 'COM1'
                self.port = 'COM1'
            # master's bus identification mask
            master_mask = et.SubElement(config, 'master_mask')
            master_mask.text = 'p999'
            self.master_mask = 'p999'
            # name of source input file for testing
            test_port = et.SubElement(config, 'test_port')
            test_port.text = str(os.path.join(home, 'serport.txt'))
            self.test_port = os.path.join(home, 'serport.txt')
            if not os.path.exists(self.test_port): # if test source file doesn't exist, create default one
                with open(self.test_port, 'a', encoding='utf-8') as f:
                    f.write('p999'+chr(14)+chr(55))
            # name log errors file
            errlog = et.SubElement(config, 'error_log')
            errlog.text = str(os.path.join(home, 'eDrive.errlog'))
            self.errlog = os.path.join(home, 'eDrive.errlog')
            # write configuration file
            document = et.tostring(config, pretty_print=True, xml_declaration=True, encoding="utf-8")
            with open(cfile, 'wb') as f:
                f.write(document)

    def exchangeData(self, device, command, nr_bytes):
        '''
        Method for exchange data thru bus.
        Sends command to slave device and returns answer.
        Input: str() address of device, int() command number code, int() count of expected bytes
        Output: list() of single bytes() 
        '''
        result = []
        rep = 5
        while rep: # make max 5 communication attempts until response appears
            try:
                if not self.test: # when not test mode, open serial connection
                    with serial.Serial(self.port, 2400, timeout = 0) as ser:
                        ser.flushInput() #clean serial input
                        # string of device address+command retyped to bytes string and sent to serial bus
                        ser.write(bytes(device + chr(command), 'utf-8')) # write to serial port
                        print('To device {0} was sent command {1}.'.format(device, command))
                        time.sleep(2) # time pause until measurements done
                        picaxe = ser.readline() # read line of bytes from bus
                else: # when test mode is running, read bytes from file, not from serial bus
                    with open(self.test_port, 'r', encoding='utf-8') as ser:
                        time.sleep(1)
                        picaxe = bytes(ser.readline(), 'utf-8') # offline; read line from the test file and retype to bytes sequence
                for n in range(len(picaxe)): #iterate thru given sequence of bytes and searching bytes come after 'master mask'
                    x = chr(picaxe[n]) + chr(picaxe[n+1]) + chr(picaxe[n+2]) + chr(picaxe[n+3])
                    if x == self.master_mask: # if 'master mask' found, append next bytes to return list
                        try:
                            for a in range(nr_bytes): # make list of bytes after 'mask'
                                result.append(picaxe[n+4+a])
                        except IndexError:
                            self.__log('exchangeData(): Expected count of bytes not found.')
                        break # break for n
                break # break while rep
            except (serial.SerialException, FileNotFoundError, IndexError) as e:
                self.__log('exchangeData(): {0}; {1}'.format(e, type(e).__name__ ))
                if rep == 1: raise e # when 5 attempts gone, raise exception
            rep -= 1
        print('From device {0} come {1} bytes: {2}'.format(device, len(result), result))
        return result

    def sendData(self, device, command): # to be completed
        pass

    def __log(self, text):
        '''
        Writes datum&text to error log
        '''
        try:
            with open(self.errlog, 'a', encoding='utf-8') as f:
                if f.write('{0} {1} \n'.format(time.strftime('%d.%m.%Y %H:%M'), text)):
                    return True
                else:
                    return False
        except:
            print('Log failed.')


class Temperature(Config):
    '''
    Class represents temperature of the sensor at the device.
    At Picaxe08M hardware one device has two sensors, measurement at each sensor has it's own command.
    Args: str() device name, int() command nr.
    '''
    def __init__(self, device, command) -> None:
        super().__init__()
        self.device = device
        self.command = command

    def measure(self, repeat=5):
        '''
        Method returns temperature value from sensor.
        Input: int() number of measure repeats
        Output: +-float() temperature averange value from <repeat-2> count 
        '''
        if repeat < 3: # not possible set less repeats than 3; min/max values are cut off
            self.__log('measure(): Min. <repeat> value=3. Set to 3.')
            repeat = 3
        temperatures = []
        for _ in range(repeat): # repeat measurements
            datas = self.exchangeData(self.device, self.command, 2) # send command and get 2 bytes according to DS18B20 sensor 12bit protocol
            x = self.__alignByte(datas[0]) + self.__alignByte(datas[1]) #make one str() which represents sequence of bits from input values
            temperature = 0
            # get temp values acc to DS18B20 sensor 12bit protocol
            p = 6
            for n in range(5,16): # sum of each bit powers according by it's position 
                temperature += int(x[n])*2**p
                p = p - 1
            if x[4] == '1': # if the fifth bit is 1, temperature is negative
                temperature -= 128
            temperatures.append(temperature)
        temperatures = sorted(temperatures) # sort values in min-max order
        # cut min/max values, make averange and round
        return round((sum(temperatures[1:(repeat-1)]))/(repeat-2),1) 

    def __alignByte(self, intbyte):
        '''
        Returns 8-chars string, which is binary representation of int value input
        examples: alignByte(11) -> '00001011'
                alignByte(36) -> '00100100'
        '''
        return '0' * (8-len(str(bin(intbyte))[2:])) + str(bin(intbyte))[2:]
