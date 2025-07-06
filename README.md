<p align="center">
  <img width="18%" align="center" src="https://raw.githubusercontent.com/RicardoJackMC/eGPUSwapper/main/.imgs/ico.png" alt="logo">
</p>
  <h1 align="center">
  eGPUSwapper
</h1>
<p align="center">
  更优雅地"热插拔" Oculink 外接显卡
</p>
<p align="center">
  for Ver.0.0.1
</p>
<p align="center">
  <a href="https://www.bilibili.com/video/BV1iWdAYJEdP">灵感来源</a>
</p>
<p align="center">
<a style="text-decoration:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue?color=#4ec820" alt="GPLv3"/>
  </a>  
<a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Windows-blue?color=#4ec820" alt="Platform Windows"/>
  </a>
<a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.9.13-blue?color=#4ec820" alt="Python 3.9.13"/>
  </a>
</p>
<p align="center">
源代码: <a href="https://github.com/RicardoJackMC/eGPUSwapper">GitHub 仓库</a>
</p>
<p align="center">
下载地址: <a href="https://github.com/RicardoJackMC/eGPUSwapper/releases">GitHub release</a> | <a href="https://www.123912.com/s/Y59qVv-pTtbd">123云盘</a>
</p>  


> [!CAUTION]
> ⚠️ 强烈建议用户在了解本软件运行原理以及熟悉 Oculink 外接显卡方案的情况下使用本软件
>
> ⚠️ 本软件未经过广泛的测试, 目前已知在开发者的个人电脑 (ThinkBook 14+ 2025 + RTX 5070 Ti) 运行良好
> 
> ⚠️ 本软件针对 Oculink 外接显卡设置, 不保证兼容其他设备
> 

