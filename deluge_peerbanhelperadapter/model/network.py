from dataclasses import dataclass

from deluge_peerbanhelperadapter.model.base import BaseModel

@dataclass
class NetworkData(BaseModel):
    # 监听端口列表
    listen_port: int
