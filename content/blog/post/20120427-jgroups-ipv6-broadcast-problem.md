---
kind: article
created_at: 2012-04-27 12:53 EET
title: JGroups IPv6 Broadcast Problem
tags:
  - java
  - groups
---

Here is a quick tip: Do you regularly observe below _harmless_ JGroups message send failures?

    09:49:02.270 [Timer-3,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (95 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (98 bytes), cause: java.io.IOException: Network is unreachable
    09:49:03.132 [Timer-4,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (95 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (98 bytes), cause: java.io.IOException: Network is unreachable
    09:49:04.111 [Timer-5,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (84 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (87 bytes), cause: java.io.IOException: Network is unreachable
    09:49:04.328 [Timer-3,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (91 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (94 bytes), cause: java.io.IOException: Network is unreachable
    09:49:05.281 [Timer-4,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (91 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (94 bytes), cause: java.io.IOException: Network is unreachable
    09:49:06.331 [Timer-3,<ADDR>] ERROR org.jgroups.protocols.UDP - failed sending message to cluster (74 bytes): java.lang.Exception: dest=/ff0e:0:0:0:0:8:8:8:45588 (77 bytes), cause: java.io.IOException: Network is unreachable

As Bela Ban [says](http://article.gmane.org/gmane.comp.java.javagroups.general/7932),

> Your messages are sent to an IPv6 multicast address; is this what you want? If not, and you want to force use of IPv4, use `-Djava.net.preferIPv4Stack=true`. If you want to use IPv6, make sure your routing table is set up correctly.
