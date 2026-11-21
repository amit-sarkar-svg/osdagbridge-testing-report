#!/usr/bin/env python3
import sys, json
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
bv=BridgeInputValidator()

def rec(name,args):
    try:
        r=bv.validate_map_coordinates(*args) if name=='map' else bv.validate_custom_weather_data(*args)
        return ('ok', r)
    except Exception as e:
        return ('exc', f"{type(e).__name__}: {e}")

cases=[]
# map coords: (lat,lon)
map_cases=[
 ('90','0'),('-90','0'),('0','180'),('0','-180'),
 ('90.0001','0'),('-90.0001','0'),('0','180.0001'),('0','-180.0001'),
 ('77','28'),('28','77'), # swapped typical India lat/lon
 ('',''),('','77'),('28',''),(' ','77'),
 ('abc','77'),('28','abc'),('12.34.56','77'),('28,5','77'),
 ('40.7128','-74.0060'), # outside India
]
for a in map_cases:
    cases.append(('map',a,rec('map',a)))
# weather: wind, zone, max_temp, min_temp
w_cases=[
 ('50','II','45','20'), # baseline ok?
 ('0','II','45','20'),('-1','II','45','20'),('1000000','II','45','20'),
 ('50','Select Zone','45','20'),('50','UNKNOWN','45','20'),('50','','45','20'),
 ('50','II','20','45'), # max below min
 ('50','II','30','30'), # equal
 ('50','II','200','-100'),('50','II','60','-50'),
 ('','II','45','20'),('abc','II','45','20'),
 ('50','II','abc','20'),('50','II','45','abc'),
]
for a in w_cases:
    cases.append(('weather',a,rec('weather',a)))

flags=[]
for t,a,r in cases:
    if r[0]=='exc': flags.append((t,a,r))
    # check claims
print('G_SUMMARY cases=%d exceptions=%d' % (len(cases), len([c for c in cases if c[2][0]=='exc'])))
for t,a,r in cases[:30]:
    print(t,a,r)
open('evidence/logs/trackG_location_weather.json','w').write(json.dumps({'cases':[(t,a,r) for t,a,r in cases]}, default=str))
print('WROTE evidence/logs/trackG_location_weather.json')
