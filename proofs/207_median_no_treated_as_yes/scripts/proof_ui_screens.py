"""Offscreen screenshots of the real InputDock for #206 (empty skew) and #207 (empty carriageway, median No).
usage: proof_ui_screens.py <outdir>"""
import os,sys
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from PySide6.QtWidgets import QApplication, QComboBox
app=QApplication([])
from osdagbridge.desktop.ui.docks import input_dock as ID
popups=[]
class FakeBox:
    def __init__(self,*a,**k): popups.append(k.get('text'))
    def exec(self): return 0
ID.CustomMessageBox=FakeBox
from osdagbridge.desktop.ui.template_page import CustomWindow
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.utils.common import KEY_SPAN, KEY_SKEW_ANGLE, KEY_CARRIAGEWAY_WIDTH, KEY_INCLUDE_MEDIAN
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
w=CustomWindow("OsdagBridge (offscreen)",PlateGirderBridge); dock_size=(420,900)
dock=w.input_dock; dock.resize(*dock_size)
def grp():
    g=dock._w(KEY_SKEW_ANGLE)
    while g.parentWidget() is not None and g.parentWidget().height() < 260: g=g.parentWidget()
    return g.parentWidget() or g
def setv(key,text):
    wd=dock._w(key); wd.setText(text); wd.editingFinished.emit()
setv(KEY_SPAN,"30"); setv(KEY_CARRIAGEWAY_WIDTH,"10"); setv(KEY_SKEW_ANGLE,"5")
med=dock._w(KEY_INCLUDE_MEDIAN)
if isinstance(med,QComboBox): med.setCurrentText("No")
grp().grab().save(os.path.join(out,'01_before.png'))
print('BEFORE skew=%r cw=%r median=%r'%(w.input_dict.get(KEY_SKEW_ANGLE),w.input_dict.get(KEY_CARRIAGEWAY_WIDTH),w.input_dict.get(KEY_INCLUDE_MEDIAN)))
n=len(popups); wd=dock._w(KEY_SKEW_ANGLE); wd.clear(); wd.editingFinished.emit()
grp().grab().save(os.path.join(out,'02_after_clearing_skew.png'))
print('AFTER clearing skew: text=%r dict=%r popup=%r'%(wd.text(),w.input_dict.get(KEY_SKEW_ANGLE),popups[n:]))
n=len(popups); wd=dock._w(KEY_CARRIAGEWAY_WIDTH); wd.clear(); wd.editingFinished.emit()
grp().grab().save(os.path.join(out,'03_after_clearing_carriageway_median_no.png'))
print('AFTER clearing carriageway (median %r): text=%r dict=%r popup=%r'%(w.input_dict.get(KEY_INCLUDE_MEDIAN),wd.text(),w.input_dict.get(KEY_CARRIAGEWAY_WIDTH),popups[n:]))
