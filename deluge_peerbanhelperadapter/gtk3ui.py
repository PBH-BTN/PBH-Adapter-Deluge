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

from gi.repository import Gtk

import deluge.component as component
from deluge.plugins.pluginbase import Gtk3PluginBase
from deluge.ui.client import client

from .common import get_resource

log = logging.getLogger(__name__)


class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource("config.ui"))

        component.get("Preferences").add_page(
            "PeerBanHelperAdapter", self.builder.get_object("prefs_box")
        )
        component.get("PluginManager").register_hook(
            "on_apply_prefs", self.on_apply_prefs
        )
        component.get("PluginManager").register_hook(
            "on_show_prefs", self.on_show_prefs
        )

    def disable(self):
        component.get("Preferences").remove_page("PeerBanHelperAdapter")
        component.get("PluginManager").deregister_hook(
            "on_apply_prefs", self.on_apply_prefs
        )
        component.get("PluginManager").deregister_hook(
            "on_show_prefs", self.on_show_prefs
        )

    def on_apply_prefs(self):
        log.debug("applying prefs for PeerBanHelperAdapter")
        # client.peerbanhelperadapter.set_config(config)
        client.peerbanhelperadapter.get_config().addCallback(self.cb_get_config)

    def on_show_prefs(self):
        client.peerbanhelperadapter.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        """callback for on show_prefs"""
        blocklist = config["blocklist"]
        self.update_text_blocklist(blocklist)

    def update_text_blocklist(self, blocklist):
        if not blocklist:
            return
        text = '\n'.join([ip for ip in blocklist])
        self.builder.get_object("text_blocklist").get_buffer().set_text(text, len(text))
