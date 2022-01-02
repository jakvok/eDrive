#!/usr/bin/python3

import eDrive
import time

outside1 = eDrive.Temperature('p001', 81)
outside2 = eDrive.Temperature('p001', 82)
inside = eDrive.Temperature('p002', 81)
heat_water = eDrive.Temperature('p002', 82)

data = '{};{};{};{};{}\n'.format(time.strftime('%d.%m.%Y %H:%M'),outside1.measure(),outside2.measure(),inside.measure(),heat_water.measure())
print(data)

if outside1.test:
    file = outside1.test_output
else:
    file = outside1.output

try:
    with open(file, 'a', encoding='utf-8') as f:
        f.write(data)
except:
	print('Writing to file {} failed.'.format(file))
