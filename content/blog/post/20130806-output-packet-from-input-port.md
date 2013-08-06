---
kind: article
created_at: 2013-08-06 19:29 EET
title: How come a packet gets output from its input port?
tags:
  - networking
  - openflow
  - sdn
---

A couple of weeks ago I spotted a really suspicious flow in the logs that directly made me think of a bug at the controller. A packet was arriving to a port of a switch and was getting output from the very same port of the switch. This was kind of weird. If it is supposed to be transmitted back again, then why was it ended up here in the first hand? Was it because of a bug at the controller that first redirected the packet to the switch and then redirected it backwards to the previous switch? A logical fault at the controller was definitely the first suspect here. But later it turned out that this was not the case. The details are as follows.

![SDN Topology](topology.jpg)

Consider the above topology, where three switches `s1`, `s2`, `s3` are connected linearly and all together managed by the controller `c1`. In addition, `s1` and `s2` is connected to two hosts `h1` and `h2`, respectively. The controller, switches, hosts, their connections, and connection port numbers are given in the figure. The scenario generating the subtle gotcha is as follows.

1. `h2` sends a packet destined to `h1`, whose attachment point is not learnt yet by `c1`.
2. Hence, upon arrival of the packet from `s2`, `c1` commands `s2` to flood the request.
3. The flooded request goes to `s1` and `s3`.
4. Upon arrival of the packet to `s1`, `s1` sends the packet to `c1` again.
5. Since `c1` still does not know the attachment point of `h1`, `c1` commands `s1` to flood the request for a second time.
6. Flooded request from `s1` reaches to `h1` and `h1` replies back.
7. With `h1`s response, `c1` learns the attachment point of `h1`.
8. In the meantime, `s2`s flood (see 3rd step) reaches to `s3`
9. Now `c1` knows the attachment point of the `h1`. Consequently, `c1` figures out that the route to `h1` goes through `s1` and `s1` is reachable by `p1` of `s3`. Hence, `c1` commands `s3` to output the packet from the very same input port of the packet.

I do not have a single idea about the probability of such a subtle bug, but somehow it happened to exist in my logs, right at the lines I was just taking a glance and wasted my whole day. The saying was right, network is really unreliable. Gorgeous!
