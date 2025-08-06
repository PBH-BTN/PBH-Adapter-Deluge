from deluge.core.core import Core as DelugeCore

LISTEN_PORTS_CONFIG_KEY = 'listen_ports'

class Network():

    deluge_core: DelugeCore

    def __init__(self, deluge_core: DelugeCore):
        self.deluge_core = deluge_core

    def get_listen_port(self) -> int:
        """
        获取 Deluge 的监听端口列表
        :return: 监听端口列表
        """
        return self.deluge_core.config[LISTEN_PORTS_CONFIG_KEY][0]

    def set_listen_port(self, port: int) -> None:
        """
        设置 Deluge 的监听端口列表
        :param ports: 监听端口列表
        """
        self.deluge_core.config[LISTEN_PORTS_CONFIG_KEY] = [port, port]

    def __str__(self):
        return f""

    def __repr__(self):
        return f"Network()"
