; cteni teploty,
; 12bit DS18B20
for b0 = 0 to 10
high C.0
pause 100
low C.0
pause 100
next b0
high C.4

start:
serin C.3,T2400,("p002"),b1
for b0 = 0 to 5
high C.0
pause 200
low C.0
pause 200
next b0
if b1 = 84 then goto teplot
serout C.4,T2400,("p999XXXX")
goto start

teplot:
readtemp12 C.1, w1
readtemp12 C.2, w2

serout C.4,T2400,("p999",b3,b2,b5,b4)
goto start