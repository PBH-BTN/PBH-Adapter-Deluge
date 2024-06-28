# PBH-Adapter-Deluge
一个 Deluge 插件，为 PeerBanHelper 提供所需的 Json RPC 接口

## 下载 PBH-Adapter-Deluge 插件 Egg

在 [版本发布页](https://github.com/PBH-BTN/PBH-Adapter-Deluge/releases) 下载和您 Deluge 版本匹配的版本 Egg，如果没有特殊说明，请下载最新的。

## 在 Deluge 中安装

如果是 Linux 用户，请自行将 egg 放在配置文件夹中。

如果是 Windows 用户，请按照下列步骤操作：

打开 Deluge 配置菜单：
![image](https://github.com/PBH-BTN/PBH-Adapter-Deluge/assets/30802565/4a29ed95-1c17-4e53-b4c1-d0f52d7d3ed9)

转到 Plugins 菜单，点击 Install 按钮

![image](https://github.com/PBH-BTN/PBH-Adapter-Deluge/assets/30802565/22efe0e2-ca92-4a59-8b67-37875095aeea)

在弹出的选择文件对话框中，选择刚刚下载的 egg 文件：

![image](https://github.com/PBH-BTN/PBH-Adapter-Deluge/assets/30802565/a5214562-38ee-499c-9c80-59ec7505899b)

选择后，插件应该就会安装，返回 plugins 菜单，你应该已经看到了 PeerBanHelper 插件，请在前面的复选框中打勾启动，并保存退出。

![image](https://github.com/PBH-BTN/PBH-Adapter-Deluge/assets/30802565/adb53a25-f5bd-4e0a-bb94-2c33a35a6899)

## 在 PBH 中配置

点击 PBH 的新建下载器按钮，弹出的对话框中选择 Deluge 下载器。

![image](https://github.com/PBH-BTN/PBH-Adapter-Deluge/assets/30802565/00d0f5bb-793f-4364-a18f-9e7dc79817ec)

* 名称：起一个自己喜欢的名字
* 地址：填写你的 Deluge WebUI 地址
* 密码：填写你的 Deluge WebUI 密码
* RPC URL：如果不知道这是什么，请填写 `/json`
* 增量封禁：建议启用
* HTTP 版本：保持默认
* 验证 SSL 证书：根据实际情况填写，如果不知道这是什么，请保持默认


