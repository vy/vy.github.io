---
kind: article
created_at: 2014-01-03 21:19 EET
title: Sockets, TCP Keep Alive and TIME_WAIT
modules:
  - twitter
tags:
  - java
  - link
---

Time to time I share some technical links on Twitter and let them get lost in the internet junk yard. I thought it might be a better idea to archive them on my blog in a more organized fashion. (I will group such posts under tag <%= link_to("link", tag_identifier("link")) %>.) This way they will at least be more accessible by myself. This post is my first effort towards this goal. (Sorry for the ugly Twitter embeddings. I find some 3rd party libraries to configure the display, but that stuff usually gets broken in the long run due to changes in the Twitter API.)

Last month I have been bitten seriously by a software bug caused by `TIME_WAIT` sockets. Below is the list of links I found useful in the pursuit of trying to solve the problem.

<blockquote class="twitter-tweet" lang="en" data-conversation="none" data-cards="hidden"><p>Multi-platform <a href="https://twitter.com/search?q=%23TCP&amp;src=hash">#TCP</a> Keep Alive guide: <a href="http://t.co/uEukpMrCEV">http://t.co/uEukpMrCEV</a> <a href="https://twitter.com/search?q=%23bsd&amp;src=hash">#bsd</a> <a href="https://twitter.com/search?q=%23linux&amp;src=hash">#linux</a> <a href="https://twitter.com/search?q=%23solaris&amp;src=hash">#solaris</a> <a href="https://twitter.com/search?q=%23windows&amp;src=hash">#windows</a> <a href="https://twitter.com/search?q=%23osx&amp;src=hash">#osx</a></p>&mdash; Volkan Yazıcı (@yazicivo) <a href="https://twitter.com/yazicivo/statuses/413989234052067328">December 20, 2013</a></blockquote>

<blockquote class="twitter-tweet" lang="en" data-conversation="none" data-cards="hidden"><p>The ultimate guide to socket/bind/connect: <a href="http://t.co/7YjSiIfWnX">http://t.co/7YjSiIfWnX</a> <a href="https://twitter.com/search?q=%23bsd&amp;src=hash">#bsd</a> <a href="https://twitter.com/search?q=%23linux&amp;src=hash">#linux</a> <a href="https://twitter.com/search?q=%23unix&amp;src=hash">#unix</a> <a href="https://twitter.com/search?q=%23network&amp;src=hash">#network</a> <a href="https://twitter.com/search?q=%23programming&amp;src=hash">#programming</a></p>&mdash; Volkan Yazıcı (@yazicivo) <a href="https://twitter.com/yazicivo/statuses/413970759489294336">December 20, 2013</a></blockquote>

<blockquote class="twitter-tweet" lang="en"><p>Suffering from <a href="https://twitter.com/search?q=%23TIME_WAIT&amp;src=hash">#TIME_WAIT</a> <a href="https://twitter.com/search?q=%23sockets&amp;src=hash">#sockets</a> while trying to handle thousands of connections? Enabled tcp_tw_recycle? <a href="http://t.co/XGdPYNibGE">http://t.co/XGdPYNibGE</a> <a href="https://twitter.com/search?q=%23linux&amp;src=hash">#linux</a></p>&mdash; Volkan Yazıcı (@yazicivo) <a href="https://twitter.com/yazicivo/statuses/413967038147612672">December 20, 2013</a></blockquote>
