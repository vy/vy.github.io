---
kind: article
created_at: 2012-02-23 04:25 EET
title: Synchronization Between JGroups.ReplicatedHashMap's
tags:
  - java
  - jgroups
---

[`ReplicatedHashMap`](http://www.jgroups.org/javadoc/org/jgroups/blocks/ReplicatedHashMap.html) of [JGroups](http://www.jgroups.org/) provides a distributed [`ConcurrentHashMap`](http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/ConcurrentHashMap.html) implementation. In its simplest form, it propagates every local change to all other instances in the cluster and you get your replicated-HashMap between available cluster members.

In a cluster environment, new node arrivals are highly anticipated, but `ReplicatedHashMap` doesn't really keep up with the late joiners. See below execution flow for a late joiner scenario.

|Time|Node A       |Node B     |
|:--:|-------------|-----------|
|1   |join         |           |
|2   |send 1       |           |
|3   |recv 1       |           |
|4   |observe {1}  |           |
|5   |             |join       |
|6   |             |observe {} |
|7   |             |send 2     |
|8   |recv 2       |recv 2     |
|9   |observe {1,2}|observe {2}|

In the above figure, nodes are out of sync at time steps 6 and 9. To avoid such cases, we need to force `ReplicatedHashMap` for a sync during initialization. For this purpose, quoting with Bela Ban's (author of JGroups) words,

1. Move `JChannel.connect()` after the creation of `ReplicatedHashMap`,
2. I also suggest to call `ReplicatedHashmap.start()`, or else there won't be any state transfer.

See [ReplicatedHashMap Updates for Late Joiners](http://comments.gmane.org/gmane.comp.java.javagroups.general/7665) post in the mailing-list for the related discussion.
