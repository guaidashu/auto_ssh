"""
Create by yy on 2019/12/25
"""
import sys
import getopt
import threading

import paramiko
from tool_yy import debug, Thread

__all__ = ["AutoDeploy"]

lock = threading.RLock()


class AutoDeploy(Thread):
    def __init__(self, init_db):
        super().__init__()
        self.db = init_db('AUTODEPLOY')
        self.script_id = 1
        self.cmd = self.get_cmd()

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
        server_list = self.get_server_list()
        results = self.start_thread(server_list, self.ssh_start, is_test=False, pk=pk)
        # debug(results)

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
        if pk == "":
            ssh.connect(hostname=server["host"], port=port, username=username)
        else:
            ssh.connect(hostname=server["host"], port=port, username=username, key_filename=pk)

        stdin, stdout, stderr = ssh.exec_command(self.cmd)
        result = stdout.read()

        if not result:
            result = stderr.read()
        ssh.close()

        return result

    def get_cmd(self):
        """
        获取要执行的命令
        :return:
        """
        lock.acquire()
        data = self.db.select({
            "table": "script",
            "condition": ["id={id}".format(id=self.script_id)]
        }, is_close_db=False, get_all=False)
        lock.release()
        try:
            data = data["content"]
        except:
            data = "echo cmd is null"
        return data

    def get_server_list(self):
        lock.acquire()
        server_list = self.db.select({
            "table": "server_list",
            "condition": ["is_execute=1", "and", "status=1"]
        }, is_close_db=False)
        lock.release()
        return server_list
