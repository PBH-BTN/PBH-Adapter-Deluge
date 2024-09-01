from dataclasses import dataclass, asdict, fields
from datetime import datetime

LT_STATUS_NAMES = [
    "net.sent_payload_bytes",
    "net.sent_bytes",
    "net.sent_ip_overhead_bytes",
    "net.sent_tracker_bytes",
    "net.recv_payload_bytes",
    "net.recv_bytes",
    "net.recv_ip_overhead_bytes",
    "net.recv_tracker_bytes",
    "net.limiter_up_bytes",
    "net.limiter_down_bytes",
    "net.recv_redundant_bytes",
    "net.recv_failed_bytes",
    "dht.dht_bytes_in",
    "dht.dht_bytes_out",
    "dht.dht_nodes",
    "peer.num_peers_up_disk",
    "peer.num_peers_down_disk",
    "peer.num_peers_connected",
]


@dataclass
class PersistenceStatus:
    # 最后统计时间戳
    stats_last_timestamp: int = int(datetime.now().timestamp())

    # 接收的有效载荷字节数(recv_payload_bytes)
    total_payload_download: int = 0

    # 发送的有效载荷字节(sent_payload_bytes)
    total_payload_upload: int = 0

    # 接收IP开销字节(recv_ip_overhead_bytes)
    ip_overhead_download: int = 0

    # 发送IP开销字节(sent_ip_overhead_bytes)
    ip_overhead_upload: int = 0

    # 接收追踪器字节(recv_tracker_bytes)
    tracker_download: int = 0

    # 发送追踪器字节(sent_tracker_bytes)
    tracker_upload: int = 0

    # DHT 接收字节(dht_bytes_in)
    dht_download: int = 0

    # DHT 发送字节(dht_bytes_out)
    dht_upload: int = 0

    # 总丢弃字节(重复下载丢弃字节数 + 哈希校验失败丢弃字节数)
    # recv_redundant_bytes + recv_failed_bytes
    total_wasted: int = 0

    # 总下载量
    total_download: int = 0

    # 总上传量
    total_upload: int = 0

    def __add__(self, other):
        # 实现两个 Vector 对象的相加
        if isinstance(other, PersistenceStatus):
            self.total_payload_download = self.total_payload_download + other.total_payload_download
            self.total_payload_upload = self.total_payload_upload + other.total_payload_upload
            self.ip_overhead_download = self.ip_overhead_download + other.ip_overhead_download
            self.ip_overhead_upload = self.ip_overhead_upload + other.ip_overhead_upload
            self.tracker_download = self.tracker_download + other.tracker_download
            self.tracker_upload = self.tracker_upload + other.tracker_upload
            self.dht_download = self.dht_download + other.dht_download
            self.dht_upload = self.dht_upload + other.dht_upload
            self.total_wasted = self.total_wasted + other.total_wasted
            self.total_download = self.total_download + other.total_download
            self.total_upload = self.total_upload + other.total_upload
            return self
        return NotImplemented

    def persistence_dist(self) -> dict:
        return asdict(self)

    def dist(self) -> dict:
        return asdict(self)


_persistence_fields = {field.name for field in fields(PersistenceStatus)}


@dataclass
class SessionStatus(PersistenceStatus):
    # 有效载荷下载速率
    payload_download_rate: int = 0

    # 有效载荷上传速率
    payload_upload_rate: int = 0

    # 下载速率
    download_rate: int = 0

    # 上传速率
    upload_rate: int = 0

    # IP 开销下载速率
    ip_overhead_download_rate: int = 0

    # IP 开销上传速率
    ip_overhead_upload_rate: int = 0

    # DHT 下载速率
    dht_download_rate: int = 0

    # DHT 上传速率
    dht_upload_rate: int = 0

    # Tracker 下载速率
    tracker_download_rate: int = 0

    # Tracker 上传速率
    tracker_upload_rate: int = 0

    # DHT 路由表中的节点数量
    dht_nodes: int = 0

    # 上传磁盘对等点数量(num_peers_up_disk)
    disk_read_queue: int = 0

    # 下载磁盘对等点数量(num_peers_down_disk)
    disk_write_queue: int = 0

    # 已连接的对等方数量(num_peers_connected)
    peers_count: int = 0


    def persistence_dist(self) -> dict:
        dist = asdict(self)
        return {field: dist[field] for field in _persistence_fields}
