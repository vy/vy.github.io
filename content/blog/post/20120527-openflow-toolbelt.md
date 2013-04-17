---
kind: article
created_at: 2012-05-27 09:58 EET
title: "OpenVSwitch Installation Notes: OpenFlow Toolbelt"
tags:
  - openflow
  - openvswitch
  - sdn
---

In the lab, I quite often find my self installing [Open vSwitch](http://www.openvswitch.org/) instances, configuring network parameters for certain functionality and probing network interfaces to check connectivity, again and again. You know, the daily routines in an [OpenFlow](http://www.openflow.org/) research laboratory. To ease the workflow, I put together a small *toolbelt*.

    #!bash
    $ of-toolbelt.sh
    Usage: of-toolbelt.sh <ACTION>
    Actions: ofctl
             vsctl
             vswitchd
             insmod
             db_create
             db_start
             get_controller
             set_controller
             del_controller
             get_dpid
             set_dpid
             get_stp
             set_stp
             dl_ovs
             install_ovs
             ethtool_help
             arping_help
    $ of-toolbelt.sh dl_ovs
    $ of-toolbelt.sh install_ovs openvswitch-1.4.1.tar.gz
    $ of-toolbelt.sh db_create
    $ of-toolbelt.sh db_start
    $ of-toolbelt.sh vsctl add-br br0
    $ of-toolbelt.sh set_dpid br0 1
    $ of-toolbelt.sh get_dpid br0
    "0000000000000001"
    $ of-toolbelt.sh get_stp br0
    false
    $ of-toolbelt.sh set_stp br0 true
    $ of-toolbelt.sh insmod
    $ of-toolbelt.sh vswitchd
    $ of-toolbelt.sh ethtool_help
    ethtool eth0
    ethtool -s eth0 speed 10 duplex full autoneg off
    ethtool -s eth0 autoneg on
    ethtool -s eth0 autoneg on adver 0x001    # 10 Half
                                     0x002    # 10 Full
                                     0x004    # 100 Half
                                     0x008    # 100 Full
                                     0x010    # 1000 Half(not supported by IEEE standards)
                                     0x020    # 1000 Full
                                     0x8000   # 2500 Full(not supported by IEEE standards)
                                     0x1000   # 10000 Full
                                     0x03F    # Auto
    $ sudo ethtool -s eth0 speed 10 duplex half autoneg off
    $ of-toolbelt.sh vsctl add-port br0 eth0

You can find the sources in the following gist. Feel free to use it for your own purpose. (*Free* as in *free beer*.) No need to say but here it goes: Comments/Contributions are highly welcome.

<script src="https://gist.github.com/2814489.js?file=of-toolbelt.sh"></script>
