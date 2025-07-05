from plyer import notification


# 显示通知

def swap(device, icon, state):
    if not device:
        device = ''
    if state:
        title = '启用设备'
        message = "检测到 " + device + " 已接入计算机, 已成功自动启用该设备"
    else:
        title = '移除设备'
        message = "已成功禁用 " + device + ", 现在您可将此设备安全地从计算机移除"
    notification.notify(
        title=title,
        message=message,
        timeout=1,  # timeout 是通知的显示时长，单位为秒
        app_icon=icon
    )

def error(device, code):
    notification.notify(
        title="出现错误",
        message="检测发现 "+device+" 出现 "+str(code)+" 错误, 请打开设备管理器进行排查, 为保护设备本软件将退出",
        timeout=1,  # timeout 是通知的显示时长，单位为秒
        app_icon='resource\\error.ico'
    )

def devcon_warning():
    notification.notify(
        title="警告",
        message="无法调用 devcon.exe, 软件将继续运行, 但响应速度将降低, 请检查软件设置",
        timeout=1,  # timeout 是通知的显示时长，单位为秒
        app_icon='resource\\error.ico'
    )