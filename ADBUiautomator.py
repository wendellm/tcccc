import subprocess
from lxml import etree
import time
import re
from subprocess import check_output
import os
from PIL import Image

import xml.etree.ElementTree as ET


class ADBUiautomator:
    def __init__(self, idDevice):
        self.idDevice = idDevice
        self.os_version = (
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "getprop ro.build.version.release",
                ]
            )
            .decode("ascii")
            .strip()
        )
        self.tree = None

    def getSize(self):
        result = subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "wm", "size"], stdout=subprocess.PIPE
        ).stdout.__str__()
        if "Override size" in result and "Physical size" in result:
            width, height = result.split("\\r\\n")[1], result.split("\\r\\n")[1]


            width = width[width.find(":") + 1 : len(width) - 1].split("x")[0]
            height = height[height.find(":") + 1 : len(height)].split("x")[1]

        else:
            width, height = (
                result[result.find(":") + 1 : len(result) - 1]
                .strip("\\n\\r ")
                .split("x")[0],
                result[result.find(":") + 1 : len(result) - 1]
                .strip("\\n\\r ")
                .split("x")[1],
            )

        return int(width), int(height)

    def getXMLDump(self):
        # Fazer dump da
        result = subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "uiautomator", "dump"],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")

        # Get File path and file name
        filePath = result[result.find(":") + 1 : len(result) - 1].strip("\n\r ")
        filePath[filePath.rfind("/") + 1 : len(filePath)]

        if not os.path.isdir("./temp/{self}.xml"):
            print("Criando PATH")
            os.makedirs("./temp/{self}.xml")

        # pull do arquivo gerado
        p = subprocess.Popen(
            "adb -s {deviceFull} pull {path} ./temp/{self}.xml".format(
                path=filePath,
                deviceFull=self.idDevice,
                self=self.idDevice.replace(":", "."),
            )
        )
        _, _ = p.communicate()

        # Carrega o XML da tela
        self.tree = etree.parse(
            "./temp/{self}.xml".format(self=self.idDevice.replace(":", "."))
        )
        return etree.tostring(self.tree)

    def checkElement(self, text):
        aux = self.getXMLDump()
        encoding = "utf-8"
        xml = aux.decode(encoding)
        return text in xml

    def checkElementWithDump(self, text, dump):
        encoding = "utf-8"
        xml = dump.decode(encoding)
        # print(type(xml))
        return text in xml

    def get_dump_decoded(self):
        # pode utilizar para realizar um check element de varios elementos so com 1 dump
        aux = self.getXMLDump()
        encoding = "utf-8"
        xml = aux.decode(encoding)
        return xml

    def is_download_apps_from_omc(self):
        self.open_omc_agent()
        aux = self.getXMLDump()
        encoding = "utf-8"
        xml = aux.decode(encoding)
        if "No apps" in xml:
            return False
        elif "Waiting" in xml or "Installing…" in xml or "will be downloaded" in xml:
            return True
        else:
            return False

    def open_omc_agent(self):
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.samsung.android.app.omcagent/.rna.ui.RnaManagerActivity".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

    def calcItemPosition(self, item):
        c1, c2 = item.items()[-1][-1].split("][")[0].replace("[", ""), item.items()[-1][
            -1
        ].split("][")[1].replace("]", "")
        x = ((int(c1.split(",")[0]) + int(c2.split(",")[0])) / 2).__round__()
        y = ((int(c1.split(",")[1]) + int(c2.split(",")[1])) / 2).__round__()
        return x, y

    def swipe(self, x1, y1, x2, y2, t):
        p = subprocess.Popen(
            "adb -s {self} shell input swipe {x1} {y1} {x2} {y2} {t}".format(
                self=self.idDevice, x1=x1, y1=y1, x2=x2, y2=y2, t=t
            )
        )
        _, _ = p.communicate()

    def swipe_up(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) / 2,
            int(height) / 2,
            int(width) / 2,
            (int(height) / 2) * move,
            500,
        )

    def swipe_up_tablet(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) / 5,
            int(height) / 2,
            int(width) / 5,
            (int(height) / 2) * move,
            500,
        )

    def swipe_up_APN(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) * 0.90,
            int(height) / 2,
            int(width) * 0.90,
            (int(height) / 2) * move,
            500,
        )

    def swipe_down(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) * 0.97,
            (int(height) / 2) * move,
            int(width) * 0.97,
            int(height) / 2,
            500,
        )

    def swipe_right(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) * 0.97,
            int(height) / 2,
            (int(height) / 2) * move,
            int(width) * 0.97,
            500,
        )

    def swipe_left(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            (int(height) / 2) * move,
            int(width) * 0.97,
            int(width) * 0.97,
            int(height) / 2,
            500,
        )

    def swipe_edge(self, move=1):
        width, height = self.getSize()
        self.swipe(
            (int(width) - 10), int(height) / 4, int(width) / 2, int(height) / 4, 500
        )
        time.sleep(1)

    def swipe_touch_protection(self):
        x, y = self.getElementPositionByXPath(
            "//*[@resource-id='com.android.systemui:id/locker_img_view']"
        )
        self.swipe(x, y, x * 2, y, 500)
        time.sleep(1)

    def getElementPositionByText(self, text):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@text='{TEXT}']".format(TEXT=text))[0]
        return self.calcItemPosition(item)

    def move_file_to(self, name, path):
        subprocess.Popen(
            'adb -s {self} pull /sdcard/{name} "{path}'.format(
                self=self.idDevice, name=name, path=path
            )
        )

    def getElementPositionListByText(self, text):
        self.getXMLDump()
        elementlist = self.tree.xpath("//node[@text='{TEXT}']".format(TEXT=text))
        return elementlist

    def getElementPositionByContentDesc(self, text):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@content-desc='{TEXT}']".format(TEXT=text))[0]
        return self.calcItemPosition(item)

    def getElementListByContentDesc(self, text):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@content-desc='{TEXT}']".format(TEXT=text))
        return item

    def getElementPositionByXPath(self, xpath):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath(xpath)[0]
        return self.calcItemPosition(item)

    def getElementPositionByResourceId(self, text):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@resource-id='{TEXT}']".format(TEXT=text))[0]
        return self.calcItemPosition(item)

    def getElementListByResourceId(self, text):
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@resource-id='{TEXT}']".format(TEXT=text))
        return item

    def getElementByText(self, text: object) -> object:
        self.getXMLDump()
        # Filtrar o XML para pegar o texto do componente da tela
        item = self.tree.xpath("//node[@text='{TEXT}']".format(TEXT=text))[0]
        return item

    def write_sysmocom(self, mccmnc, spc):
        self.openSimEditor()

        self.click_element_by_resource_id("com.sec.SimEditor:id/Btn_Read")

        self.wait(5)

        msin_element = self.getElementListByResourceId(
            "com.sec.SimEditor:id/EditText_MSIN"
        )
        msin = msin_element[0].get("text")

        iccId_element = self.getElementListByResourceId(
            "com.sec.SimEditor:id/EditText_ICCID"
        )
        iccId = iccId_element[0].get("text")

        self.closeAllApps()

        # gerar txt para gravação da APN
        file = open("SimEditor_Script.txt", "w")
        subset = "(HEX)FF"
        spname = "null"
        gid2 = "(HEX)null"
        password = "77777777"

        IMSI = mccmnc + msin
        len_imsi = len(IMSI)
        if len_imsi > 15:
            param = len_imsi - 15
            msin = msin[param:]

        kk = """mccmnc: {}\nmsin: {}\nsubset(gid1): {}\nspname: {}\nspcode: {}\ngid2: {}\niccid: {}\npassword: {}""".format(
            mccmnc, msin, subset, spname, spc, gid2, iccId, password
        )
        file.write(kk)
        file.close()

        Send_infos = (
            f"adb -s {self.idDevice} shell am broadcast -a omc_plugin_client.SimEditBroadcastReceive"
            f".SEND_BROAD_CAST -n "
            f"com.sec.SimEditor/com.sec.SimEditor.omc_plugin_client.SimEditBroadcastReceiver "
        )
        Send_infos = Send_infos.split()
        cp_reset = (
            f"adb -s {self.idDevice} shell am broadcast -a com.sec.SimEditor.activity.CPReset"
            f".ACTION_EVENT_CP_RESET_REQ "
        )
        cp_reset = cp_reset.split()

        # ,cwd=directory) #arquivo está na raiz do self
        p = subprocess.Popen(
            ["adb", "-s", self.idDevice, "push", "SimEditor_Script.txt", "/sdcard/"]
        )
        p.wait()
        self.wait(1)
        p = subprocess.Popen(Send_infos)  # arquivo está na raiz do self
        p.wait()
        self.wait(1)
        resp = subprocess.Popen(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -a android.intent.action.MAIN -n com.sec.SimEditor/.activity.MainActivity",
            ]
        )
        resp.wait()
        p = subprocess.Popen(cp_reset)
        p.wait()

        # CP Reset log delete
        p = subprocess.Popen(
            ["adb", "-s", self.idDevice, "shell", "rm -rf sdcard/log"]
        )
        p.wait()

    def getScreenShot(self, name, path):
        # remove qualquer espaço e caracteres especiais
        name = name.replace(" ", "_")
        time.sleep(1)

        p = subprocess.Popen(
            "adb -s {self} shell screencap -p /sdcard/{name}".format(
                self=self.idDevice, name=name
            )
        )
        _, _ = p.communicate()

        time.sleep(1)

        p = subprocess.Popen(
            'adb -s {self} pull /sdcard/{name} "{path}\\{name}"'.format(
                self=self.idDevice, name=name, path=path
            )
        )
        _, _ = p.communicate()

        time.sleep(1)

        # reduz a qualidade da imagem e salvar espaço de armazenamento
        img = Image.open(path + "\\" + name)
        (width, height) = (int(img.width // 2.5), int(img.height // 2.5))
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(path + "\\" + name, optimize=True, quality=70)

    def openDeviceInfo(self):
        p = subprocess.Popen(
            "adb -s {self} shell am start -a android.settings.DEVICE_INFO_SETTINGS".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

        time.sleep(1)

    def enableWifi(self):
        subprocess.Popen(
            "adb -s {self} shell svc wifi enable".format(self=self.idDevice)
        )

    def enableData(self):
        subprocess.Popen(
            "adb -s {self} shell svc data enable".format(self=self.idDevice)
        )

    def disableWifi(self):
        subprocess.Popen(
            "adb -s {self} shell svc wifi disable".format(self=self.idDevice)
        )

    def disableData(self):
        subprocess.Popen(
            "adb -s {self} shell svc data disable".format(self=self.idDevice)
        )

    def openDeviceLockscreenHomescreen(self):
        # "adb -s %idDevice% shell am start -n com.samsung.android.app.dressroom/.presentation.settings.WallpaperSettingActivity"
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.samsung.android.app.dressroom/.presentation.settings.WallpaperSettingActivity".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

        time.sleep(1)

    def wait(self, second):
        time.sleep(second)

    def open_csc_verifier(self):
        if self.os_version in ("10", "11", "12"):
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "am start -a android.intent.action.MAIN -n "
                    "com.samsung.sec.android.application.csc/com.samsung.sec.android.application.csc.ui"
                    ".CscVerifierActivity",
                ]
            ).decode("ascii")
        elif self.os_version == "9":
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "am start -a android.intent.action.MAIN -n "
                    "com.samsung.sec.android.application.csc/.utils.CscVerifierActivity",
                ]
            ).decode("ascii")
        else:
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "am start -a android.intent.action.MAIN -n "
                    "com.samsung.sec.android.application.csc/.CscVerifierActivity",
                ]
            ).decode("ascii")

    def openDialer(self):
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.samsung.android.dialer/.DialtactsActivity".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

        if self.checkElement("Not now"):
            self.click_element_by_text("Not now")

    def install_Sim_Editor(self):

        try:
            check_output(
                ["adb", "-s", self.idDevice, "install", "./files/SIMEditor_USER.apk"]
            )
            print("SIM Editor instalado - USER")
            time.sleep(1)
        except:
            pass
        try:

            check_output(
                ["adb", "-s", self.idDevice, "install", "./files/SIMEditor_RIZE.apk"]
            )
            print("SIM Editor instalado - RIZE")
            time.sleep(1)
        except:
            pass
        try:
            check_output(
                ["adb", "-s", self.idDevice, "install", "./files/SIMEditor_ENG.apk"]
            )
            print("SIM Editor instalado - ENG")
            time.sleep(1)
        except:
            pass

    def getElementList_title_summary_linearLayout(self):

        self.getXMLDump()

        # Filtrar o XML para pegar o texto do componente da tela

        titleList = self.tree.xpath(
            "//node[@resource-id='{TEXT}']".format(TEXT="android:id/title")
        )

        summaryList = self.tree.xpath(
            "//node[@resource-id='{TEXT}']".format(TEXT="android:id/summary")
        )

        linearLayoutList = self.tree.xpath(
            "//node[@class='{TEXT}']".format(TEXT="android.widget.LinearLayout")
        )

        return titleList, summaryList, linearLayoutList

    def getElementList_RadioButton(self):

        self.getXMLDump()

        # Filtrar o XML para pegar o texto do componente da tela

        linearLayoutList = self.tree.xpath(
            "//node[@class='{TEXT}']".format(TEXT="android.widget.RadioButton")
        )

        return linearLayoutList

    def openSimEditor(self):

        re = check_output(
            ["adb", "-s", self.idDevice, "shell", "pm list packages com.sec.SimEditor"]
        ).decode("ascii")
        if not "SimEditor" in re:
            self.install_Sim_Editor()

        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -a android.intent.action.MAIN -n com.sec.SimEditor/.activity.MainActivity",
            ]
        ).decode("ascii")

        time.sleep(2)

        if self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        ):
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        time.sleep(1)
        if self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        ):
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )

        sim1 = self.getElementListByResourceId("com.sec.SimEditor:id/radio_sim1")[
            0
        ].get("checked")

        try:
            sim2 = self.getElementListByResourceId("com.sec.SimEditor:id/radio_sim2")[
                0
            ].get("checked")
        except:
            sim2 = "false"

        if sim1 == "false" and sim2 == "false":

            return False

        # elif sim1.get("checked") == "true" or sim2.get("checked") == "true":
        elif sim1 == "true" or sim2 == "true":
            return True

    def is_simcard_rewriteble(self, resource_id):
        self.click_element_by_resource_id(resource_id)

        self.click_element_by_text("READ")

        self.getElementListByResourceId("com.sec.SimEditor:id/EditText_PLMNwAcT")[0]

    def uninstall_Sim_editor(self):

        p = subprocess.Popen(
            "adb -s {self} uninstall com.sec.SimEditor".format(self=self.idDevice)
        )

        _, _ = p.communicate()

    def openDefaultApps(self):
        # Others
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.google.android.permissioncontroller/com.android.packageinstaller.role.ui.DefaultAppListActivity".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

        # Android 11
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.google.android.permissioncontroller/com.android.permissioncontroller.role.ui.DefaultAppListActivity".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

    def openEdgeSettings(self):
        p = subprocess.Popen(
            "adb -s {self} shell am start -n com.samsung.android.app.appsedge/com.samsung.android.app.appsedge.settings.AppsEdgeSettings".format(
                self=self.idDevice
            )
        )

        _, _ = p.communicate()

    def getDeviceLanguage(self):
        p = subprocess.Popen(
            "adb -s {self} shell getprop persist.sys.locale".format(self=self.idDevice),
            stdout=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        stdout.decode("utf-8")
        return stdout.decode("utf-8").replace("\r\n", "")

    def click_element_by_position(self, positions):
        p = subprocess.Popen(
            "adb -s {self} shell input tap {x} {y}".format(
                x=positions[0], y=positions[1], self=self.idDevice
            )
        )
        _, _ = p.communicate()

    def click_element_by_text(self, text):

        x, y = self.getElementPositionByText(text)
        p = subprocess.Popen(
            "adb -s {self} shell input tap {x} {y}".format(x=x, y=y, self=self.idDevice)
        )
        _, _ = p.communicate()

    def click_element_by_content_desc(self, text):
        x, y = self.getElementPositionByContentDesc(text)
        p = subprocess.Popen(
            "adb -s {self} shell input tap {x} {y}".format(x=x, y=y, self=self.idDevice)
        )
        _, _ = p.communicate()

    def click_element_by_xpath(self, xpath):
        x, y = self.getElementPositionByXPath(xpath)
        p = subprocess.Popen(
            "adb -s {self} shell input tap {x} {y}".format(x=x, y=y, self=self.idDevice)
        )
        _, _ = p.communicate()

    def click_element_by_resource_id(self, xpath):
        x, y = self.getElementPositionByResourceId(xpath)
        p = subprocess.Popen(
            "adb -s {self} shell input tap {x} {y}".format(x=x, y=y, self=self.idDevice)
        )
        _, _ = p.communicate()

    def long_press_by_resource_id(self, text):
        x, y = self.getElementPositionByResourceId(text=text)
        self.swipe(x, y, x, y, 1000)

    def long_press_by_text(self, text):
        x, y = self.getElementPositionByText(text=text)
        self.swipe(x, y, x, y, 1000)

    def long_press_by_position(self, position):
        x = position
        y = x
        self.swipe(x, y, x, y, 1000)

    def long_press_add_home(self, position_x, position_y):
        x = position_x
        y = position_y
        self.swipe(x, y, x, y, 3000)

    def press_dial_button(self):

        self.click_element_by_resource_id("com.samsung.android.dialer:id/dialButton")

    def press_end_call(self):
        self.click_element_by_resource_id(
            "com.samsung.android.incallui:id/voice_disconnect_button"
        )

    def unlock_device(self):

        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent 82"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def openLanguageSettings(self):
        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -a android.settings.LOCALE_SETTINGS",
            ]
        )

    def KEYCODE_HOME(self):
        print(self.idDevice)
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_HOME"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def KEYCODE_BACK(self):
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_BACK"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def KEYCODE_APP_SWITCH(self):
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_APP_SWITCH"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def KEYCODE_MENU(self):
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_MENU"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def KEYCODE_DPAD_DOWN(self):
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent 20"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def KEYCODE_ENTER(self):
        subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "input keyevent 66"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def openSBrowser(self):
        subprocess.run(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -n com.sec.android.app.sbrowser/com.sec.android.app.sbrowser.SBrowserMainActivity",
            ],
            stdout=subprocess.PIPE,
        ).stdout.__str__()
        time.sleep(1)

        if self.checkElement(
            "com.sec.android.app.sbrowser:id/guided_tour_view_message"
        ):
            self.swipe_up()

    def openChrome(self):
        subprocess.run(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -n com.android.chrome/com.google.android.apps.chrome.Main",
            ],
            stdout=subprocess.PIPE,
        ).stdout.__str__()
        time.sleep(1)

    def inputText(self, text):
        check_output(
            ["adb", "-s", self.idDevice, "shell", "input text {text}".format(text=text)]
        ).decode("ascii")

    def removeKeyString(self):
        p = subprocess.Popen(
            "adb -s {self} uninstall com.sec.keystringscreen".format(self=self.idDevice)
        )
        _, _ = p.communicate()

    def long_press_atHScreen(self):
        # adb shell input touchscreen swipe 170 187 170 187 2000
        subprocess.run(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "input touchscreen swipe 170 187 170 187 2000",
            ],
            stdout=subprocess.PIPE,
        ).stdout.__str__()
        time.sleep(1)

    def openDeviceSettings(self):
        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -a android.settings.SETTINGS",
            ]
        )

    def openWirelessSettings(self):
        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -a android.settings.WIRELESS_SETTINGS",
            ]
        )

    def open_app_by_package(self, package):

        check_output(["adb", "-s", self.idDevice, "shell", "monkey -p", package, "1"])

        self.wait(1)

    def closeAllApps(self):
        try:
            botao_fechar = ""
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_APP_SWITCH"]
            )
            self.check_tip_popup()
            if self.os_version == "10":
                botao_fechar = "com.sec.android.app.launcher:id/clear_all"
            elif self.os_version == "11" or self.os_version == "12":
                botao_fechar = "com.sec.android.app.launcher:id/clear_all_button"

            if self.checkElement(botao_fechar):
                print("APPS FECHADOS")
                self.click_element_by_resource_id(botao_fechar)
                self.wait(1)
            else:
                print("NÃO HÁ APPS ABERTOS")
                self.KEYCODE_HOME()
        except:
            self.go_home()

    def createNewContact(self):
        self.KEYCODE_HOME()
        self.swipe_up()
        # self.click_element_by_text('Contacts')
        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -n com.samsung.android.app.contacts/com.samsung.android.contacts.contactslist.PeopleActivity",
            ]
        )
        self.click_element_by_content_desc("Create contact")
        time.sleep(2)
        if self.checkElement("com.samsung.android.app.contacts:id/alertTitle"):
            # resp = check_output(["adb", "-s", self.idDevice, "shell", "input text SELBOT"]).decode('ascii')
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent 66"]
            ).decode("ascii")
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent 61"]
            ).decode("ascii")
            # resp = check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 61"]).decode('ascii')
            # resp = check_output(["adb", "-s", self.idDevice, "shell", "input text 9281238699"]).decode('ascii')
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent 66"]
            ).decode("ascii")
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent 61"]
            ).decode("ascii")
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent 66"]
            ).decode("ascii")
            # self.click_element_by_text('Save')
            # resp = check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 4"]).decode('ascii')
        check_output(["adb", "-s", self.idDevice, "shell", "input text SELBOT"]).decode(
            "ascii"
        )
        check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 61"]).decode(
            "ascii"
        )
        check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 66"]).decode(
            "ascii"
        )
        check_output(
            ["adb", "-s", self.idDevice, "shell", "input text 92981238699"]
        ).decode("ascii")
        self.click_element_by_text("Save")
        check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 4"]).decode(
            "ascii"
        )

    def check_tip_popup(self):
        try:
            self.click_element_by_resource_id("android:id/sem_tip_popup_message")
        except:
            pass

    def moveAppTrayToFirstScreen(self):
        before = self.getXMLDump()
        after = None
        while before != after:
            self.swipe_left()
            after = self.getXMLDump()
            if after != before:
                before = after
                after = None
            else:
                return True

    def set_Chrome(self):
        self.wait(1)
        if self.checkElement("Allow Chrome to send you notifications"):
            self.click_element_by_text("Allow")
        try:
            self.click_element_by_text("Accept & continue")
        except:
            pass

        try:
            self.click_element_by_text("No thanks")
        except:
            pass

        try:
            self.click_element_by_text("Next")
            self.click_element_by_text("No thanks")
        except:
            print("Chrome já configurado")

    def set_Sbrowser(self):

        # Wait until all pop-ups are displayed
        self.openSBrowser()
        self.wait(5);

        if self.checkElement("Update Samsung Internet?"):
            self.click_element_by_text("Cancel")

        if self.os_version in ["12", "11", "10"]:
            aux = self.getXMLDump()
            encoding = "utf-8"
            dump = aux.decode(encoding)
            if (
                "Welcome to" in dump
                or "Bienvenido a" in dump
                or "Bem-vindo a" in dump
                or "com.sec.android.app.sbrowser:id/help_intro_legal_title" in dump
            ):
                self.swipe_up()
                self.click_element_by_resource_id(
                    "com.sec.android.app.sbrowser:id/help_intro_legal_optional_checkbox"
                )
                self.click_element_by_resource_id(
                    "com.sec.android.app.sbrowser:id/help_intro_legal_agree_button"
                )

        # em casos o sbrowser não seja default
        if self.checkElement("Set Samsung Internet as default browser?"):
            self.click_element_by_text("Not now")

        # if adicionado para assegurar realmente que o pop não irá aparecer na hora de clicar nos botão,
        # as vezes mesmo configurando o browser, o pop up aparece quando for executar o segundo teste que depende do
        # sbrowser
        if self.checkElement("Update Samsung Internet?"):
            self.click_element_by_text("Cancel")

    def screenrecord(self, seconds, name, path):
        time.sleep(1)
        p = subprocess.Popen(
            "adb -s {self} shell screenrecord --time-limit={seconds} /sdcard/{name}.mp4".format(
                self=self.idDevice, seconds=seconds, name=name
            )
        )
        _, _ = p.communicate()
        time.sleep(1)
        p = subprocess.Popen(
            "adb -s {self} pull /sdcard/{name}.mp4 {path}\\{name}.mp4".format(
                self=self.idDevice, name=name, path=path
            )
        )
        _, _ = p.communicate()
        time.sleep(1)

    def get_app_version_by_package(self, package):
        version_name = check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                f"dumpsys package {package} | grep versionName",
            ],
            encoding="UTF-8",
        )
        return version_name.strip()

    def checkPermissions_SBrowser(self):
        self.wait(3)
        if (
            self.os_version == "12"
            or self.os_version == "11"
            or self.os_version == "10"
        ):
            checkUpdateSamsungInternet = self.checkElement("Update Samsung Internet?")
            if checkUpdateSamsungInternet:
                self.click_element_by_resource_id(
                    "android:id/button3"
                )  # Se aparecer o o popup de att, clicar em cancelar
            self.wait(1)
            # # Clicar em "more" e depois clicar em "Continue" por isso que precisa de duas checagens pois os botoes
            # tem o mesmo ID
            checkLegalAgreeButton = self.checkElement(
                "com.sec.android.app.sbrowser:id/help_intro_legal_agree_button"
            )
            if checkLegalAgreeButton:
                self.click_element_by_resource_id(
                    "com.sec.android.app.sbrowser:id/help_intro_legal_agree_button"
                )
            self.wait(1)
            checkLegalAgreeButton = self.checkElement(
                "com.sec.android.app.sbrowser:id/help_intro_legal_agree_button"
            )
            if checkLegalAgreeButton:
                self.click_element_by_resource_id(
                    "com.sec.android.app.sbrowser:id/help_intro_legal_agree_button"
                )
            ## Check update samsung internet
            self.wait(1)
            check_Update = self.checkElement("android:id/button3")
            if check_Update:
                self.click_element_by_resource_id("android:id/button3")
            self.wait(1)
            check_defaultApp = self.checkElement(
                "Set Samsung Internet as default browser?"
            )
            if check_defaultApp:
                self.click_element_by_resource_id("android:id/button2")

        # self.closeAllApps()

    def check_permissions_googleChrome(self):
        check_acceptANDcontinue = self.checkElement(
            "com.android.chrome:id/terms_accept"
        )
        if check_acceptANDcontinue:
            self.click_element_by_resource_id("com.android.chrome:id/terms_accept")
        check_accept = self.checkElement("com.android.chrome:id/next_button")
        if check_accept:
            self.click_element_by_resource_id("com.android.chrome:id/next_button")
        check_NoThanks = self.checkElement("com.android.chrome:id/negative_button")
        if check_NoThanks:
            self.click_element_by_resource_id("com.android.chrome:id/negative_button")
        checkDontAllow = self.checkElement("android:id/button2")
        if checkDontAllow:
            self.click_element_by_resource_id("android:id/button2")

    def setAutomaticSMS(self):
        self.click_element_by_text("Settings")
        self.click_element_by_text("More settings")
        self.click_element_by_text("Text messages")
        self.click_element_by_text("Input mode")
        self.click_element_by_text("Automatic")

    def identify_SIM_VIVO(self, num):
        samsungApp_package = "com.samsung.android.messaging"
        androidMessage_package = "com.google.android.apps.messaging"
        check_MessageApp = self.checkElement("Messages")
        if check_MessageApp:
            self.click_element_by_text("Messages")
        else:
            return "Aplicativo de mensagem não encontrado"

        # ------ Detectar se Samsung App ou Androir --------- #
        # adb shell "dumpsys activity activities | grep mResumedActivity"
        check_MessageApp = check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "dumpsys activity activities | grep mResumedActivity",
            ]
        )  # achar tela atual
        check_MessageApp = check_MessageApp.decode("utf-8").strip()
        checkIfSamsungApp = samsungApp_package in check_MessageApp
        # desabilitar rotação automática do device
        p = check_output(
            [
                "adb",
                "-s",
                self.getDeviceId(),
                "shell",
                "settings put system accelerometer_rotation 0",
            ]
        )

        if checkIfSamsungApp:
            self.messages_permissions()
            self.wait(1)
            p = subprocess.Popen(
                ["adb", "-s", self.getDeviceId(), "shell", "input keyevent 82"]
            )  # Abrir menu do aplicativo
            self.wait(1)
            self.setAutomaticSMS()
            self.wait(1)
            self.closeAllApps()
            self.click_element_by_text("Messages")
            self.wait(1)
            # clicar no botão para escrever nova mensagem
            self.click_element_by_resource_id("com.samsung.android.messaging:id/fab")
            resp = check_output(
                ["adb", "-s", self.getDeviceId(), "shell", f'input text "8300"']
            )  # MANDA SMS PARA SI
            resp = check_output(
                ["adb", "-s", self.getDeviceId(), "shell", "input keyevent 61"]
            )  # ENTER
            self.click_element_by_resource_id(
                "com.samsung.android.messaging:id/message_edit_text"
            )
            self.wait(2)
            resp = check_output(
                ["adb", "-s", self.getDeviceId(), "shell", f'input text "."']
            )
            self.wait(1)
            # check send_button
            checkSendButton2 = self.checkElement(
                "com.samsung.android.messaging:id/send_button2"
            )
            checkSendButton1 = self.checkElement(
                "com.samsung.android.messaging:id/send_button1"
            )
            checkSendButton = self.checkElement(
                "com.samsung.android.messaging:id/send_button"
            )
            if checkSendButton2:
                self.click_element_by_resource_id(
                    "com.samsung.android.messaging:id/send_button2"
                )
            elif checkSendButton1:
                self.click_element_by_resource_id(
                    "com.samsung.android.messaging:id/send_button1"
                )
            elif checkSendButton:
                self.click_element_by_resource_id(
                    "com.samsung.android.messaging:id/send_button"
                )

        elif androidMessage_package:
            # Help Improve Messages dump
            HelpImproveMessages_dump = self.getXMLDump()
            checkHelpImproveMessages_popUp = self.checkElementWithDump(
                "Help improve Messages", HelpImproveMessages_dump
            )
            checkGotIt_button = self.checkElementWithDump(
                "com.google.android.apps.messaging:id/federated_learning_popup_positive_button",
                HelpImproveMessages_dump,
            )
            if checkHelpImproveMessages_popUp:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/federated_learning_popup_positive_button"
                )

            # Set default SMS App
            checkSetDefaulSMSapp = self.checkElementWithDump(
                "com.google.android.apps.messaging:id/set_as_default_button",
                HelpImproveMessages_dump,
            )
            if checkSetDefaulSMSapp:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/set_as_default_button"
                )

            # Set_Messages_as_your_default_SMS_app_dump = self.getXMLDump()
            RadioButton_list = self.getElementList_RadioButton()
            for RadioButton in RadioButton_list:
                checkIfChecked = RadioButton.get("checked")
                if checkIfChecked == "false":
                    positions_to_click = self.calcItemPosition(RadioButton)
                    self.click_element_by_position(positions_to_click)
                    self.wait(1)
                    # click Set as default
                    self.click_element_by_resource_id("android:id/button1")

            chatFeaures_dump = self.getXMLDump()
            check_chatFeatures = self.checkElementWithDump(
                "com.google.android.apps.messaging:id/conversation_list_google_tos_popup_negative_button",
                chatFeaures_dump,
            )
            if check_chatFeatures:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/conversation_list_google_tos_popup_negative_button"
                )

            self.wait(6)
            if self.checkElement(
                "com.google.android.apps.messaging:id/start_new_conversation_button_v2"
            ):
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/start_new_conversation_button_v2"
                )
            else:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/start_chat_fab"
                )
            self.wait(1)
            resp = check_output(
                ["adb", "-s", self.getDeviceId(), "shell", f'input text "8300"']
            )  # MANDA SMS PARA SI
            self.wait(1)
            self.KEYCODE_ENTER()
            self.wait(1)
            self.click_element_by_resource_id(
                "com.google.android.apps.messaging:id/compose_message_text"
            )
            self.wait(2)
            resp = check_output(
                ["adb", "-s", self.getDeviceId(), "shell", f'input text "."']
            )
            # enviar mensagem
            check_sendButton = self.checkElement(
                "com.google.android.apps.messaging:id/send_message_button_icon"
            )
            if check_sendButton:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/send_message_button_icon"
                )

        self.wait(15)
        # resp = check_output(["adb", "-s", d_url, "shell", 'input keyevent 19'])  # KEYCODE_DPAD_UP
        xml_dump = str(self.getXMLDump())
        print(type(xml_dump))
        index = xml_dump.find("(92)")
        print(index)
        numero_bruto = xml_dump[index : index + 15]
        print(numero_bruto)
        numero = (
            numero_bruto.replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )
        print(numero)
        numero = "+55" + numero
        print(numero)

        try:
            # Abrir menu do aplicativo
            p = subprocess.Popen(
                ["adb", "-s", self.getDeviceId(), "shell", "input keyevent 82"]
            )
            check_DeleteMessages = self.checkElement("Delete messages")
            check_Delete = self.checkElement("Delete")
            if check_DeleteMessages:
                self.click_element_by_text("Delete messages")
            elif check_Delete:
                self.click_element_by_text("Delete")
            if self.checkElement(
                "com.samsung.android.messaging:id/bubble_all_select_checkbox"
            ):
                self.click_element_by_resource_id(
                    "com.samsung.android.messaging:id/bubble_all_select_checkbox"
                )
                self.click_element_by_resource_id(
                    "com.samsung.android.messaging:id/delete"
                )
                self.click_element_by_resource_id("android:id/button1")
            elif self.checkElement("android:id/button1"):
                self.click_element_by_resource_id("android:id/button1")
        except:
            print("Não foi possível deletar as mensagens")

        return numero

    def call_emergency(self, num, pathToSave):
        d_url = self.idDevice
        # Call to emergency numbers 112 and 190
        check_output(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                f"am start -a android.intent.action.CALL -d tel:112",
            ]
        )
        time.sleep(2)
        self.checar_e_pressionar_dialer(num)
        time.sleep(5)
        self.getScreenShot(f"T68_CallLogInfo_112_{num}.png", pathToSave)
        self.getScreenShot(f"T107_CallLogInfo_112_{num}.png", pathToSave)
        # check_output(["adb", "-s", d_url, "shell",f'input keyevent KEYCODE_ENDCALL'])
        try:
            self.click_element_by_resource_id(
                "com.samsung.android.incallui:id/disconnect_button"
            )
        except:
            try:
                self.click_element_by_resource_id(
                    "com.samsung.android.incallui:id/voice_disconnect_button"
                )
            except:
                pass
        time.sleep(5)
        check_output(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                f"am start -a android.intent.action.CALL -d tel:190",
            ]
        )
        time.sleep(1)
        self.checar_e_pressionar_dialer(num)
        time.sleep(5)
        self.getScreenShot(f"T68_CallLogInfo_190_{num}.png", pathToSave)
        self.getScreenShot(f"T107_CallLogInfo_190_{num}.png", pathToSave)
        # check_output(["adb", "-s", d_url, "shell",f'input keyevent KEYCODE_ENDCALL'])
        try:
            self.click_element_by_resource_id(
                "com.samsung.android.incallui:id/disconnect_button"
            )
        except:
            self.click_element_by_resource_id(
                "com.samsung.android.incallui:id/voice_disconnect_button"
            )
        time.sleep(2)

        self.closeAllApps()

    def checar_e_pressionar_dialer(self, num):
        time.sleep(2)
        check_DialSS = self.checkElement("com.samsung.android.dialer:id/dialpad_keypad_only")
        check_dial = self.checkElement(f"com.samsung.android.dialer:id/dialButton{num}")
        if check_dial:
            self.click_element_by_resource_id(
                f"com.samsung.android.dialer:id/dialButton{num}"
            )
        elif check_DialSS:
            self.click_element_by_resource_id(
                "com.samsung.android.dialer:id/dialButton"
            )

    def messages_permissions(self):
        d_url = self.idDevice
        checkAllow = self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        )  # Permissão 1
        if checkAllow:
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        checkAllow = self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        )  # Permissão 2
        if checkAllow:
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        checkAllow = self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        )  # Permisão 3
        if checkAllow:
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        checkAllow = self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        )  # Permisão 4
        if checkAllow:
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        checkAllow = self.checkElement(
            "com.android.permissioncontroller:id/permission_allow_button"
        )  # Permisão 5
        if checkAllow:
            self.click_element_by_resource_id(
                "com.android.permissioncontroller:id/permission_allow_button"
            )
        checkDefault = self.checkElement("com.samsung.android.messaging:id/change_app")
        if checkDefault:
            self.click_element_by_resource_id(
                "com.samsung.android.messaging:id/change_app"
            )
            # dpad down
            p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 20"])
            p.wait()
            p = subprocess.Popen(
                ["adb", "-s", d_url, "shell", "input keyevent 20"]
            )  # dpad down
            p.wait()
            subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 66"])
        checkSetAsDefault = self.checkElement("android:id/button1")
        if checkSetAsDefault:
            self.click_element_by_resource_id("android:id/button1")

    def s_messages_permissions(self):  # Funciona em Android GO
        d_url = self.idDevice
        pos_palette = False
        while self.checkElement("Allow"):
            if self.checkElement(
                "com.android.permissioncontroller:id/permission_allow_foreground_only_button"
            ):
                self.click_element_by_resource_id(
                    "com.android.permissioncontroller:id/permission_allow_foreground_only_button"
                )
            elif self.checkElement(
                "com.android.permissioncontroller:id/permission_allow_button"
            ):
                self.click_element_by_resource_id(
                    "com.android.permissioncontroller:id/permission_allow_button"
                )

        checkDefault = self.checkElement("com.samsung.android.messaging:id/change_app")
        if checkDefault:
            self.click_element_by_resource_id(
                "com.samsung.android.messaging:id/change_app"
            )
            # dpad down
            p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 20"])
            p.wait()
            p = subprocess.Popen(
                ["adb", "-s", d_url, "shell", "input keyevent 20"]
            )  # dpad down
            p.wait()
            subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 66"])
        checkSetAsDefault = self.checkElement("android:id/button1")
        if checkSetAsDefault:
            pos_palette = True
            self.click_element_by_resource_id("android:id/button1")
        return pos_palette

    def open_message_App(self):
        d_url = self.idDevice
        time.sleep(1)
        try:
            subprocess.Popen(
                [
                    "adb",
                    "-s",
                    d_url,
                    "shell",
                    "am start -n com.samsung.android.messaging/com.android.mms.ui.ConversationComposer",
                ]
            )
            time.sleep(2)
            self.messages_permissions()
        except:
            subprocess.Popen(
                [
                    "adb",
                    "-s",
                    d_url,
                    "shell",
                    "am start -n com.google.android.apps.messaging/.ui.ConversationListActivity",
                ]
            )
            check_OK = self.checkElement(
                "com.google.android.apps.messaging:id/conversation_list_spam_popup_positive_button"
            )
            if check_OK:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/conversation_list_spam_popup_positive_button"
                )
            check_UseWithout = self.checkElement(
                "com.google.android.apps.messaging:id/conversation_list_google_tos_popup_negative_button"
            )
            if check_UseWithout:
                self.click_element_by_resource_id(
                    "com.google.android.apps.messaging:id/conversation_list_google_tos_popup_negative_button"
                )

    def saveContact(self, numero, nome):
        idDevice = self.idDevice
        savePhone = 'Phone'
        saveButton_os10 = 'com.samsung.android.app.contacts:id/menu_done'
        setAsDefault = 'Set as default'
        self.contactScreen()
        self.wait(1)
        button_addNewContact_os10 = 'com.samsung.android.app.contacts:id/contact_list_floating_action_button'
        button_addNewContact_os12 = 'com.samsung.android.app.contacts:id/menu_create_contact'
        if self.os_version == "10":
            self.click_element_by_resource_id(button_addNewContact_os10)
        else:
            self.click_element_by_resource_id(button_addNewContact_os12)
        if self.checkElement('Save contact to'):
            check_Phone = self.checkElement(savePhone)
            if check_Phone:
                self.click_element_by_text(savePhone)
                check_SetAsDefault = self.checkElement(setAsDefault)
                if check_SetAsDefault:
                    self.click_element_by_text(setAsDefault)
            self.insertContactInfo(idDevice, nome, numero)
        else:
            self.insertContactInfo(idDevice, nome, numero)

        self.closeAllApps()

    def insertContactInfo(self, idDevice, nome, numero):
        self.wait(1)
        check_output(
            ["adb", "-s", idDevice, "shell", f'input text "{nome}"'])  # inserir nome no campo Name (já vem selecionado)
        self.KEYCODE_BACK()  # remover o teclado da tela
        self.wait(1)

        if self.os_version == '10':
            self.KEYCODE_DPAD_DOWN()
            self.wait(1)
            self.KEYCODE_DPAD_DOWN()
            self.wait(1)
            self.KEYCODE_ENTER()


        else:
            self.KEYCODE_DPAD_DOWN()
            self.wait(1)
            self.KEYCODE_ENTER()
            self.wait(1)
            self.KEYCODE_DPAD_DOWN()
            self.wait(1)
            self.KEYCODE_ENTER()

        self.wait(1)
        check_output(["adb", "-s", idDevice, "shell",
                      f'input text "{numero}"'])  # inserir nome no campo Name (já vem selecionado)
        self.KEYCODE_BACK()  # remover o teclado da tela
        self.wait(1)
        self.click_element_by_resource_id('com.samsung.android.app.contacts:id/menu_done')

    def set_SIM2(self):
        idDevice = self.idDevice
        self.KEYCODE_HOME()
        check_output(
            [
                "adb",
                "-s",
                idDevice,
                "shell",
                "am start -a android.settings.WIRELESS_SETTINGS",
            ]
        )
        self.click_element_by_text("SIM card manager")
        print("##### SETANDO SIM CARD 2 #####")
        try:
            self.click_element_by_text("Calls")
            self.click_element_by_text("SIM 2")
            check_Messages = self.checkElement("Messages")
            check_TextMessages = self.checkElement("Text messages")
            if check_Messages:
                self.click_element_by_text("Messages")
            elif check_TextMessages:
                # fazer a lógica para o 'Text messages'
                self.click_element_by_text("Text messages")
            self.click_element_by_text("SIM 2")
            self.click_element_by_text("Mobile data")
            self.click_element_by_text("SIM 2")
            print("##### SIM CARD 2 SETADO #####")
        except:
            print("Erro ao setar amostra para usar SIM Card 2")

        check_Change = self.checkElement("android:id/button1")
        if check_Change:
            self.click_element_by_resource_id("android:id/button1")

        try:
            self.closeAllApps()
        except:
            self.go_home()

    def set_SIM1(self):
        idDevice = self.idDevice
        print("##### SETANDO SIM CARD 1 #####")
        self.KEYCODE_HOME()
        check_output(
            [
                "adb",
                "-s",
                idDevice,
                "shell",
                "am start -a android.settings.WIRELESS_SETTINGS",
            ]
        )
        checkSIM_Manager = self.checkElement("SIM card manager")
        if checkSIM_Manager:
            self.click_element_by_text("SIM card manager")
            try:
                self.click_element_by_text("Calls")
                self.click_element_by_text("SIM 1")
                check_Messages = self.checkElement("Messages")
                check_TextMessages = self.checkElement("Text messages")
                if check_Messages:
                    self.click_element_by_text("Messages")
                elif check_TextMessages:
                    # fazer a lógica para o 'Text messages'
                    self.click_element_by_text("Text messages")
                self.click_element_by_text("SIM 1")
                self.click_element_by_text("Mobile data")
                self.click_element_by_text("SIM 1")
                print("##### SIM CARD 1 SETADO #####")
            except:
                print("Erro ao setar amostra para usar SIM Card 1")

        check_Change = self.checkElement("android:id/button1")
        if check_Change:
            self.click_element_by_resource_id("android:id/button1")

        try:
            self.closeAllApps()
        except:
            self.go_home()

    def contactScreen(self):
        d_url = self.idDevice
        check_output(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                "am start -n com.samsung.android.app.contacts/com.samsung.android.contacts.contactslist.PeopleActivity",
            ]
        )

    def getDeviceId(self):
        return self.idDevice

    def try_closeAllApps(self):
        try:
            self.closeAllApps()
        except:
            self.KEYCODE_HOME()

    def outgoing_voicecall(
        self,
        support_device1,
        support_device1_url,
        numero_suporte1,
        support_device2,
        support_device2_url,
        numero_suporte2,
        pathToSave,
        SIMslot,
    ):
        try:
            time.sleep(3)
            # phone 1 SIM1 liga para telefone de suporte #1 (numero3)
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    f"am start -a android.intent.action.CALL -d tel:{numero_suporte1}",
                ]
            )
            time.sleep(25)
            # phone 2 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    time.sleep(1)
                    check_output(
                        ["adb", "-s", support_device1_url, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a chamada")
            # phone1 desliga a ligação após 10 segundos
            time.sleep(32)
            self.gerar_evidencia_testes_de_ligacao_outgoing(SIMslot, pathToSave)
            # support_device1.getScreenShot("T2_Incoming_VoiceCall_DS.png", pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_ENDCALL"]
            )
            time.sleep(3)
            # desbloquear a tela
            check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 82"])
            support_device1.closeAllApps()
            self.closeAllApps()
            time.sleep(2)
        except:
            self.closeAllApps()
            time.sleep(2)
            # phone 1 liga para telefone de suporte #2 (numero4)
            self.KEYCODE_HOME()
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    f"am start -a android.intent.action.CALL -d tel:{numero_suporte2}",
                ]
            )
            time.sleep(20)
            # phone 2 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    time.sleep(1)
                    check_output(
                        ["adb", "-s", support_device2_url, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a chamada")
            # phone1 desliga a ligação após 10 segundos
            time.sleep(32)
            self.gerar_evidencia_testes_de_ligacao_outgoing(SIMslot, pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "input keyevent KEYCODE_ENDCALL"]
            )
            time.sleep(3)
            # desbloquear a tela
            check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 82"])
            support_device2.KEYCODE_HOME()
            self.KEYCODE_HOME()
            time.sleep(2)

    def gerar_evidencia_testes_de_ligacao_outgoing(self, SIMslot, pathToSave):
        if SIMslot == "SS":
            self.getScreenShot("T116_Outgoing_VoiceCall_SS.png", pathToSave)
        elif SIMslot == "DS":
            self.getScreenShot("T76_Outgoing_VoiceCall_DS.png", pathToSave)

    def incoming_voicecall(
        self,
        numero_device,
        support_device1,
        support_device1_url,
        support_device2,
        support_device2_url,
        pathToSave,
        SIMslot,
    ):
        try:
            # suporte1 liga para o phone numero1
            time.sleep(2)
            check_output(
                [
                    "adb",
                    "-s",
                    support_device1_url,
                    "shell",
                    f"am start -a android.intent.action.CALL -d tel:{numero_device}",
                ]
            )
            time.sleep(15)
            # phone1 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    check_output(
                        ["adb", "-s", self.idDevice, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a chamada")
            # phone2 desliga a ligação após 10 segundos
            time.sleep(32)
            self.gerar_evidencias_incoming_voicecall(SIMslot, pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    support_device1_url,
                    "shell",
                    "input keyevent KEYCODE_ENDCALL",
                ]
            )
            time.sleep(3)
            # desbloquear a tela
            check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 82"])
            # desbloquear a tela
            check_output(
                ["adb", "-s", support_device1_url, "shell", "input keyevent 82"]
            )
            support_device1.KEYCODE_HOME()
            self.KEYCODE_HOME()
            time.sleep(2)
        except:
            self.closeAllApps()
            time.sleep(2)
            # suporte2 liga para o phone numero1
            check_output(
                [
                    "adb",
                    "-s",
                    support_device2_url,
                    "shell",
                    f"am start -a android.intent.action.CALL -d tel:{numero_device}",
                ]
            )
            time.sleep(15)
            # phone1 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    check_output(
                        ["adb", "-s", self.idDevice, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a chamada")
            # phone2 desliga a ligação após 10 segundos
            time.sleep(32)
            self.gerar_evidencias_incoming_voicecall(SIMslot, pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    support_device2_url,
                    "shell",
                    "input keyevent KEYCODE_ENDCALL",
                ]
            )
            time.sleep(3)
            # desbloquear a tela
            check_output(["adb", "-s", self.idDevice, "shell", "input keyevent 82"])
            support_device2.KEYCODE_HOME()
            self.KEYCODE_HOME()
            time.sleep(2)

    def gerar_evidencias_incoming_voicecall(self, SIMslot, pathToSave):
        if SIMslot == "SS":
            self.getScreenShot("T128_Incoming_VoiceCall_SS.png", pathToSave)
        elif SIMslot == "DS":
            self.getScreenShot("T2_Incoming_VoiceCall_DS.png", pathToSave)
            # support_device1.getScreenShot("T76_Outgoing_VoiceCall_DS.png", pathToSave)

    def add_GoogleDuo_acc(self, numero):
        d_url = self.idDevice
        check_output(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                "am start -n com.google.android.apps.tachyon/.ui.main.MainActivity",
            ]
        )
        # d.click_element_by_resource_id("com.google.android.apps.tachyon:id/welcome_agree_button")
        time.sleep(5)
        self.click_element_by_resource_id(
            "com.google.android.apps.tachyon:id/welcome_agree_button"
        )
        try:
            self.click_element_by_resource_id(
                "com.google.android.apps.tachyon:id/registration_country_code_text"
            )
            present = self.checkElement("Brazil")
            if present:
                self.click_element_by_text("Brazil")
            else:
                while not present:
                    before = self.getXMLDump()
                    self.swipe_up()
                    after = self.getXMLDump()
                    # Scroll down
                    while after != before:
                        before = after
                        self.swipe_up()
                        after = self.getXMLDump()
                        present = self.checkElement("Brazil")
                        if present:
                            self.click_element_by_text("Brazil")
                            break
                    # Scroll Up
                    before = self.getXMLDump()
                    self.swipe_down()
                    after = self.getXMLDump()
                    while after != before:
                        before = after
                        self.swipe_down()
                        after = self.getXMLDump()
                        present = self.checkElement("Brazil")
                        if present:
                            self.click_element_by_text("Brazil")
                            break
            print("Elemento clicado!!")
            print("Código do país está setado")
        except:
            print("Código do país já está setado")

        # Colocar o número
        self.long_press_by_resource_id(
            "com.google.android.apps.tachyon:id/registration_phone_edittext"
        )
        time.sleep(1)
        check_output(["adb", "-s", d_url, "shell", "input keyevent 67"]).decode("ascii")
        time.sleep(1)
        check_output(["adb", "-s", d_url, "shell", f'input text "{numero}"'])
        time.sleep(5)
        self.KEYCODE_APP_SWITCH()
        x_centro, y_centro = self.getSize()
        x_centro = x_centro / 2
        y_centro = y_centro / 2
        subprocess.Popen(f"adb -s {d_url} shell input tap {x_centro} {y_centro}")
        time.sleep(1)
        # stdout, stderr = p.communicate()
        check_Agree = self.checkElement(
            "com.google.android.apps.tachyon:id/registration_send_button"
        )
        if check_Agree:
            self.click_element_by_resource_id(
                "com.google.android.apps.tachyon:id/registration_send_button"
            )
        else:
            self.click_element_by_resource_id(
                "com.google.android.apps.tachyon:id/footer_registration_send_button"
            )
        time.sleep(15)
        try:
            self.closeAllApps()
            self.KEYCODE_HOME()
        except:
            print("Apps fechados")

    def DuT_liga(
        self,
        SIMslot,
        numero_suporte1,
        numero_suporte2,
        pathToSave,
        support_device1_url,
        support_device2_url,
    ):
        try:
            # DuT liga para suporte 1
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    f'service call phone 1 s16 "{numero_suporte1}"',
                ]
            )
            time.sleep(1)
            self.click_VideoCall_button()
            time.sleep(10)
            # suporte 1 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    check_output(
                        ["adb", "-s", support_device1_url, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a ligação")
            ## tirar um pop up de auxilio ##
            x_centro, y_centro = self.getSize()
            x_centro = x_centro / 2
            y_centro = y_centro / 2
            p = subprocess.Popen(
                f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
            )
            _, _ = p.communicate()
            ## tirar um pop up de auxilio ##
            print("Esperar 30s")
            time.sleep(30)
            self.coleta_evidencias_googleDuo_outgoing(SIMslot, pathToSave)
            subprocess.Popen(
                f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
            )
            x_end, Y_end = self.getElementPositionByContentDesc("End call")
            # DuT desliga
            desligou = False
            cont = 0
            while not desligou and cont < 6:
                try:
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
                    )
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_end} {Y_end}"
                    )
                    desligou = True
                    print("Chamada encerrada")
                except:
                    cont += 1
                    print("Elemento não encontrado")
            self.closeAllApps()
            time.sleep(5)
        except:
            # DuT liga para suporte 2
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    f'service call phone 1 s16 "{numero_suporte2}"',
                ]
            )
            self.click_VideoCall_button()
            time.sleep(10)
            # suporte 2 atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 6:
                try:
                    check_output(
                        ["adb", "-s", support_device2_url, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a ligação")
            ## tirar um pop up de auxilio ##
            x_centro, y_centro = self.getSize()
            x_centro = x_centro / 2
            y_centro = y_centro / 2
            p = subprocess.Popen(
                f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
            )
            _, _ = p.communicate()
            ## tirar um pop up de auxilio ##
            print("Esperar 30s")
            time.sleep(30)
            self.coleta_evidencias_googleDuo_outgoing(SIMslot, pathToSave)
            # DuT desliga
            desligou = False
            cont = 0
            while not desligou and cont < 6:
                try:
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
                    )
                    self.click_element_by_content_desc("End call")
                    desligou = True
                    print("Chamada encerrada")
                except:
                    cont += 1
                    print("Elemento não encontrado")
            try:
                self.closeAllApps()
                self.KEYCODE_HOME()
            except:
                print("Não há apps abertos")
            time.sleep(5)

    def click_VideoCall_button(self):
        check_DuoVideoCallButton = self.checkElement("Duo video call button")
        check_VideoCallButton = self.checkElement("Video call button")
        if check_DuoVideoCallButton:
            self.click_element_by_content_desc("Duo video call button")
        elif check_VideoCallButton:
            self.click_element_by_content_desc("Video call button")

    def coleta_evidencias_googleDuo_outgoing(self, SIMslot, pathToSave):

        if SIMslot == "SS":
            self.getScreenShot("T111_Outgoing_VideoCall_SS_screen.png", pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "cmd statusbar expand-notifications",
                ]
            )
            self.getScreenShot("T111_Outgoing_VideoCall_SS_time.png", pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "cmd statusbar collapse"]
            )
        elif SIMslot == "DS":
            self.getScreenShot("T110_Outgoing_VideoCall_DS_screen.png", pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "cmd statusbar expand-notifications",
                ]
            )
            self.getScreenShot("T110_Outgoing_VideoCall_DS_time.png", pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "cmd statusbar collapse"]
            )

    def DuT_recebe(
        self,
        SIMslot,
        numero_device,
        pathToSave,
        support_device1,
        support_device1_url,
        support_device2,
        support_device2_url,
    ):
        try:
            # Suporte 1 liga para Dut
            check_output(
                [
                    "adb",
                    "-s",
                    support_device1_url,
                    "shell",
                    f'service call phone 1 s16 "{numero_device}"',
                ]
            )
            self.click_VideoCall_button()
            # support_device1.click_element_by_content_desc("Duo video call button")
            time.sleep(10)
            # DuT atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 10:
                try:
                    check_output(
                        ["adb", "-s", self.idDevice, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 1
                    print("Aguardando a ligação")
            print("Esperar 30s")
            time.sleep(30)
            # prints da tela
            # adb shell cmd statusbar expand-notifications //// adb shell cmd statusbar collapse
            self.coleta_evidencias_googleDuo_incoming(SIMslot, pathToSave)
            # DuT desliga
            x_centro, y_centro = self.getSize()
            x_centro = x_centro / 2
            y_centro = y_centro / 2
            p = subprocess.Popen(
                f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
            )
            _, _ = p.communicate()
            x_end, Y_end = self.getElementPositionByContentDesc("End call")
            desligou = False
            cont = 0
            while not desligou and cont < 10:
                try:
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
                    )
                    # self.click_element_by_content_desc("End call")
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_end} {Y_end}"
                    )
                    desligou = True
                    print("Chamada encerrada")
                except:
                    cont += 1
                    print("Elemento não encontrado")
            self.closeAllApps()
            print("Teste finalizado")
        except:
            # Suporte 2 liga para Dut
            check_output(
                [
                    "adb",
                    "-s",
                    support_device2_url,
                    "shell",
                    f'service call phone 1 s16 "{numero_device}"',
                ]
            )
            self.click_VideoCall_button()
            # support_device2.click_element_by_content_desc("Duo video call button")
            time.sleep(10)
            # DuT atende
            atendeu = False
            cont = 0
            while not atendeu and cont < 10:
                try:
                    check_output(
                        ["adb", "-s", self.idDevice, "shell", "input keyevent 5"]
                    )
                    atendeu = True
                except:
                    cont += 0
                    print("Aguardando a ligação")
            ## tirar um pop up de auxilio ##
            x_centro, y_centro = self.getSize()
            x_centro = x_centro / 2
            y_centro = y_centro / 2
            p = subprocess.Popen(
                f"adb -s {support_device2_url} shell input tap {x_centro} {y_centro}"
            )
            _, _ = p.communicate()
            ## tirar um pop up de auxilio ##
            print("Esperar 30s")
            time.sleep(30)
            # prints da tela
            # adb shell cmd statusbar expand-notifications //// adb shell cmd statusbar collapse
            self.coleta_evidencias_googleDuo_incoming(SIMslot, pathToSave)
            # Dut desliga
            x_centro, y_centro = self.getSize()
            x_centro = x_centro / 2
            y_centro = y_centro / 2
            p = subprocess.Popen(
                f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
            )
            _, _ = p.communicate()
            desligou = False
            cont = 0
            while not desligou and cont < 10:
                try:
                    subprocess.Popen(
                        f"adb -s {self.idDevice} shell input tap {x_centro} {y_centro}"
                    )
                    self.click_element_by_content_desc("End call")
                    desligou = True
                    print("Chamada encerrada")
                except:
                    cont += 1
                    print("Elemento não encontrado")
            try:
                self.closeAllApps()
                self.KEYCODE_HOME()
            except:
                print("Apps fechados")
            print("Teste finalizado")

    def coleta_evidencias_googleDuo_incoming(self, SIMslot, pathToSave):

        if SIMslot == "SS":
            self.getScreenShot("T115_Incoming_VideoCall_SS_screen.png", pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "cmd statusbar expand-notifications",
                ]
            )
            self.getScreenShot("T115_Incoming_VideoCall_SS_time.png", pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "cmd statusbar collapse"]
            )
        elif SIMslot == "DS":
            self.getScreenShot("T72_Incoming_VideoCall_DS_screen.png", pathToSave)
            check_output(
                [
                    "adb",
                    "-s",
                    self.idDevice,
                    "shell",
                    "cmd statusbar expand-notifications",
                ]
            )
            self.getScreenShot("T72_Incoming_VideoCall_DS_time.png", pathToSave)
            check_output(
                ["adb", "-s", self.idDevice, "shell", "cmd statusbar collapse"]
            )

    def remove_googleDuo_account(self):
        self.openDeviceSettings()
        while not self.checkElement("Accounts and backup"):
            self.swipe_up()
        self.click_element_by_text("Accounts and backup")
        if self.checkElement("Manage accounts"):
            self.click_element_by_text("Manage accounts")
        elif self.checkElement("Accounts"):
            self.click_element_by_text("Accounts")
        check_Duo = self.checkElement("Duo")
        if check_Duo:
            self.click_element_by_text("Duo")
        check_RemoveButton = self.checkElement("com.android.settings:id/button")
        if check_RemoveButton:
            self.click_element_by_resource_id("com.android.settings:id/button")
        check_RemoveAccountButton_popUp = self.checkElement(
            "com.android.settings:id/button1"
        )
        check_RemoveAccountButton_popUp_11 = self.checkElement("android:id/button1")
        if check_RemoveAccountButton_popUp:
            self.click_element_by_resource_id("com.android.settings:id/button1")
        elif check_RemoveAccountButton_popUp_11:
            self.click_element_by_resource_id("android:id/button1")
        self.closeAllApps()
        # d.KEYCODE_HOME()

    def limpar_dados_GoogleDuo(self):
        self.openDeviceSettings()
        time.sleep(5)
        self.swipe_up()
        check_Apps = self.checkElement("Apps")
        while not check_Apps:
            self.swipe_up()
            check_Apps = self.checkElement("Apps")
        self.click_element_by_text("Apps")
        time.sleep(6)
        self.swipe_up()
        time.sleep(2)
        self.swipe_up()
        check_Duo = self.checkElement("Duo")
        while not check_Duo:
            self.swipe_up()
            check_Duo = self.checkElement("Duo")
        self.click_element_by_text("Duo")
        time.sleep(3)
        check_storage = self.checkElement("Storage")
        if check_storage:
            self.click_element_by_text("Storage")
        time.sleep(3)
        check_ClearData = self.checkElement("com.android.settings:id/button1")
        if check_ClearData:
            self.click_element_by_resource_id("com.android.settings:id/button1")
        time.sleep(3)
        check_OkButton = self.checkElement("android:id/button1")
        if check_OkButton:
            self.click_element_by_resource_id("android:id/button1")
        else:
            self.click_element_by_resource_id("com.android.settings:id/button1")
        self.try_closeAllApps()
        self.KEYCODE_HOME()

    def clear_launcher(self):

        check_output(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "pm clear com.sec.android.app.launcher",
            ]
        )

    def move_to_hotseat(self, text, pos_y):
        x, y = self.getElementPositionByResourceId(text=text)
        self.swipe(x, y, 15, pos_y, 25000)

    def pos_y_app(self, text):
        x, y = self.getElementPositionByResourceId(text=text)
        return y

    def down_element(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 20"])
        p.wait()

    def up_element(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 19"])
        p.wait()

    def right_element(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 22"])
        p.wait()

    def left_element(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 21"])
        p.wait()

    def click_atual_element(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 66"])
        p.wait()

    def get_ap_version(self):

        ap_device = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ro.build.PDA"]
            ).decode("ascii")
        ).strip()
        return ap_device

    def get_csc_version(self):
        csc_device = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ril.official_cscver"]
            ).decode("ascii")
        ).strip()

        return csc_device

    def get_cp_version(self):
        cp_device = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ril.sw_ver"]
            ).decode("ascii")
        ).strip()
        return cp_device

    def get_hidden_version(self):

        ap_hidden = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ril.approved_codever"]
            ).decode("ascii")
        ).strip()

        csc_hidden = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ril.approved_cscver"]
            ).decode("ascii")
        ).strip()

        cp_hidden = str(
            subprocess.check_output(
                ["adb", "-s", self.idDevice, "shell", "getprop ril.approved_modemver"]
            ).decode("ascii")
        ).strip()

        hidden_version = "{ap} {csc} {cp}".format(
            ap=ap_hidden, csc=csc_hidden, cp=cp_hidden
        )
        return hidden_version

    def get_svn_number(self):

        if self.os_version in ("11"):
            svn_device = str(
                subprocess.check_output(
                    [
                        "adb",
                        "-s",
                        self.idDevice,
                        "shell",
                        "service",
                        "call",
                        "iphonesubinfo",
                        "6",
                    ]
                ).decode("ascii")
            ).strip()
        else:
            svn_device = str(
                subprocess.check_output(
                    [
                        "adb",
                        "-s",
                        self.idDevice,
                        "shell",
                        "service",
                        "call",
                        "iphonesubinfo",
                        "5",
                    ]
                ).decode("ascii")
            ).strip()

        r = re.findall("'(.*)'", svn_device)
        svn_number = str(int(r[0].replace(".", "")))
        return svn_number

    def get_current_activity(self):

        output = (
            subprocess.Popen(
                "adb -s "
                + self.idDevice
                + ' shell "dumpsys activity activities | grep mResumedActivity"',
                shell=True,
                stdout=subprocess.PIPE,
            )
            .communicate()[0]
            .decode("ascii")
        )

        return output

    def swipe_up_wizard(self):
        width, height = self.getSize()
        self.swipe(
            int(width) / 2,
            int(height) * 0.965,
            int(width) / 2,
            int(height) - int(height) / 2,
            500,
        )

    def disable_mobile_data(self):

        subprocess.Popen(
            "adb -s {device} shell svc data disable".format(device=self.idDevice)
        )

    def enable_mobile_data(self):

        subprocess.Popen(
            "adb -s {device} shell svc data enable".format(device=self.idDevice)
        )

    def install_adb_join_wifi(self):
        subprocess.Popen(
            "adb -s " + self.idDevice + ' install -r "%cd%\\files\\adb-join-wifi.apk"',
            shell=True,
            stdout=subprocess.PIPE,
        ).communicate()[0]

    def install_adb_keyboard(self):
        subprocess.Popen(
            "adb -s " + self.idDevice + ' install -r "%cd%\\files\\adb-keyboard.apk"',
            shell=True,
            stdout=subprocess.PIPE,
        ).communicate()[0]

    def set_adb_keyboard(self):
        self.openDeviceSettings()

        flag = self.checkElement("General management")
        
        while flag == False:
            for i in range(0,5):
                self.down_element()

            flag = self.checkElement("General management")

        self.click_element_by_text("General management")
        self.click_element_by_text("Keyboard list and default")

        ref = self.get_dump_decoded()
        ref_tree = ET.ElementTree(ET.fromstring(ref))
        fil = "*"

        for child in ref_tree.iter(fil):
            if (child.tag == 'node') and (child.attrib['resource-id'] == "android:id/switch_widget"):
                if (child.attrib['content-desc'] == 'ADB Keyboard') and (child.attrib['checked'] == 'false'):
                    self.click_element_by_content_desc("ADB Keyboard")
                    self.wait(1)
                    self.click_element_by_text("OK")
                    self.wait(1)
                    self.click_element_by_text("OK")

        p = subprocess.Popen(
            "adb -s {device} shell ime set com.android.adbkeyboard/.AdbIME".format(device=self.idDevice)
        )
        p.wait()

    def set_samsung_keyboard(self):
        p = subprocess.Popen(
            "adb -s {device} shell ime set com.samsung.android.honeyboard/.service.HoneyBoardService".format(device=self.idDevice)
        )
        p.wait()

    def inputADBText(self, msg):
        p = subprocess.Popen(
            "adb -s {device} shell am broadcast -a ADB_INPUT_TEXT --es msg \'{msg}\'".format(device=self.idDevice, msg=msg)
        )
        p.wait()

    def connect_to_wifi_with_adb_join(self):
        self.install_adb_join_wifi()

        subprocess.run(
            [
                "adb",
                "-s",
                self.idDevice,
                "shell",
                "am start -n com.steinwurf.adbjoinwifi/.MainActivity -e ssid SIDIA-GA-2.4GHZ -e password_type WPA -e "
                "password antoniocosta712768",
            ],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

    def get_all_packages(self):
        resp = check_output(
            ["adb", "-s", self.idDevice, "shell", "pm list packages -l -e"]
        )
        return resp

    def open_recent_apps(self):
        d_url = self.idDevice
        p = subprocess.Popen(
            ["adb", "-s", d_url, "shell", "input keyevent KEYCODE_APP_SWITCH"]
        )
        p.wait()

    def open_airplane_settings(self):
        d_url = self.idDevice
        p = subprocess.Popen(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                "am start -a android.settings.AIRPLANE_MODE_SETTINGS",
            ]
        )
        p.wait()

    def KEYCODE_CALL(self):
        d_url = self.idDevice
        p = subprocess.Popen(["adb", "-s", d_url, "shell", "input keyevent 5"])
        p.wait()

    def get_imei1(self):
        d_url = self.idDevice
        p = subprocess.Popen(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                """ "service call iphonesubinfo 1 | cut -c 52-66 | tr -d '.[:space:]'" """,
            ]
        )
        p.wait()

    def enable_disable_airplane(self):
        self.open_airplane_settings()
        self.down_element()
        self.down_element()
        self.click_atual_element()

    def count_hotseat_apps(self):
        screen = self.getXMLDump()
        tree = ET.ElementTree(ET.fromstring(screen))

        filtro = "*"
        flag = False
        count = 0
        for child in tree.iter(filtro):
            if (child.tag == "node") and (
                child.attrib["resource-id"] == "com.sec.android.app.launcher:id/hotseat"
            ):
                flag = True
            if flag:
                count = count + 1

        return count - 2

    def get_serial_model_device(self):
        # ril.serialnumber
        p = subprocess.run(
            ["adb", "-s", self.idDevice, "shell", "getprop", "ril.serialnumber"],
            stdout=subprocess.PIPE,
        ).stdout.__str__()

        result = p.replace("b'", "").replace("'", "").replace("\\r\\n", "")
        if result == "":
            p = subprocess.run(
                ["adb", "-s", self.idDevice, "shell", "getprop", "ro.serialno"],
                stdout=subprocess.PIPE,
            ).stdout.__str__()

        return p.replace("b'", "").replace("'", "").replace("\\r\\n", "")

    def homeScreen_byPath(self):
        d_url = self.idDevice
        p = subprocess.Popen(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                "am start -a android.intent.action.MAIN -c android.intent.category.HOME",
            ]
        )
        p.wait()

    def go_home(self):
        self.homeScreen_byPath()
        self.KEYCODE_BACK()
        self.KEYCODE_BACK()
        self.homeScreen_byPath()

    def swipe_right_folder(self, move=0.3):
        width, height = self.getSize()
        self.swipe(
            int(width) * 0.90,
            int(height) / 2,
            (int(height) / 2) * move,
            int(width) * 0.97,
            500,
        )

    def portrait_mode(self):
        d_url = self.idDevice
        p = subprocess.Popen(
            [
                "adb",
                "-s",
                d_url,
                "shell",
                "content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0",
            ]
        )
        p.wait()

    def saveContact(self, numero, nome):
        idDevice = self.idDevice
        savePhone = 'Phone'
        saveButton_os10 = 'com.samsung.android.app.contacts:id/menu_done'
        setAsDefault = 'Set as default'
        self.contactScreen()
        self.wait(1)
        button_addNewContact_os10 = 'com.samsung.android.app.contacts:id/contact_list_floating_action_button'
        button_addNewContact_os12 = 'com.samsung.android.app.contacts:id/menu_create_contact'
        if self.os_version == "10":
            self.click_element_by_resource_id(button_addNewContact_os10)
        else:
            self.click_element_by_resource_id(button_addNewContact_os12)
        if self.checkElement('Save contact to'):
            check_Phone = self.checkElement(savePhone)
            if check_Phone:
                self.click_element_by_text(savePhone)
                check_SetAsDefault = self.checkElement(setAsDefault)
                if check_SetAsDefault:
                    self.click_element_by_text(setAsDefault)
            self.insertContactInfo(idDevice, nome, numero)
        else:
            self.insertContactInfo(idDevice, nome, numero)

        self.closeAllApps()

    def open_ManageAccount(self):
        self.go_home()
        self.openDeviceSettings()
        count = 0
        while (not self.checkElement("Accounts and backup")) and (count < 20):
            self.swipe_up_tablet()
        self.click_element_by_text("Accounts and backup")
        if self.checkElement("Manage accounts"):
            self.click_element_by_text("Manage saccounts")
        elif self.checkElement("Accounts"):
            self.click_element_by_text("Accounts")

    def open_widgets_screen(self):
        self.KEYCODE_HOME()
        self.wait(1)
        self.KEYCODE_HOME()
        self.wait(1)
        self.long_press_atHScreen()
        self.click_element_by_resource_id("com.sec.android.app.launcher:id/widgets_button")

if __name__ == "__main__":

    self = ADBUiautomator("RQCT302JYQD")
    self.inputText("\ç ")
