; temperature reading,
; 12bit DS18B20
for b0 = 0 to 10 ; startup signalization
high C.0
pause 100
low C.0
pause 100
next b0
high C.4

start: ; main loop
serin C.3,T2400,("p001"),b1 ; wait for serial input calls device address
for b0 = 0 to 5 ; input confirmation
high C.0
pause 100
low C.0
pause 100
next b0
if b1 = 84 then goto teplot ; to measure both sensors
if b1 = 81 then goto tempC1 ; to measure sensor at C.1 input
if b1 = 82 then goto tempC2 ; to measure sensor at C.2 input
serout C.4,T2400,("p999XXXX") ; serial output when command not recognized
goto start

teplot: ; subprogram  for both sensors
readtemp12 C.1, w1 ; measure sensor at C.1
readtemp12 C.2, w2 ; measure sensor at C.2
serout C.4,T2400,("p999",b3,b2,b5,b4) ; serial output 4 bytes with 2 temperature values
goto start

tempC1: ; subprogram for sensor C.1
readtemp12 C.1, w1
serout C.4,T2400,("p999",b3,b2) ; 2 bytes output with 1 temperature value
goto start

tempC2: ; subprogram for sensor C.2
readtemp12 C.2, w1
serout C.4,T2400,("p999",b3,b2) ; 2 bytes output with 1 temperature value
goto start
