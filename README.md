# JUEJIN-FRIENDS-21days

JUEJIN FRIENDS 好好生活计划 21 天自动签到脚本  
活动地址 (https://juejin.cn/pin/7163551843082043399)

## 更新日志

1. 2022-11-10 增加发表图片和一言，支持多账号

## 使用方法

1. clone 本项目到本地
2. 安装依赖

```bash
pip3 install -r requirements.txt
```

3. 修改 `main.py` 文件中的 `cookie` 和 `content`

    > `cookie` 获取方式：登录掘金官网 (https://juejin.cn/)
    > `F12` 打开开发者工具，切换到 `网络` 标签页，随便选个带有 `cookie` 的请求，找到 `cookie`，复制粘贴到 `main.py` 文件中的 `cookie` 变量中

4. 运行脚本

```bash
python3 main.py
```

## 云函数部署

函数入口改为：`main.day`

## 说明

1. 本项目仅供学习交流使用，不得用于商业用途
2. 运行环境：`Python 3`
3. 脚本第一次运行会自动发一贴，如果发送成功说明配置正常，后续每天 00:01 自动打卡
4. 脚本需要保持运行，建议使用 `screen` 或 `tmux` 等工具
