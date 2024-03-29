# This is a sample Python script.
import os
import subprocess
import time
from enum import Enum


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def execute(cmd, ignore_error=False):
    # return sp.run(cmd)
    print("执行---------->" + cmd)

    result = os.popen(cmd)

    result_str = result.read()

    print(result_str)

    if result.close() is not None and not ignore_error:
        raise Exception("执行异常，退出")

    print("结束---------->" + cmd)
    return result_str


# 写入nginx、v2ray配置
def write_config():
    with open("./nginx/default.conf", "r") as template:
        content = template.read() % (domain, domain, domain, path)
        print(content)

        nginx_config_path = "/etc/nginx/conf.d/default.conf"

        with open(nginx_config_path, "w") as file:
            file.write(content)
    # with open("./v2ray/config.json", "r") as template:
    with open("./v2ray/config_cloudflare_wrap.json", "r") as template:
        content = template.read() % (userid, path)
        print(content)

        v2ray_config_path = "/usr/local/etc/v2ray/config.json"

        with open(v2ray_config_path, "w") as file:
            file.write(content)


if __name__ == '__main__':
    # domain = input("请输入域名：")
    # path = input("请输入路径（不带/）：")
    # userid = input("请输入用户id：")
    # email = input("请输入邮箱：")

    domain = "a.fqym.top"
    path = "uimpaw"
    userid = "75d243ec-2ff5-47a7-8bc4-a5cc932e2950"
    email = "david.suk0614@gmail.com"

    # 获取当前系统信息
    os_release = execute("awk -F= '/^NAME/{print $2}' /etc/os-release")
    # 包管理器
    pak_manager = ""
    # 根据系统区分
    if os_release.__contains__("Ubuntu") or os_release.__contains__("Debian"):
        pak_manager = "apt-get"
        execute(pak_manager + " update")
        # 安装Certbot
        execute(pak_manager + " install -y certbot")
        # 停止防火墙
        execute("ufw disable")
        # 申请SSL证书
        execute("certbot certonly --standalone --agree-tos -n -d %s -m %s" % (domain, email))
        # 安装nginx、v2ray
        execute(pak_manager + " install -y nginx")
        execute(pak_manager + " install -y curl")
        execute(
            "bash -c \"$(curl  -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)\"")

        # 安装仓库 GPG key
        execute(
            "bash -c \"$(curl https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg)\"")
        # 添加CloudFlare WARP客户端源
        execute(
            "echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ bullseye main' | tee /etc/apt/sources.list.d/cloudflare-client.list")
        # 更新源
        execute(pak_manager + " update")
        # 安装CloudFlare WARP客户端
        execute(pak_manager + " -y install cloudflare-warp")
        # 注册客户端
        execute("warp-cli --accept-tos registration new")
        # 设置 WARP 为代理模式(很重要，否则您将无法远程连接 VPS)
        execute("warp-cli --accept-tos set-mode proxy")
        # 启动连接
        execute("warp-cli --accept-tos connect")
        # 保持连接
        # execute("warp-cli enable-always-on")
        #
        write_config()

        # 启动nginx、v2ray
        execute("systemctl enable nginx && systemctl start nginx")
        execute("systemctl enable v2ray && systemctl start v2ray")

        # 自动更新证书
        execute("echo \"0 0 1 */2 * service nginx stop; certbot renew; service nginx start;\" | crontab")

    elif os_release.__contains__("CentOS"):
        pak_manager = "yum"

        # 更新pip
        execute("python3 -m pip install --upgrade pip")
        # 安装Certbot
        execute("pip3 install certbot")
        # 停止防火墙
        execute("systemctl stop firewalld && systemctl disable firewalld")
        # 申请SSL证书
        execute("certbot certonly --standalone --agree-tos -n -d %s -m %s" % (domain, email))
        # 安装nginx、v2ray
        execute(pak_manager + " install -y nginx")
        execute(pak_manager + " install -y curl")
        execute(
            "bash -c \"$(curl  -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)\"")

        write_config()

        # 启动nginx、v2ray
        execute("systemctl enable v2ray && systemctl start v2ray")
        execute("systemctl enable nginx && systemctl sta    rt nginx")

        # 自动更新证书
        execute("echo \"0 0 1 */2 * service nginx stop; certbot renew; service nginx start;\" | crontab")
# todo 自动更新证书
# echo "0 0 1 */2 * service nginx stop; certbot renew; service nginx start;" | crontab
