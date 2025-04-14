## WechatRobot

项目参考自：https://github.com/lich0821/WeChatFerry

## Quick Start
0. 遇到问题先看看上面的**文档、教程和 FAQ。**
    - 按照步骤来，版本保持一致，少走弯路。
    - 按照步骤来，版本保持一致，少走弯路。
    - 按照步骤来，版本保持一致，少走弯路。
1. 安装 Python>=3.9（Python 12 需要自己编译依赖，慎选），例如 [3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
2. 安装微信对应版本(3.9.12.17)，可点击 [这里](https://github.com/lich0821/WeChatRobot/releases/download/v39.4.2.2/WeChatSetup-3.9.12.17.exe) 下载。
3. 克隆项目
4. 安装依赖
```sh
# 升级 pip
python -m pip install -U pip
# 安装必要依赖
pip install -r requirements.txt
# 国内用户可能会因为网络问题出现安装失败，届时可使用镜像源来下载
pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
```
5. 运行 python main.py