## 食用方法🍕
> [!CAUTION]
> ⚠️ [Configuration_view.ui](https://github.com/RicardoJackMC/eGPUSwapper/blob/main/Configuration_view.ui) 通过 pyuic 转换后得出的文件并非本软件最终使用的 [ Configuration_view.py](https://github.com/RicardoJackMC/eGPUSwapper/blob/main/Configuration_view.py)
### 0. **使用前请确保自己的设备可以通过以下步骤实现"热插拔"**
> 拔出:
> 🔌 打开**设备管理器**, 在**显示适配器**中右击外接的显卡, 点击**禁用设备**, 拔出 Oculink 连接线
> 
> 插入:
> 🔌 插入 Oculink 连接线后, 打开**设备管理器**, 在**显示适配器**中右击外接的显卡, 点击**启用设备**
> 
> 警告⚠️: 在通过上述方法拔出外接显卡的前提下重新启动计算机, 再通过上述方法插入外接显卡时, 在点击**启用设备**后, 操作系统会弹窗要求重启, 此时若关闭弹窗显卡会报错 (代码 12), 再次重启可解决此问题
> 
> 建议: 将"关机"操作换为"休眠"(不是"睡眠"), 可解决此问题

*本软件实际上自动化完成了这些步骤 (详见[软件原理](#软件原理))*

### 1. 获取设备 ID
1. 打开**设备管理器**, 在**显示适配器**中右击外接的显卡
2. 点击**属性**
3. 点击**事件**
4. 在列表中随便选中一项
5. 将设备 ID 选中并复制 (注意不要漏掉任何字符)

*可参考下面图片*
![get device id](https://raw.githubusercontent.com/RicardoJackMC/eGPUSwapper/main/.imgs/device_id.png)

### 2. 在 Configuration.exe 中配置
1. 填写上一步获得的设备 ID, 然后按 ENTER 键或输入框右侧的放大镜图标确认
2. 配置其他选项
3. 完成配置后在页面下面点"保存"

*若对 Configuration.exe 的其他配置项有疑问可查阅[软件原理](#软件原理)*

### 3. 以管理员身份运行 Swapper.exe
* 右击托盘图标可以禁用外接显卡, 此时可以拔出 Oculink 连接线
* 当外接显卡接入时程序会自动启用设备
* 双击托盘图标可以退出程序

*是不是觉得有点像 U 盘*

> [!CAUTION]
> ⚠️ 由于软件实际上进行的操作与[步骤0](#0. 使用前请确保自己的设备可以通过以下步骤实现"热插拔")的“热插拔”方法相同(详见[软件原理](#软件原理), 所以在拔出外接显卡的前提下重新启动计算机的情况下显卡同样会报错, 并且会导致软件自动退出, 此时再次重启可解决此问题
> 
> 建议: 将"关机"操作换为"休眠"(不是"睡眠"), 可解决此问题

*如果用"休眠"代替"关机", 为保证使用体验, 建议定期“关机”*

## 软件原理📒
软件通过使用 Python 库 subprocess 调用 Windows 自带命令 [pnputil](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax) 实现设备的启用/禁用, 通过周期性 (周期即 Configuration.exe 中的**检查频率**设置项) 使用 [wmi 库](https://pypi.org/project/WMI/)/调用 [devcon.exe](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/devcon) (需用户自行安装, 并在 Configuration.exe 中设置) 实现对设备状态的监控, 其中使用 wmi 库和调用 devcon.exe 的条件及差异如下表
|                             | wmi 库                                                       | devcon.exe                                                   |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 使用条件                    | 当**使用 devcon.exe** 配置项关闭时, 或当**使用 devcon.exe** 配置项开启但软件没有找到 devcon.exe 时 | 当**使用 devcon.exe** 配置项开启并且 devcon.exe 的路径被正确配置 |
| 系统占用 | 较高                                                         | 较低                                                         |
| 响应速度                    | 较慢                                                         | 较快                                                         |
| 安全性                      | 较高                                                         | 较低                                                         |
| 兼容性                      | 较高                                                         | 当设备 ID 设置为外接显卡的设备 ID 时, 软件可以正常工作, 但当设备 ID 设置为其他设备的设备 ID 时, 软件可能无法正常工作 |

* 关于系统占用

  下图分别为启用 devcon.exe 和关闭 devcon.exe 时的系统占用 (其他设置为默认设置)

  * 启用 devcon.exe:

  ![](https://raw.githubusercontent.com/RicardoJackMC/eGPUSwapper/main/.imgs/devcon.png)

  * 关闭 devcon.exe:

  ![](https://raw.githubusercontent.com/RicardoJackMC/eGPUSwapper/main/.imgs/wmi.png)

  *占用很离谱是吧, 所以开发者自己是启用 devcon.exe 的 (实际上开发者本人还是觉得启用 devcon.exe 时的 30 多 MB 的内存占用太高了, 但是他懒得再优化了)*

* 关于安全性

  上文提到当**使用 devcon.exe** 配置项开启并且 devcon.exe 的路径被正确配置, 软件使用 Python 库 subprocess 调用 devcon.exe 实现对设备状态的监控, 而实际上只有当 devcon.exe 的输出包含下列字段时软件才会做出响应:
  
  * Driver is running.
  * Device is disabled.
  * The device has the following problem:
  
  所以用户/软件可能会在用户不知情的情况下**在不恰当的时机禁用/启用设备**, 从而导致**设备损坏**
  
* 关于兼容性

  开发者测试了几种设备, 下表反映了是否使用 devcon.exe 对软件兼容性的影响
  *软件正常工作标记为 ·, 反之记为 X*

  ||wmi 库|devcon.exe|
  |------|------|------|
  |RTX 5070 Ti|·|·|
  |Apple iPhone|·|·|
  |HUAWEI Mate 40|·|·|
  |WD Elements 移动硬盘|·|X|

*小声BB: 网上广为流传的[英伟达 43 补丁](https://egpu.io/forums/expresscard-mpcie-m-2-adapters/script-nvidia-error43-fixer/)*里面有 devcon.exe

## 许可证🏛️

eGPUSwapper 使用 [GPLv3](https://github.com/RicardoJackMC/eGPUSwapper/blob/main/LICENSE) 许可证.

Copyright 2025 by RicardoJackMC

> **Note**
> 如果您是在阅读[软件原理](#软件原理)或软件源码后自行编写程序然后分发, 则您的程序可以不必使用 [GPLv3](https://github.com/RicardoJackMC/eGPUSwapper/blob/main/LICENSE) 许可证. 