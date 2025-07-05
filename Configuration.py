import json
import os
import sys
import threading

import pythoncom
import wmi
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from qfluentwidgets import FluentIcon as FIF, Dialog, getIconColor
from qfluentwidgets import FluentWindow, ScrollArea, SmoothMode
from qfluentwidgets import setTheme, Theme

from Configuration_view import Ui_Form
from notice import swap
from device_icon import DeviceIcon as DI

class UI_Interface(Ui_Form, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.user_config = {}
        self.check = True

        self.setupUi(self)
        self.IndeterminateProgressBar.setVisible(False)
        self.ComboBox.addItem('浅色', userData=Theme.LIGHT)
        self.ComboBox.addItem('深色', userData=Theme.DARK)
        self.ComboBox.addItem('使用系统设置', userData=Theme.AUTO)
        self.CompactDoubleSpinBox.setRange(0.01, 100)
        self.IconWidget.setIcon(DI.DEVICE)
        self.IconWidget_2.setIcon(FIF.RINGER)
        self.IconWidget_3.setIcon(FIF.STOP_WATCH)
        self.IconWidget_4.setIcon(FIF.APPLICATION)
        self.IconWidget_5.setIcon(FIF.BRUSH)
        self.IconWidget_6.setIcon(FIF.BACKGROUND_FILL)
        self.IconWidget_7.setIcon(FIF.FOLDER_ADD)

        self.load_config()
        self.init_config()

        self.SwitchButton.checkedChanged.connect(lambda checked: self.switch_devcon(checked))
        self.SwitchButton_4.checkedChanged.connect(lambda checked: self.switch_swap_in_notice(checked))
        self.SwitchButton_3.checkedChanged.connect(lambda checked: self.switch_swap_out_notice(checked))
        self.SearchLineEdit.returnPressed.connect(lambda: self.handle_device_id(self.SearchLineEdit.text()))
        self.SearchLineEdit.searchSignal.connect(lambda: self.handle_device_id(self.SearchLineEdit.text()))
        self.PushButton.clicked.connect(self.reset_config)
        self.PrimaryPushButton.clicked.connect(self.save_config)
        self.PushButton_2.clicked.connect(self.change_devcon)
        self.PushButton_3.clicked.connect(self.test_swap_in_notice)
        self.PushButton_4.clicked.connect(self.test_swap_out_notice)
        self.PushButton_5.clicked.connect(self.change_notice_icon)
        self.PushButton_6.clicked.connect(self.change_icon)
        self.CompactDoubleSpinBox.valueChanged.connect(lambda value: self.time_changed(value))
        self.ComboBox.currentIndexChanged.connect(lambda index: self.theme_changed(index))

    def load_config(self):
        if not os.path.isfile('config.json'):
            self.fix_config()
        with open('config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)
            self.user_config.update(self.config)

    def init_config(self):
        self.button_init()
        self.SearchLineEdit.setText(self.user_config['device_ID'])
        if self.user_config['device_name']:
            self.CaptionLabel_5.setText('设置应用控制的设备的 ID, 当前设备: '+self.user_config['device_name'])
        else:
            self.CaptionLabel_5.setText('设置应用控制的设备的 ID')
        self.switch_devcon_init()
        self.switch_swap_in_notice_init()
        self.switch_swap_out_notice_init()
        self.CompactDoubleSpinBox.setValue(self.user_config['time'])
        self.ComboBox.setCurrentIndex(self.user_config['theme_index'])

    def button_init(self):
        self.PushButton.setEnabled(False)
        self.PrimaryPushButton.setEnabled(False)

    def config_changde(self):
        if self.user_config != self.config:
            self.PushButton.setEnabled(True)
            self.PrimaryPushButton.setEnabled(True)
        else:
            self.button_init()

    def fix_config(self):
        default_config = {
            'device_ID': None,
            'device_name': None,
            'time': 0.5,
            'devcon': False,
            'devcon_path': None,
            'swap_out_notice': True,
            'swap_in_notice': True,
            'icon': 'default',
            'notice_icon': 'resource\\logo.ico',
            'theme_index': 2
        }
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(default_config, file, ensure_ascii=False, indent=4)

    def reset_config(self):
        self.user_config.update(self.config)
        self.check = False
        self.init_config()

    def save_config(self):
        self.config.update(self.user_config)
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)
        self.check = False
        self.init_config()

    def time_changed(self, value):
        self.user_config['time'] = value
        self.config_changde()

    def switch_swap_out_notice_init(self):
        self.SwitchButton_3.setChecked(self.user_config['swap_out_notice'])
        self.PushButton_4.setEnabled(self.SwitchButton_3.isChecked())

    def switch_swap_in_notice_init(self):
        self.SwitchButton_4.setChecked(self.user_config['swap_in_notice'])
        self.PushButton_3.setEnabled(self.SwitchButton_4.isChecked())

    def switch_devcon_init(self):
        if self.user_config['devcon']:
            self.SwitchButton.setChecked(True)
        else:
            self.SwitchButton.setChecked(False)
        self.CardWidget_9.setEnabled(self.SwitchButton.isChecked())

    def switch_devcon(self, state):
        self.CardWidget_9.setEnabled(state)
        self.user_config['devcon'] = state
        self.config_changde()

    def change_devcon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "devcon.exe", "", "可执行文件 (*.exe)")
        if file_path:
            self.user_config['devcon_path'] = file_path
            self.config_changde()

    def switch_swap_out_notice(self, state):
        self.PushButton_4.setEnabled(state)
        self.user_config['swap_out_notice'] = state
        self.config_changde()

    def switch_swap_in_notice(self, state):
        self.PushButton_3.setEnabled(state)
        self.user_config['swap_in_notice'] = state
        self.config_changde()

    def test_swap_in_notice(self):
        swap(self.user_config['device_name'], self.user_config['notice_icon'], True)

    def test_swap_out_notice(self):
        swap(self.user_config['device_name'], self.user_config['notice_icon'], False)

    def change_notice_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "通知图标", "", "图标 (*.ico)")
        if file_path:
            self.user_config['notice_icon'] = file_path
            self.config_changde()

    def change_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "应用图标", "", "图片 (*.png)")
        if file_path:
            self.user_config['icon'] = file_path
            self.config_changde()

    def theme_changed(self, index):
        self.user_config['theme_index'] = index
        self.config_changde()

    def handle_device_id(self, device_id):
        if self.check:
            self.IndeterminateProgressBar.setVisible(True)
            self.SearchLineEdit.setEnabled(False)
            t = threading.Thread(target=self.check_device_id, args=(device_id,))
            t.start()
        self.check = False

    def check_device_id(self, device_id):
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        c = wmi.WMI()
        for device in c.Win32_PnPEntity():
            if device.PNPDeviceID and device_id.lower() == device.PNPDeviceID.lower():
                # 找到了
                self.IndeterminateProgressBar.setVisible(False)
                self.CaptionLabel_5.setText("已识别设备,设备名: "+str(device.Name))
                self.CaptionLabel_5.show()
                self.SearchLineEdit.setEnabled(True)
                self.user_config['device_name'] = device.Name
                self.user_config['device_ID'] = device_id
                self.config_changde()
                return True
        self.IndeterminateProgressBar.setVisible(False)
        self.CaptionLabel_5.setText("未找到设备, 请检查连接")
        self.CaptionLabel_5.show()
        self.SearchLineEdit.setEnabled(True)
        return False

