# -*- coding: utf-8 -*-
# Copyright (C) 2024 azicen <chenjiazi2000@outlook.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of PeerBanHelperAdapter and is licensed under MIT license, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging

from deluge._libtorrent import lt
import deluge.component as component
from deluge.core.filtermanager import FilterManager
from deluge.core.torrentmanager import TorrentManager
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase
from deluge.common import decode_bytes

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    "blocklist": [],
}


class Core(CorePluginBase):
    filtermanager: FilterManager = None
    torrentmanager: TorrentManager = None

    blocklist: set[str] = set()

    def enable(self):
        log.debug("PeerBanHelperAdapter: Plugin enabled...")

        # 获取 libtorrent.session
        self.session = component.get("Core").session
        # 获取 deluge.core.filtermanager.FilterManager 实例
        self.filtermanager = component.get("FilterManager")
        # 获取 deluge.core.torrentmanager.TorrentManager 实例
        self.torrentmanager = component.get("TorrentManager")

        self.config = deluge.configmanager.ConfigManager(
            "peerbanhelper_adapter.conf", DEFAULT_PREFS
        )

        if "blocklist" not in self.config:
            self.config["blocklist"] = []

        self.blocklist = set(self.config["blocklist"])

        # 恢复 blocklist
        ip_filter = self.session.get_ip_filter()
        for ip in self.blocklist:
            ip_filter.add_rule(ip, ip, 1)
        self.session.set_ip_filter(ip_filter)

    def disable(self):
        self.config["blocklist"] = list(self.blocklist)
        self.config.save()

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config:
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        status = {}
        status["blocklist"] = self.blocklist
        return status

    @export
    def get_active_torrents_info(self):
        """返回活跃种子的列表"""

        # 获取活跃的种子列表
        filter_dict = {}
        filter_dict["state"] = ["Active"]
        torrent_ids = self.filtermanager.filter_torrent_ids(filter_dict)

        infos = []

        for torrent_id in torrent_ids:
            info = {}
            torrent = self.torrentmanager[torrent_id]
            info["id"] = torrent_id
            info["name"] = torrent.get_name()
            info["info_hash"] = torrent_id
            info["progress"] = torrent.get_progress()
            info["size"] = torrent.status.total_wanted
            info["upload_payload_rate"] = torrent.status.upload_payload_rate
            info["download_payload_rate"] = torrent.status.download_payload_rate
            peers = torrent.handle.get_peer_info()
            peer_infos = []
            for peer in peers:
                log.debug("peer_id: %s", str(peer.pid))
                # 必须排除半连接状态节点，否则可能进入等待阻塞
                if peer.flags & peer.connecting or peer.flags & peer.handshake:
                    continue
                try:
                    client_name = decode_bytes(peer.client)
                except UnicodeDecodeError:
                    client_name = "unknown"

                peer_info = {
                    "ip": peer.ip[0],
                    "port": peer.ip[1],
                    "peer_id": str(peer.pid),
                    "client_name": client_name,
                    "up_speed": peer.up_speed,  # 上传速度
                    "down_speed": peer.down_speed,  # 下载速度
                    "payload_up_speed": peer.payload_up_speed,  # 有效上传速度
                    "payload_down_speed": peer.payload_down_speed,  # 有效下载速度
                    "total_upload": peer.total_upload,  # 上传量
                    "total_download": peer.total_download,  # 下载量
                    "progress": peer.progress,  # 进度
                    "flags": peer.flags,
                    "source": peer.source,
                    "local_endpoint_ip": peer.local_endpoint[0],
                    "local_endpoint_port": peer.local_endpoint[1],
                    "queue_bytes": peer.queue_bytes,  # 队列字节数
                    "request_timeout": peer.request_timeout,  # 请求超时
                    "num_hashfails": peer.num_hashfails,  # 哈希失败次数
                    "download_queue_length": peer.download_queue_length,  # 下载队列长度
                    "upload_queue_length": peer.upload_queue_length,  # 上传队列长度
                    "failcount": peer.failcount,  # 失败次数
                    "downloading_block_index": peer.downloading_block_index,  # 下载块索引
                    "downloading_progress": peer.downloading_progress,  # 下载进度
                    "downloading_total": peer.downloading_total,  # 下载总量
                    "connection_type": peer.connection_type,  # 连接类型
                    "send_quota": peer.send_quota,  # 发送配额
                    "receive_quota": peer.receive_quota,  # 接收配额
                    "rtt": peer.rtt,  # 往返时间
                    "num_pieces": peer.num_pieces,  # 块数
                    "download_rate_peak": peer.download_rate_peak,  # 下载速率峰值
                    "upload_rate_peak": peer.upload_rate_peak,  # 上传速率峰值
                    "progress_ppm": peer.progress_ppm,  # 进度每分钟百分比
                }

                peer_infos.append(peer_info)

            info["peers"] = peer_infos
            infos.append(info)

        return infos

    @export
    def get_blocklist(self):
        """目前被封禁的所有 IP 列表"""
        result = {
            "size": len(self.blocklist),
            "ips": list(self.blocklist),
        }
        return result

    @export
    def replace_blocklist(self, ips):
        """全量更新 IP 封禁列表

        Args:
            ips (list[str]): 需要封禁的所有 IP 列表
        """
        pend_ips = set(ips)
        # 重新构建 IP 过滤器
        ip_filter = lt.ip_filter()
        for ip in pend_ips:
            ip_filter.add_rule(ip, ip, 1)

        # 更新 LT
        self.session.set_ip_filter(ip_filter)

        self.blocklist.clear()
        self.blocklist.update(pend_ips)
        return {}

    @export
    def ban_ips(self, ips):
        """增量封禁 IP

        Args:
            ips (list[str]): 需要封禁的 IP 列表
        """
        # 待处理的 ip
        pend_ips = set()
        for ip in ips:
            if ip not in self.blocklist:
                pend_ips.add(ip)

        if len(pend_ips) == 0:
            return {}

        ip_filter = self.session.get_ip_filter()
        for ip in pend_ips:
            ip_filter.add_rule(ip, ip, 1)  # 1 阻止通过

        self.session.set_ip_filter(ip_filter)

        self.blocklist.update(pend_ips)
        return {}

    @export
    def unban_ips(self, ips):
        """增量解禁 IP

        Args:
            ips (list[str]): 需要解禁的 IP 列表
        """
        # 待处理的 ip
        pend_ips = set()
        for ip in ips:
            if ip in self.blocklist:
                pend_ips.add(ip)

        if len(pend_ips) == 0:
            return {}

        ip_filter = self.session.get_ip_filter()
        for ip in pend_ips:
            ip_filter.add_rule(ip, ip, 0)  # 0 允许通过，后置规则覆盖

        self.session.set_ip_filter(ip_filter)

        for ip in pend_ips:
            if ip in self.blocklist:
                self.blocklist.remove(ip)
        return {}
