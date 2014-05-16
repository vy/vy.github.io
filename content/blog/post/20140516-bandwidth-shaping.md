---
kind: article
created_at: 2014-05-16 17:05 EET
title: Bandwidth Shaping on Linux
tags:
  - linux
  - networking
---

Networking stack in Linux kernel by default ships an immense set of
functionality that provide every hairy sort of tuning a network administrator
can (and most of the time, cannot) imagine. But unfortunately it totally lacks a
user-friendly interface for the average programmer, not to mention the regular
desktop users.

[![Supported Features](xkcd.png)](http://xkcd.com/619/)

Each time I need to come up with a [`tc`](http://lartc.org/manpages/tc.txt)
one-liner for traffic shaping, I find myself reading [Linux Advanced Routing &
Traffic Control](http://www.lartc.org/) guide (aka. LARTC) all over again. No
exceptions! (Luckily they keep it up to date with the recent kernel versions,
which is something not expected in the GNU/Linux documentation ecosystem.) I
must admit that, it has almost been 16 years since I last used Microsoft Windows
on desktop, but I met with no alternative to the beloved
[NetLimiter](http://www.netlimiter.com/).

[![NetLimiter](netlimiter.png)](http://www.netlimiter.com/)

Fate knocked my door again and this time I am assigned with the task of
providing access to an `iperf` server with two different packet schedulings as
follows.

1. In the first interface, I need to cut down the bandwidth to a certain threshold, e.g., 1Mbps.
2. In the second one, I need to introduce some extra delay to each packet, e.g., 200ms.

Luckily, `iperf` was set to run over TCP and just playing with the egress
packets did suffice.

I first picked the easiest task: adding latency. In this case,
[`netem`](http://www.linuxfoundation.org/collaborate/workgroups/networking/netem)
provides a decent collection of examples and I quickly came up with a working
solution.

    #!bash
    tc qdisc add dev eth0 root netem delay 200ms

For the next task, I skimmed through the [Queueing Disciplines for Bandwidth
Management](http://lartc.org/howto/lartc.qdisc.html) section in LARTC and
figured out a solution.

    #!bash
    tc qdisc add dev eth0 root tbf rate 1024kbit buffer 1600 limit 3000

Is it just me or that has been fairly easy? Later it turned out that it was just
the beginning. Here, the problem is that the above `tc` one-liners take effect
on *every* packet transmitted through `eth0`. So how one can shape just the
`iperf` traffic? After wasting my whole day on this, I came up with the
following `tc` kung-fu.

    tc qdisc add dev eth0 root handle 1: prio
    tc qdisc add dev eth0 parent 1:3 handle 30: netem delay 200ms
    tc filter add dev eth0 protocol ip parent 1:0 u32 match ip sport 34001 0xffff flowid 1:3

That is, I set `iperf` to run on port 34001 and instructed `tc` rule to apply
just for packets outgoing from `sport` 34001.

All said and done, combining both rules (i.e., `netem` and `tbf`) was turned out
to be a nightmare. I even put one of the test servers into an inaccessible state
and needed walk down to the server room to fix the problem by hand. After hours
and hours of try and failures, I finally managed to find a working solution:

    #!bash
    tc qdisc add dev eth0 root handle 1: prio
    tc qdisc add dev eth0 parent 1:2 handle 20: tbf rate 1024kbit buffer 1600 limit 3000
    tc qdisc add dev eth0 parent 1:3 handle 30: netem delay 200ms
    tc filter add dev eth0 protocol ip parent 1: prio 2 route flowid 1:1
    tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip sport 34002 0xffff flowid 1:2
    tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip sport 34003 0xffff flowid 1:3

In this setting, I run two `iperf` instances listening for incoming connections
on ports 34002 and 34003. (First filter directs any unmatched packet to class
`1:1` created by `prio` queue.)

I could have explained the above `tc` snippets in detail and written a couple
more that demonstrate simple use cases for the readers, but believe me, that
would have no points at all. If you have a traffic shaping problem and stucked
with `tc`, you practically have two options: You either (try hard and) find
somebody to do the work for you -- which is the recommended approach, or start
reading the [Terminology](http://lartc.org/howto/lartc.qdisc.terminology.html)
section and make your way through a working solution.

After all this fuss, everytime I read the very first sentence of the [Queueing
Disciplines for Bandwidth Management](http://lartc.org/howto/lartc.qdisc.html)
chapter in LARTC, it makes me smile: **Now, when I discovered this, it really
blew me away.** So true!
