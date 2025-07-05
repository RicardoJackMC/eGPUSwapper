from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase


class DeviceIcon(FluentIconBase, Enum):
    """ Custom icons """

    DEVICE = "device"

    def path(self, theme=Theme.AUTO):
        # getIconColor() 根据主题返回字符串 "white" 或者 "black"
        return f'resource\\{self.value}_{getIconColor(theme)}.svg'