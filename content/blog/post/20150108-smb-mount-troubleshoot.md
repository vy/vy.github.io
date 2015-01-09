---
kind: article
created_at: 2015-01-08 09:43 EET
title: Troubleshooting a SMB/CIFS Mount Problem
tags:
  - cifs
  - kernel
  - linux
  - samba
---

At every introduction to a new office environment, I spend (waste?) a certain
period of time to connect to network shares through CIFS/SMB. This was not
different at my new work place either. After spending almost two days to
troubleshoot the problem, I figured out that the problem was due to the
missing `/sbin/request-key` binary provided by `keyutils` package in Xubuntu
14.04 LTS. So how did I really get it solved?

Defining the Problem
====================

It is really sick that `cifs` kernel module which is responsible for loading
CIFS/SMB filesystems returns `EINVAL` (that is, `error(22): Invalid argument`)
for an entire family of errors and makes it impossible for the user to spot
the problem. This was also the case for me.

    $ sudo mount \
    	-t cifs //path/to/network/shares /local/mount/point \
    	-o credentials=$HOME/.smbcredentials,iocharset=utf8,rw,uid=$USER,serverino
    mount error(22): Invalid argument
	Refer to the mount.cifs(8) manual page (e.g. man mount.cifs)

So given that the UNC is correct, the local mount point does exist and
accessible, and mount options are valid, `invalid argument` error does not
provide any context for the problem.

Further searching on the internet leaded me to [LinuxCIFS
troubleshooting](https://wiki.samba.org/index.php/LinuxCIFS_troubleshooting)
at Samba Wiki. There it is told that I can enable debug messages for `cifs`
module by echoing a non-zero value to `/proc/fs/cifs/cifsFYI`, hence I did so:

    $ echo 1 | sudo tee /proc/fs/cifs/cifsFYI

And tried to mount the network share again. And observed the following snippet
in the `dmesg` output:

    CIFS VFS: dns_resolve_server_name_to_ip: unable to resolve: path
    CIFS VFS: compose_mount_options: Failed to resolve server part of \\path\to\network\shares to IP

So `dns_resolve_server_name_to_ip` could not resolve `path` for some reason.

DNS at the Kernel-Level
=======================

So how does kernel really resolve domain names to IP addresses? After reading
[`mount.cifs(8)`](http://linux.die.net/man/8/mount.cifs) a couple of times, I
saw *See Also* section telling that
[`Documentation/filesystems/cifs.txt`](https://www.kernel.org/doc/readme/Documentation-filesystems-cifs-README)
in the linux kernel source tree may contain additional options and
information. I checked that too and spotted the following lines:

> DFS support allows transparent redirection to shares in an MS-DFS name
> space. In addition, DFS support for target shares which are specified as UNC
> names which begin with host names (rather than IP addresses) requires a user
> space helper (such as `cifs.upcall`) to be present in order to translate
> host names to ip address, and the user space helper must also be configured
> in the file `/etc/request-key.conf`.  Samba, Windows servers and many NAS
> appliances support DFS as a way of constructing a global name space to ease
> network configuration and improve reliability.
> 
> To use cifs Kerberos and DFS support, the Linux `keyutils` package should be
> installed and something like the following lines should be added to the
> `/etc/request-key.conf` file:
> 
>     create cifs.spnego * * /usr/local/sbin/cifs.upcall %k
>     create dns_resolver * * /usr/local/sbin/cifs.upcall %k

This was getting interesting. I spotted the `dns_resolver` keyword at the
bottom and started reading
[`Documentation/networking/dns_resolver.txt`](https://www.kernel.org/doc/Documentation/networking/dns_resolver.txt)
as well.

> The DNS resolver module provides a way for kernel services to make DNS
> queries by way of requesting a key of key type `dns_resolver`.  These
> queries are upcalled to userspace through `/sbin/request-key`.

The long story short, CIFS module employs DNS resolver module, which
internally upcalls the queries to userspace through `/sbin/request-key`. I got
further curious and checked the `request-key(8)`:

> This  program  is invoked by the kernel when the kernel is asked for a key
> that it doesn't have immediately available. The kernel creates a partially
> set up key and then calls out to this program to instantiate it. It is not
> intended to be called directly.

The Solution
============

Everything was pointing that something was wrong with my `/sbin/request-key`.
Ooops! The binary was not there at all. `apt-file search /sbin/request-key`
told that the binary was provided by `keyutils` package, which was missing in
my system. After installing `keyutils`, I did not observe any DNS resolver
issues in the `dmesg` logs and `mount.cifs` worked without a problem.
