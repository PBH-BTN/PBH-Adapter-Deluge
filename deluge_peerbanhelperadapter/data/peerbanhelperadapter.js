/**
 * Script: peerbanhelperadapter.js
 *     The client-side javascript code for the PeerBanHelperAdapter plugin.
 *
 * Copyright:
 *     (C) azicen 2024 <chenjiazi@aliyun.com>
 *
 *     This file is part of PeerBanHelperAdapter and is licensed under MIT license, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.PeerBanHelperAdapterPage = Ext.extend(Ext.Panel, {
    title: _('PeerBanHelperAdapter'),
    header: false,
    layout: 'fit',
    border: false,
    autoScroll: true,

    initComponent: function () {
        Deluge.ux.preferences.PeerBanHelperAdapterPage.superclass.initComponent.call(this);

        this.BlocklistFset = this.add({
            xtype: 'fieldset',
            border: false,
            title: _('Blocklist'),
            autoHeight: true,
            defaultType: 'editorgrid',
            style: 'margin-top: 3px; margin-bottom: 0px; padding-bottom: 0px;',
            autoWidth: true,
            labelWidth: 0,
            items: [
                {
                    fieldLabel: _(''),
                    name: 'blocklist',
                    margins: '2 0 5 5',
                    height: 320,
                    width: 260,
                    autoExpandColumn: 'ip',
                    viewConfig: {
                        emptyText: _('No IP addresses blocklisted.'),
                        deferEmptyText: false,
                    },
                    colModel: new Ext.grid.ColumnModel({
                        columns: [
                            {
                                id: 'ip',
                                header: _('IP'),
                                dataIndex: 'ip',
                                sortable: true,
                                hideable: false,
                                editable: true,
                                editor: {
                                    xtype: 'textfield',
                                },
                            },
                        ],
                    }),
                    selModel: new Ext.grid.RowSelectionModel({
                        singleSelect: false,
                        moveEditorOnEnter: false,
                    }),
                    store: new Ext.data.ArrayStore({
                        autoDestroy: true,
                        fields: [{ name: 'ip' }],
                    }),
                    listeners: {
                        afteredit: function (e) {
                            e.record.commit();
                        },
                    },
                    setEmptyText: function (text) {
                        if (this.viewReady) {
                            this.getView().emptyText = text;
                            this.getView().refresh();
                        } else {
                            Ext.apply(this.viewConfig, { emptyText: text });
                        }
                    },
                    loadData: function (data) {
                        this.getStore().loadData(data);
                        if (this.viewReady) {
                            this.getView().updateHeaders();
                        }
                    },
                },
            ],
        });

        this.ipButtonsContainer = this.BlocklistFset.add({
            xtype: 'container',
            layout: 'hbox',
            margins: '4 0 0 5',
            items: [
                {
                    xtype: 'button',
                    text: ' Update Block list ',
                    margins: '0 5 0 0',
                },
            ],
        });

        this.updateTask = Ext.TaskMgr.start({
            interval: 30000,
            run: this.onUpdate,
            scope: this,
        });

        this.ipButtonsContainer.getComponent(0).setHandler(this.updateBlocklist, this);
    },

    onUpdate: function () {
        this.updateBlocklist();
    },

    updateBlocklist: function () {
        deluge.client.peerbanhelperadapter.get_blocklist({
            success: function (blocklist) {
                var data = [];
                var ips = blocklist['ips'];
                for (var i = 0; i < ips.length; i++) {
                    data.push([ips[i]]);
                }

                this.BlocklistFset.getComponent(0).loadData(data);
            },
            scope: this,
        });
    },

    onDestroy: function () {
        Ext.TaskMgr.stop(this.updateTask);

        Deluge.ux.preferences.PeerBanHelperAdapterPage.superclass.onDestroy.call(this);
    },
});

PeerBanHelperAdapterPlugin = Ext.extend(Deluge.Plugin, {
    name: 'PeerBanHelperAdapter',

    onDisable: function () {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function () {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.PeerBanHelperAdapterPage()
        );
    },
});

Deluge.registerPlugin('PeerBanHelperAdapter', PeerBanHelperAdapterPlugin);
