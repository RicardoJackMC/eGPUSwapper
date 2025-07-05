import json
import os
import subprocess
import sys
import threading
import time

from pythoncom import COINIT_MULTITHREADED, CoInitializeEx
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon
from qfluentwidgets import SystemTrayMenu, Action, Theme, setTheme, getIconColor, Dialog
from wmi import WMI

import notice


class SWAPPER(QMainWindow):
    def __init__(self):
        super().__init__()
        self.devcon = None
        self.auto = True
        self.timer_ = True

        if not os.path.isfile('config.json'):
            self.error_w('配置文件缺失, 请打开 Configuration 或重新下载软件')
        with open('config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        if not self.config['device_ID']:
            self.error_w('未配置设备, 请打开 Configuration 或打开 config.json 进行设置')
        if self.config['devcon']:
            if self.config['devcon_path'] and os.path.isfile(self.config['devcon_path']):
                self.devcon = self.config['devcon_path']
            elif os.path.isfile('devcon.exe'):
                self.devcon = 'devcon.exe'
            else:
                notice.devcon_warning()

        theme = [Theme.LIGHT, Theme.DARK, Theme.AUTO]
        theme = theme[self.config['theme_index']]
        setTheme(theme)
        self.SystemTrayIcon = QSystemTrayIcon(self)
        if self.config['icon'] == 'default':
            self.SystemTrayIcon.setIcon(QIcon(f'resource\\device_{getIconColor(theme)}.png'))
        else:
            self.SystemTrayIcon.setIcon(QIcon(self.config['icon']))
        self.SystemTrayIcon.activated.connect(self.stop)
        self.SystemTrayIcon.show()

        self.menu = SystemTrayMenu(parent=self,title='')
        self.menu.addActions([
            Action('移除 '+self.config['device_name'], triggered=self.swap_out),
        ])
        self.SystemTrayIcon.setContextMenu(self.menu)

        t = threading.Thread(target=self.timer)
        t.start()

    def stop(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.timer_ = False
            QCoreApplication.quit()
            sys.exit()

    def error_w(self, msg):
        setTheme(Theme.AUTO)
        w = Dialog("错误", msg, self)
        w.cancelButton.hide()
        if w.exec():
            if os.path.isfile('Configuration.exe'):
                os.startfile('Configuration.exe')
            elif os.path.isfile('config.json'):
                p = subprocess.Popen(
                    ['rundll32.exe', 'shell32.dll,OpenAs_RunDLL', 'config.json'],
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                p.communicate()
            QCoreApplication.quit()
            sys.exit()

    def timer(self):
        CoInitializeEx(COINIT_MULTITHREADED)
        while self.timer_:
            time.sleep(self.config['time'])
            if self.devcon:
                state = self.devcon_command()
            else:
                c = WMI()
                devices = c.Win32_PnPEntity()
                state = self.wmi_checker(devices)
            if not state:
                self.auto = True
                self.menu.setEnabled(False)

    def wmi_checker(self, devices):
        for device in devices:
            if self.config['device_ID'].lower() in device.DeviceID.lower():
                if device.ConfigManagerErrorCode == 0:
                    self.menu.setEnabled(True)
                elif device.ConfigManagerErrorCode == 22:
                    self.menu.setEnabled(False)
                    if self.auto:
                        self.pnputil_command('enable-device')
                else:
                    self.error(code=device.ConfigManagerErrorCode)
                return True
        return False

    def swap_out(self):
        self.auto = False
        self.menu.setEnabled(False)
        self.pnputil_command('disable-device')

    def error(self, code):
        notice.error(self.config['device_name'], code)
        self.timer_ = False
        QCoreApplication.quit()
        sys.exit()

    def devcon_command(self):
        hwid = self.config['device_ID'].rsplit("\\", 1)[0]
        try:
            p = subprocess.Popen(
                [self.devcon, 'status', hwid],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise subprocess.CalledProcessError(p.returncode, p.args, output=stdout, stderr=stderr)

            result = stdout.splitlines()

            if 'Driver is running.' in stdout:
                self.menu.setEnabled(True)
                return True
            elif 'Device is disabled.' in stdout:
                self.menu.setEnabled(False)
                if self.auto:
                    self.pnputil_command('enable-device')
                return True
            elif 'The device has the following problem:' in stdout:
                for r in result:
                    if 'The device has the following problem:' in r:
                        self.error(code=r)
            elif 'No matching devices found.' in stdout:
                return False
            else:
                return True

        except subprocess.CalledProcessError as e:
            self.error(e.returncode)

    def pnputil_command(self, arg):
        try:
            process = subprocess.Popen(
                ['pnputil', '/' + arg, self.config['device_ID']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.error(process.returncode)
                return

            state = arg == 'enable-device'
            notice.swap(self.config['device_name'], self.config['notice_icon'], state)

        except Exception as e:
            self.error(str(e))


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)

    # 替换为你的视频文件路径

    swapper = SWAPPER()

    sys.exit(app.exec_())
