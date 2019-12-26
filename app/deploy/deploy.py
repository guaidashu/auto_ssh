"""
Create by yy on 2019/12/25
"""
import sys
import getopt

import paramiko
from tool_yy import debug, Thread
from app.config import server_config

__all__ = ["AutoDeploy"]


class AutoDeploy(Thread):
    def __init__(self, init_db):
        super().__init__()
        self.db = init_db('AUTODEPLOY')

    def run(self):
        # 命令行参数
        pk = ""
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hk:", ["pem_key="])
        except:
            print("deploy.py -k <pem_key_filename>")
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-h":
                print("deploy.py -k <pem_key_filename>")
                sys.exit()
            elif opt in ("-k", "--pem_key_filename"):
                pk = arg

        # 从配置文件获取 服务器地址
        server_list = server_config.server_list
        self.start_thread(server_list, self.ssh_start, max_worker=5, is_test=False, pk=pk)

    def ssh_start(self, server, pk):
        # 创建ssh对象
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        username = "root"
        port = 22

        try:
            port = server["port"]
        except:
            pass

        try:
            username = server["user"]
        except:
            pass

        try:
            pk = server["key_path"]
        except:
            pass

        # 判断是否传入了
        debug(server)
        if pk == "":
            ssh.connect(hostname=server["host"], port=port, username=username)
        else:
            ssh.connect(hostname=server["host"], port=port, username=username, key_filename=pk)

        cmd = self.get_cmd()

        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()

        if not result:
            result = stderr.read()
        ssh.close()

        debug(result.decode())

    def get_cmd(self):
        """
        获取要执行的命令
        :return:
        """
        return "ls"
