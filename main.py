#!/usr/bin/python3

import eDrive
import time

# create 4 objects of temperature
outside1 = eDrive.Temperature('p001', 81)
outside2 = eDrive.Temperature('p001', 82)
inside = eDrive.Temperature('p002', 81)
heat_water = eDrive.Temperature('p002', 82)

# make string of actuall time and temperature values
data = '{};{};{};{};{}\n'.format(time.strftime('%d.%m.%Y %H:%M'),outside1.measure(),outside2.measure(),inside.measure(),heat_water.measure())
print(data)

try: # writing data to output file
    with open(outside1.output, 'a', encoding='utf-8') as f:
        f.write(data)
except:
	print('Writing to file {} failed.'.format(outside1.output))
