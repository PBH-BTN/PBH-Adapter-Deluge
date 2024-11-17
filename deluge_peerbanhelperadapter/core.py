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
from deluge.common import decode_bytes
from deluge.plugins.pluginbase import CorePluginBase
from deluge.ui.client import client
from datetime import datetime

from deluge_peerbanhelperadapter.model.stats import SessionStatus, PersistenceStatus, LT_STATUS_NAMES
from deluge_peerbanhelperadapter.model.torrent import ActiveTorrent, Peer, Torrent

log = logging.getLogger(__name__)

CONF_KEY_BLOCKLIST = "blocklist"
CONF_KEY_HISTORY_STATUS = "history_status"
CONF_KEY_SESSION_STATUS = "session_status"

DEFAULT_PREFS = {
    CONF_KEY_BLOCKLIST: [],
    CONF_KEY_HISTORY_STATUS: {},
    CONF_KEY_SESSION_STATUS: {},
}


class Core(CorePluginBase):
    # 当前会话状态信息
    session_status: SessionStatus
    # 历史状态信息
    history_status: PersistenceStatus

    filtermanager: FilterManager
    torrentmanager: TorrentManager

    blocklist: set[str] = set()

    def enable(self):
        log.debug("PeerBanHelperAdapter: Plugin enabled...")

        self.session_status = SessionStatus()

        # 获取 libtorrent.session
        self.session = component.get("Core").session
        # 获取 deluge.core.filtermanager.FilterManager 实例
        self.filtermanager = component.get("FilterManager")
        # 获取 deluge.core.torrentmanager.TorrentManager 实例
        self.torrentmanager = component.get("TorrentManager")

        self.config = deluge.configmanager.ConfigManager(
            "peerbanhelper_adapter.conf", DEFAULT_PREFS
        )

        if CONF_KEY_BLOCKLIST not in self.config:
            self.config[CONF_KEY_BLOCKLIST] = []
        if CONF_KEY_HISTORY_STATUS not in self.config:
            self.config[CONF_KEY_HISTORY_STATUS] = {}
        if CONF_KEY_SESSION_STATUS not in self.config:
            self.config[CONF_KEY_SESSION_STATUS] = {}

        self.blocklist = set(self.config[CONF_KEY_BLOCKLIST])
        self.history_status = PersistenceStatus(**self.config[CONF_KEY_HISTORY_STATUS])
        session_status = self.config[CONF_KEY_SESSION_STATUS]

        if len(session_status) > 0:
            # 异常中断后恢复数据
            self.history_status = self.history_status + session_status
            self.config[CONF_KEY_HISTORY_STATUS] = self.history_status.persistence_dist()
            self.config[CONF_KEY_SESSION_STATUS] = {}
            self.config.save()

        # 恢复 blocklist
        ip_filter = self.session.get_ip_filter()
        for ip in self.blocklist:
            ip_filter.add_rule(ip, ip, 1)
        self.session.set_ip_filter(ip_filter)

    def disable(self):
        self.config[CONF_KEY_BLOCKLIST] = list(self.blocklist)

        session_status = PersistenceStatus(**self.session_status.persistence_dist())
        self.history_status = self.history_status + session_status
        self.config[CONF_KEY_HISTORY_STATUS] = self.history_status.persistence_dist()
        self.config[CONF_KEY_SESSION_STATUS] = {} # 清空

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
        status[CONF_KEY_BLOCKLIST] = self.blocklist
        return status

    @export
    def get_active_torrents_info(self):
        """返回活跃种子的列表"""

        # 获取活跃的种子列表
        filter_dict = {}
        filter_dict["state"] = ["Active"]
        torrent_ids = self.filtermanager.filter_torrent_ids(filter_dict)

        active_torrents = []

        for torrent_id in torrent_ids:
            torrent = ActiveTorrent()
            deluge_torrent = self.torrentmanager[torrent_id]
            torrent.id = torrent_id
            torrent.name = deluge_torrent.get_name()
            torrent.info_hash = torrent_id
            torrent.progress = deluge_torrent.get_progress()
            torrent.completed_size = deluge_torrent.status.total_wanted_done
            torrent.upload_payload_rate = deluge_torrent.status.upload_payload_rate
            torrent.download_payload_rate = deluge_torrent.status.download_payload_rate
            # LT torrent_info
            torrent_info = deluge_torrent.handle.torrent_file()
            torrent.priv = torrent_info.priv()
            torrent.size = torrent_info.total_size()
            # LT peer_info
            lt_peers = deluge_torrent.handle.get_peer_info()
            peers = []
            for lt_peer in lt_peers:
                log.debug("peer_id: %s", str(lt_peer.pid))
                # 必须排除半连接状态节点，否则可能进入等待阻塞
                if lt_peer.flags & lt_peer.connecting or lt_peer.flags & lt_peer.handshake:
                    continue
                try:
                    client_name = decode_bytes(lt_peer.client)
                except UnicodeDecodeError:
                    client_name = "unknown"

                peer = Peer(
                    ip=lt_peer.ip[0],
                    port=lt_peer.ip[1],
                    peer_id=str(lt_peer.pid),
                    client_name=client_name,
                    up_speed=lt_peer.up_speed,
                    down_speed=lt_peer.down_speed,
                    payload_up_speed=lt_peer.payload_up_speed,
                    payload_down_speed=lt_peer.payload_down_speed,
                    total_upload=lt_peer.total_upload,
                    total_download=lt_peer.total_download,
                    progress=lt_peer.progress,
                    flags=lt_peer.flags,
                    source=lt_peer.source,
                    local_endpoint_ip=lt_peer.local_endpoint[0],
                    local_endpoint_port=lt_peer.local_endpoint[1],
                    queue_bytes=lt_peer.queue_bytes,
                    request_timeout=lt_peer.request_timeout,
                    num_hashfails=lt_peer.num_hashfails,
                    download_queue_length=lt_peer.download_queue_length,
                    upload_queue_length=lt_peer.upload_queue_length,
                    failcount=lt_peer.failcount,
                    downloading_block_index=lt_peer.downloading_block_index,
                    downloading_progress=lt_peer.downloading_progress,
                    downloading_total=lt_peer.downloading_total,
                    connection_type=lt_peer.connection_type,
                    send_quota=lt_peer.send_quota,
                    receive_quota=lt_peer.receive_quota,
                    rtt=lt_peer.rtt,
                    num_pieces=lt_peer.num_pieces,
                    download_rate_peak=lt_peer.download_rate_peak,
                    upload_rate_peak=lt_peer.upload_rate_peak,
                    progress_ppm=lt_peer.progress_ppm,
                )

                peers.append(peer)

            torrent.peers = peers
            active_torrents.append(torrent.dist())

        return active_torrents

    @export
    def get_torrents_info(self):
        """返回所有种子的列表"""
        torrent_ids = self.filtermanager.filter_torrent_ids(filter_dict={})

        torrents = []

        for torrent_id in torrent_ids:
            torrent = Torrent()
            deluge_torrent = self.torrentmanager[torrent_id]
            torrent.id = torrent_id
            torrent.name = deluge_torrent.get_name()
            torrent.info_hash = torrent_id
            torrent.progress = deluge_torrent.get_progress()
            torrent.completed_size = deluge_torrent.status.total_wanted_done
            # LT torrent_info
            torrent_info = deluge_torrent.handle.torrent_file()
            torrent.priv = torrent_info.priv()
            torrent.size = torrent_info.total_size()

            torrents.append(torrent.dist())

        return torrents

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

    @export
    def get_history_status(self):
        return self.history_status.dist()

    @export
    def get_session_totals(self):
        """获取会话统计信息"""

        def update_status(lt_stats):
            now_datetime = datetime.now()
            stats_last_datetime = datetime.fromtimestamp(self.session_status.stats_last_timestamp)
            # 计算时间间隔
            interval = (now_datetime - stats_last_datetime).total_seconds()
            if interval <= 0:
                return

            self.session_status.stats_last_timestamp = int(now_datetime.timestamp())

            ip_overhead_download = lt_stats.get('net.recv_ip_overhead_bytes')
            ip_overhead_upload = lt_stats['net.sent_ip_overhead_bytes']
            total_download = lt_stats['net.recv_bytes'] + ip_overhead_download
            total_upload = lt_stats['net.sent_bytes'] + ip_overhead_upload
            total_payload_download = lt_stats['net.recv_payload_bytes']
            total_payload_upload = lt_stats['net.sent_payload_bytes']
            tracker_download = lt_stats['net.recv_tracker_bytes']
            tracker_upload = lt_stats['net.sent_tracker_bytes']
            dht_download = lt_stats['dht.dht_bytes_in']
            dht_upload = lt_stats['dht.dht_bytes_out']

            def calc_rate(previous, current) -> float:
                assert current >= previous, "当前值应当大于或等于前一值"
                assert interval > 0, "间隔应为正数"
                return (current - previous) / interval

            self.session_status.payload_download_rate = calc_rate(self.session_status.total_payload_download, total_payload_download)
            self.session_status.payload_upload_rate = calc_rate(self.session_status.total_payload_upload, total_payload_upload)
            self.session_status.download_rate = calc_rate(self.session_status.total_download, total_download)
            self.session_status.upload_rate = calc_rate(self.session_status.total_upload, total_upload)
            self.session_status.ip_overhead_download_rate = calc_rate(self.session_status.ip_overhead_download, ip_overhead_download)
            self.session_status.ip_overhead_upload_rate = calc_rate(self.session_status.ip_overhead_upload, ip_overhead_upload)
            self.session_status.dht_download_rate = calc_rate(self.session_status.dht_download, dht_download)
            self.session_status.dht_upload_rate = calc_rate(self.session_status.dht_upload, dht_upload)
            self.session_status.tracker_download_rate = calc_rate(self.session_status.tracker_download, tracker_download)
            self.session_status.tracker_upload_rate = calc_rate(self.session_status.tracker_upload, tracker_upload)

            self.session_status.total_payload_download = total_payload_download
            self.session_status.total_payload_upload = total_payload_upload
            self.session_status.total_download = total_download
            self.session_status.total_upload = total_upload
            self.session_status.ip_overhead_download = ip_overhead_download
            self.session_status.ip_overhead_upload = ip_overhead_upload
            self.session_status.tracker_download = tracker_download
            self.session_status.tracker_upload = tracker_upload
            self.session_status.dht_download = dht_download
            self.session_status.dht_upload = dht_upload

            # 被丢弃的重复下载字节数（从不同的对等节点下载） + 因哈希校验失败而丢弃的已下载字节数
            self.session_status.total_wasted = lt_stats['net.recv_redundant_bytes'] + lt_stats['net.recv_failed_bytes']
            self.session_status.dht_nodes = lt_stats['dht.dht_nodes']
            self.session_status.disk_read_queue = lt_stats['peer.num_peers_up_disk']
            self.session_status.disk_write_queue = lt_stats['peer.num_peers_down_disk']
            self.session_status.peers_count = lt_stats["peer.num_peers_connected"]

            # 30分钟写盘一次
            if interval > 1800:
                self.config[CONF_KEY_SESSION_STATUS] = self.session_status.persistence_dist()
                self.config.save()

        lt_status_call = client.core.get_session_status(LT_STATUS_NAMES)
        lt_status_call.addCallback(update_status)

        # 合并会话状态和历史状态
        status = SessionStatus(**self.session_status.dist())
        status = status + self.history_status

        return status.dist()
