#!/usr/bin/python3

import eDrive

outside1 = eDrive.Temperature('p001', 81)
outside2 = eDrive.Temperature('p001', 82)
inside = eDrive.Temperature('p002', 81)
heat_water = eDrive.Temperature('p002', 82)

print('outside1:', outside1.measure())
print('outside2:', outside2.measure())
print('inside:', inside.measure())
print('heating:', heat_water.measure())