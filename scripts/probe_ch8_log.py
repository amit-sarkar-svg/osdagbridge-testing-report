import sys
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports import chap8
tex=chap8.ch8_design_log(["INFO: UNIQUEMARKER123","WARNING: UNIQUEMARKER456","ERROR: UNIQUEMARKER789"],{})
print('CH8_LEN',len(tex),'marker_present',any(m in tex for m in ('UNIQUEMARKER123','UNIQUEMARKER456','UNIQUEMARKER789')))
print('CH8_TITLE',tex.strip().splitlines()[0][:60])
