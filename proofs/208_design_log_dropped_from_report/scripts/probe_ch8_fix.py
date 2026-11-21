import sys,inspect
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports import chap8
src=inspect.getsource(chap8.ch8_design_log)
old="    return _ch8_assumptions(is_custom)"
assert old in src
new=src.replace(old,"    log_tex = ('\\\\section{Design Log}\\n' + '\\n'.join(lines_tex) + '\\n') if lines_tex else ''\n    return _ch8_assumptions(is_custom) + log_tex")
ns=dict(vars(chap8)); exec(new,ns)
tex=ns['ch8_design_log'](["INFO: UNIQUEMARKER123","WARNING: UNIQUEMARKER456"],{})
print('FIXED marker_present',all(m in tex for m in ('UNIQUEMARKER123','UNIQUEMARKER456')))
