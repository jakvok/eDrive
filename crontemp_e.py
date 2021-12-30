#!/usr/bin/python3
'''
Script for reading temperatures from four DS18B20 sensors.
*picaxe firmware: ser19.bas
*script writes current time and values from all sensors to the text file & csv file
*script is launched by crontab
*each final value is result from 5 measures

testing ser19.bas, more commands, 4 temperatures

'''


import serial
import time

TEST = False  # True for offline testing, False for serial broadcasting
#'p999'+chr(14)+chr(111)+chr(1)+chr(35) values for => (-25.625, 18.1875)

if not TEST:
	PORT = '/dev/ttyUSB0' # I/O, serial port
	CSV = '/home/jakvok/robot/eDrive/temper_e.csv' #output csv file, path to apache source folder
else:
	PORT = './serport_e.txt' #file with simulated serial input
	CSV = './temper_test_e.csv' #test output csv file



def sendData(adress, command, connection):
	'''
	Sends data to serialport.
	input:
		adress of the slave device, command number, opened serport reference
	output:
		True if success, False if failed
	'''
	try:
		if not TEST:
			connection.flushInput() #clean serial input
		data = adress+chr(command) #string of device address and command
		data = bytes(data, 'utf8') #retype to bytes string
		if not TEST:
			connection.write(data) #write string of bytes to serial port
		print('To address', adress, 'was sent command', command, 'data:', data) #stdout confirmation
		return True		
	except serial.SerialException:
		print('Port not found.')
		return False
	except ValueError:
		print('ValueException')
		return False
	except IndexError:
		print('IndexError')
		return False

def recieveData(nr_bytes, connection):
	'''
	Reads serial input.
	Selects given number of bytes followed after 'mask' sequence of master device
	input:
		desired number of bytes
	output:
		if read success:
			list of int() values comming from read bytes
		if read fail:
			list contains one value -> error code
	'''
	result = []
	mask = 'p999'
	try:
		if not TEST:	
			picaxe = connection.readline() # serial communication, read sequence of bytes
		else:
			picaxe = bytes(connection.readline(), 'utf8') # offline; read line from the test file and retype to bytes sequence
		try:
			for n in range(len(picaxe)): #iterate thru given sequence of bytes and searching bytes come after 'mask'
				x = chr(picaxe[n]) + chr(picaxe[n+1]) + chr(picaxe[n+2]) + chr(picaxe[n+3])
				if x == mask: # if 'mask' found, append next bytes to return list
					try:
						for a in range(nr_bytes):
							result.append(picaxe[n+4+a])
					except IndexError:
						print('moc kratka zprava')
					break
			return result
		except IndexError:
			print('mask not found')
			result.append(665)
			return result		
	except serial.SerialException:
		print('port not found')
		result.append(666)
		return result
	except ValueError:
		print('ValueException')
		result.append(667)
		return result
	except IndexError:
		print(picaxe)
		result.append(668)
		return result

def alignByte(intbyte):
	'''
	Returns 8-chars string, which is binary representation of int value input
	examples: alignByte(11) -> '00001011'
	          alignByte(36) -> '00100100'
	'''
	return '0' * (8-len(str(bin(intbyte))[2:])) + str(bin(intbyte))[2:]

def temp12bit(MSbyte, LSbyte):
	'''
	Transfers two input int() values to one float() value
	represents temperature by protocol of sensor DS18B20
	'''
	x = alignByte(MSbyte) + alignByte(LSbyte) #make one str() which represents sequence of bits from input values
	result = 0
	p = 6
	for n in range(5,16): # sum of each bit powers according by its position 
		result += int(x[n])*2**p
		p = p - 1
	if x[4] == '1': # if the fifth bit is 1, temperature is negative
		result -= 128
	return result

def temperature(address, command):
	'''
	Ridi komunikaci
	Controls serial communication, open & close serport
	input:
		slave device address str(), command number int()
	output:
		list of 2 float() temperature values from given slave device
	'''
	try:
		if not TEST:
			ser = serial.Serial(PORT, 2400, timeout = 10) # open serial port
		else:
			ser = open(PORT, 'r', encoding='utf-8') # open test file

		if sendData(address,command,ser): # if command sent successfully to slave device, read bytes from slave device
			time.sleep(1)
			tempers = recieveData(2,ser)
	
			sensor = temp12bit(tempers[0], tempers[1]) # temperature value	
		else:
			print('broadcasting failed')
			
		ser.close()
		return sensor
	except serial.SerialException:
		print('port not found')
		return False
	except IndexError:
		print
		('temperature() didn\'t recieve data')
		return False



temp = [list() for x in range(4)] # make list of 4 empty lists 

for n in range(5): # five times get values from 4 sensors
	while True:
		sensorP1C1 = temperature('p001',81) # get temperature C.1 from slave device P001
		if sensorP1C1:
			break
	while True:
		sensorP1C2 = temperature('p001',82) # get temperature C.2 from slave device P001
		if sensorP1C2:
			break
	while True:
		sensorP2C1 = temperature('p002',81) # get temperature C.1 from slave device P002
		if sensorP2C1:
			break
	while True:
		sensorP2C2 = temperature('p002',82) # get temperature C.2 from slave device P002
		if sensorP2C2:
			break
	temp[0].append(sensorP1C1) #list of 5 values - deviceP1, sensor1
	temp[1].append(sensorP1C2) #list of 5 values - deviceP1, sensor2
	temp[2].append(sensorP2C1) #list of 5 values - deviceP2, sensor1
	temp[3].append(sensorP2C2) #list of 5 values - deviceP2, sensor2

fin_t = [] #list for final 4 values of temteratures

for m in temp: #remove min/max values and make average from 3 remaining values
	m = sorted(m)
	fin_t.append((sum(m[1:4]))/3)

for o in range(len(fin_t)): # round all final values
	fin_t[o] = round(fin_t[o],1)	

# output string for csv file
csv_text = '{};{};{};{};{}\n'.format(time.strftime('%d.%m.%Y %H:%M'),fin_t[0],fin_t[1],fin_t[2],fin_t[3])
print(csv_text)

try: # write into csv file
	with open(CSV, 'a', encoding='utf-8') as f_dat:
		f_dat.write(csv_text)
except:
	print('Writing to file {} failed.'.format(CSV))