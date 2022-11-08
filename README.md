# JUEJIN-FRIENDS-21days

JUEJIN FRIENDS 好好生活计划 21 天自动签到脚本

## 使用方法

1. clone 本项目到本地
2. 安装依赖

```bash
pip3 install -r requirements.txt
```

3. 修改 `main.py` 文件中的 `cookie` 和 `content`

    > `cookie` 获取方式：登录掘金官网 (https://juejin.cn/)
    > `F12` 打开开发者工具，切换到 `控制台` 标签页，输入 `document.cookie`，复制输出的值

4. 运行脚本

```bash
python3 main.py
```

## 说明

1. 本项目仅供学习交流使用，不得用于商业用途
2. 运行环境：`Python 3`
3. 脚本第一次运行会自动发一贴，如果发送成功说明配置正常，后续每天 00:01 自动打卡
4. 脚本需要保持运行，建议使用 `screen` 或 `tmux` 等工具
