#!/usr/bin/python3
'''
Testovaci pgm pro cteni teploty z PICAXE, v.c2
*pracuje se ser18.bas
*Funkce vychazi z temper10.py
*Skript zjisti 1x teploty ze vsech cidel a zapise do text souboru a do csv souboru
*Skript je spousten pomoci crontab
*Teplota pocitana z 5ti mereni

'''


import serial
import time

PORT = '/dev/ttyUSB0'
FILE = '/home/jakvok/robot/cron_temp/temper.dat' #soubor pro textovy zaznam
CSV = '/var/www/html/temper.csv' #soubor pro datove zpracovani

def sendData(adresa, prikaz, ial):
	'''
	Posila data na serialport.
	vstup:
		adresa prislusneho volaneho slejva, cislo prikazu pro slejva
	vystup:
		True kdyz uspech, False kdyz neuspech
	'''
	#print()
	#print('sendData:')
	try:
		ial.flushInput()
		data = adresa+chr(prikaz)
		data = bytes(data, 'utf8')
		ial.write(data)
		print('na adresu', adresa, 'byl zaslan prikaz', prikaz)
		#print('data:', data)
		return True		
	except serial.SerialException:
		print('Port nenalezen.')
		return False
	except ValueError:
		print('ValueException')
		return False
	except IndexError:
		print('IndexError')
		return False

def recieveData(pocetBajtu, ial):
	'''
	Precte radek v bufferu serialportu.
	Vyzobe prislusny pocet bajtu nasledujici po sekvenci adresy masteru (po masce)
	vstup:
		chteny pocet bajtu zpravy
	vystup:
		pokud se cteni povede:
			seznam int() hodnot odpovidajicich prislusnemu chtenemu poctu bajtu 
		pokud se nepovede:
			jednoprvkovy seznam kodu chyby
	'''
	seznam = []
	vysledek = []
	maska = 'p999'
	#print()
	#print('recieveData():')
	try:	
		picaxe = ial.readline()
		#print('picaxe:',picaxe)
		for n in picaxe:
			seznam.append(n)
		#print('seznam:', seznam)
		try:
			for n in range(len(seznam)-1):
				x = chr(seznam[n]) + chr(seznam[n+1]) + chr(seznam[n+2]) + chr(seznam[n+3])
				if x == maska:
					try:
						for a in range(pocetBajtu):
							vysledek.append(seznam[n+4+a])
					except IndexError:
						print('moc kratka zprava')
					break
			#print('vysledek:', vysledek)
			return vysledek	
		except IndexError:
			print('nenalezena maska')
			vysledek.append(665)
			return vysledek		
	except serial.SerialException:
		print('Port nenalezen.')
		vysledek.append(666)
		return vysledek
	except ValueError:
		print('ValueException')
		vysledek.append(667)
		return vysledek
	except IndexError:
		print(picaxe)
		vysledek.append(668)
		return vysledek

def alignByte(intbajt):
	'''
	Vezme vstupni int hodnotu bajtu a prevede ji na retezec binarni reprezentace vstupniho bajtu z leva zarovnany nulami na celkovy pocet osmi znaku v retezci.
	'''
	return '0' * (8-len(str(bin(intbajt))[2:])) + str(bin(intbajt))[2:]
	

def temp12bit(MSbyte, LSbyte):
	'''
	Prevede dve vstupni int hodnoty bajtu na teplotu podle protokolu cidla DS18B20
	vysledek:
		float stupne celsia
	'''
	#print()
	#print('temp12bit():')
	#print('MSbyte:', MSbyte)
	#print('LSbyte:', LSbyte)
	x = alignByte(MSbyte) + alignByte(LSbyte)
	#print('x:', x)
	vysledek = 0
	p = 6
	for n in range(5,16):
		vysledek = vysledek + int(x[n])*2**p
		p = p - 1
	if x[4] == '1':
		vysledek = vysledek - 128
	#print('vysledek:', vysledek)
	return vysledek

def teplota(pe, prikaz):
	'''
	Ridi komunikaci
	Otevira a zavira serport
	Vystup: seznam dvou float teplot z dane adresy P
	'''
	cidlo = []
	try:
		ser = serial.Serial(PORT, 2400, timeout = 10)
	
		if sendData(pe,prikaz,ser):
			time.sleep(2)
			teplotyP1 = recieveData(4,ser)
	
			cidlo.append(temp12bit(teplotyP1[0], teplotyP1[1]))	
			cidlo.append(temp12bit(teplotyP1[2], teplotyP1[3]))
		else:
			print('Selhani vysilani')
			
		ser.close()
		return cidlo
	except serial.SerialException:
		print('Port nenalezen.')
		return False
	except IndexError:
		print('teplota() neobdrzela data')
		return False

tep = [[],[],[],[]]

for n in range(5):
	while True:
		cidlo1 = teplota('p001',84)
		if cidlo1:
			break
		
	while True:
		cidlo2 = teplota('p002',84)
		if cidlo2:
			break

	tep[0].append(cidlo1[0])
	tep[1].append(cidlo1[1])
	tep[2].append(cidlo2[0])
	tep[3].append(cidlo2[1])
	
print('teploty0:', tep[0])	
print('teploty1:', tep[1])
print('teploty2:', tep[2])
print('teploty3:', tep[3])
print()

lota = []

for m in range(len(tep)):
	tep[m] = sorted(tep[m])
	print('sorted:', tep[m])
	lota.append((sum(tep[m][1:4]))/3)

print('raw lota:', lota)

for o in range(len(lota)):
	lota[o] = round(lota[o],1)	
		
text = '{:<20}{:<10}{:<10}{:<10}{:<10}\n'.format(time.strftime('%d.%m.%Y %H:%M'),lota[0],lota[1],lota[2],lota[3])

csv_text = '{};{};{};{};{}\n'.format(time.strftime('%d.%m.%Y %H:%M'),lota[0],lota[1],lota[2],lota[3])

print(text)
	
f_dat = open(FILE,"a")
f_dat.write(text)
f_dat.close()
	
f_dat = open(CSV,"a")
f_dat.write(csv_text)
f_dat.close()
		
			
			

