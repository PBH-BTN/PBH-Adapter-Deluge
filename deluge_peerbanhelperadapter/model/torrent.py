from dataclasses import asdict, dataclass, field
from typing import List

from deluge_peerbanhelperadapter.model.base import BaseModel


@dataclass
class Peer(BaseModel):
    ip: str = ""
    port: int = 0
    peer_id: str = ""
    client_name: str = ""
    # 上传速度
    up_speed: int = 0
    # 下载速度
    down_speed: int = 0
    # 有效上传速度
    payload_up_speed: int = 0
    # 有效下载速度
    payload_down_speed: int = 0
    # 上传量
    total_upload: int = 0
    # 下载量
    total_download: int = 0
    # 进度
    progress: float = 0
    flags: int = 0
    source: int = 0
    local_endpoint_ip: str = ""
    local_endpoint_port: int = 0
    # 队列字节数
    queue_bytes: int = 0
    # 请求超时
    request_timeout: int = 0
    # 哈希失败次数
    num_hashfails: int = 0
    # 下载队列长度
    download_queue_length: int = 0
    # 上传队列长度
    upload_queue_length: int = 0
    # 失败次数
    failcount: int = 0
    # 下载块索引
    downloading_block_index: int = 0
    # 下载进度
    downloading_progress: int = 0
    # 下载总量
    downloading_total: int = 0
    # 连接类型
    connection_type: int = 0
    # 发送配额
    send_quota: int = 0
    # 接收配额
    receive_quota: int = 0
    # 往返时间
    rtt: int = 0
    # 块数
    num_pieces: int = 0
    # 下载速率峰值
    download_rate_peak: int = 0
    # 上传速率峰值
    upload_rate_peak: int = 0
    # 进度每分钟百分比
    progress_ppm: int = 0

    def dist(self) -> dict:
        return asdict(self)

@dataclass
class Torrent(BaseModel):
    id: str = ""
    name: str = ""

    # 种子hash
    info_hash: str = ""

    # 进度
    progress: float = 0

    # 种子大小
    size: int = 0

    # 已下载的大小
    completed_size: int = 0

    # 是否为私有种子
    priv: bool = False

    def dist(self) -> dict:
        return asdict(self)


@dataclass
class ActiveTorrent(Torrent):
    # 有效上传速率
    upload_payload_rate: int = 0

    # 有效下载速率
    download_payload_rate: int = 0

    peers: List[Peer] = field(default_factory=list)
