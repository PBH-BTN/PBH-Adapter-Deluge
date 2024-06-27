/**
 * Script: peerbanhelperadapter.js
 *     The client-side javascript code for the PeerBanHelperAdapter plugin.
 *
 * Copyright:
 *     (C) azicen 2024 <chenjiazi2000@outlook.com>
 *
 *     This file is part of PeerBanHelperAdapter and is licensed under MIT license, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

PeerBanHelperAdapterPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'PeerBanHelperAdapter'
        }, config);
        PeerBanHelperAdapterPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.PeerBanHelperAdapterPage());
    }
});
new PeerBanHelperAdapterPlugin();