class Window(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.Interface = UI_Interface(parent=self)
        self.scroll_area = ScrollArea()
        self.scroll_area.enableTransparentBackground()
        self.scroll_area.setSmoothMode(mode=SmoothMode.NO_SMOOTH, orientation=Qt.Orientation.Vertical)
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)
        self.hBoxLayout.addWidget(self.scroll_area)
        self.Interface.setStyleSheet("QWidget{background: transparent}")
        self.scroll_area.setWidget(self.Interface)
        self.scroll_area.setWidgetResizable(True)

        theme = [Theme.LIGHT, Theme.DARK, Theme.AUTO]
        theme = theme[self.Interface.user_config['theme_index']]
        setTheme(theme)
        if self.Interface.user_config['icon'] == 'default':
            self.setWindowIcon(QIcon(f'resource\\device_{getIconColor(theme)}.png'))
        else:
            self.setWindowIcon(QIcon(self.Interface.user_config['icon']))
        self.setWindowTitle('Configuration')

        self.titleBar.raise_()
        self.navigationInterface.hide()
        self.navigationInterface.panel.returnButton.hide()
        self.stackedWidget.hide()

    def closeEvent(self, a0):
        if self.Interface.user_config != self.Interface.config:
            w = Dialog("是否退出", "部分设置项未保存", self)
            if w.exec():
                a0.accept()
                QCoreApplication.quit()
                sys.exit()
            else:
                a0.ignore()

    def resizeEvent(self, e):
        self.titleBar.move(10, 0)
        self.titleBar.resize(self.width()-10, self.titleBar.height())

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()