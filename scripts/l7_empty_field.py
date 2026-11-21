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

from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT
for key in (KEY_SPAN,KEY_SKEW_ANGLE,KEY_CARRIAGEWAY_WIDTH):
    wd=dock._w(key); before=wd.text(); wd.clear(); n0=len(popups); wd.editingFinished.emit()
    print('EMPTY',key,'initial=',before,'BASIC default=',repr(BASIC_INPUT_DICT.get(key)),'-> text',repr(wd.text()),'dict',repr(w.input_dict.get(key)),'popups',len(popups)-n0, popups[-1] if len(popups)>n0 else '')
