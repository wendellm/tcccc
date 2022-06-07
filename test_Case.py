import time
from ADBUiautomator import ADBUiautomator
import pytest
#from robot_test import test_Robot
device = ADBUiautomator("RQCT302JYQD")

class test:
    
    @pytest.fixture
    def closeAllapps():
        device.closeAllApps
        time.sleep(2)
        
    def test_Case00(


            closeAllapps):
        print('Start TESTE 01')
        device.KEYCODE_CALL()
        time.sleep(2)
    
        for i in range(4):
            device.click_element_by_resource_id('com.samsung.android.dialer:id/zero')
            time.sleep(2)
    
        numeros_digitados = device.checkElement("0000")
        teclado = numeros_digitados
    
        valor_esperado = True
        assert valor_esperado == teclado
    
        
    def test_SysDump_Case01():
        pyc
        print('Start TESTE 02')
        device.closeAllApps()
        device.KEYCODE_CALL()
        time.sleep(2)
    
        device.click_element_by_resource_id('com.samsung.android.dialer:id/star')
        time.sleep(1)
        device.click_element_by_resource_id('com.samsung.android.dialer:id/pound')
        time.sleep(1)
        for i in range(2):
            device.click_element_by_resource_id('com.samsung.android.dialer:id/nine')
            time.sleep(1)
        for i in range(2):
            device.click_element_by_resource_id('com.samsung.android.dialer:id/zero')
            time.sleep(1)
        device.click_element_by_resource_id('com.samsung.android.dialer:id/pound')
        time.sleep(1)
    
        check_activity_Log = device.get_current_activity()
        checkLog = "com.sec.android.app.servicemodeapp/.SysDump"
    
        assert checkLog in check_activity_Log
        