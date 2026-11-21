"""L7 offscreen Qt: type tricky text into the real span/skew/carriageway widgets, read dict+popup count."""
import os,sys
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from PySide6.QtWidgets import QApplication, QLineEdit
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
app=QApplication([])
from osdagbridge.desktop.ui.docks import input_dock as ID
popups=[]
class FakeBox:
    def __init__(self,*a,**k): popups.append(k.get('text'))
    def exec(self): return 0
ID.CustomMessageBox=FakeBox
from osdagbridge.desktop.ui.template_page import CustomWindow
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.utils.common import KEY_SPAN, KEY_SKEW_ANGLE, KEY_CARRIAGEWAY_WIDTH
w=CustomWindow("T",PlateGirderBridge)
dock=w.input_dock
for key in (KEY_SPAN,KEY_SKEW_ANGLE,KEY_CARRIAGEWAY_WIDTH):
    wd=dock._w(key); print('WIDGET',key,type(wd).__name__, wd.validator().__class__.__name__ if isinstance(wd,QLineEdit) and wd.validator() else None)
    for typed in ("nan","inf","1e999","30,5","19.999","1e1","-0","  "):
        wd.setFocus(); wd.clear()
        QTest.keyClicks(wd,typed) if typed.isascii() else wd.setText(typed)
        n0=len(popups)
        wd.editingFinished.emit()
        print(f'{key[-12:]:>12} typed={typed!r:9} text={wd.text()!r:9} dict={w.input_dict.get(key)!r:10} popups+={len(popups)-n0}')
