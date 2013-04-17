---
kind: article
created_at: 2013-04-14 18:36 EET
title: Migrating from Blogspot to Nanoc
tags:
  - blog
  - nanoc
---

For a pretty long time, [my personal website](http://web.itu.edu.tr/~yazicivo/) at İstanbul Technical University had become my attachment point with the rest of the web. Later, it is followed by [GitHub](https://github.com/vy) and [Twitter](https://twitter.com/yazicivo) accounts. And then in the race of trying to keep up with the internet evolution, I started writing in [Blogspot](http://vyazici.blogspot.com/). All that being said, from the very beginning I (ironically) always wanted to have a single entry point to the content originating by me. This blog post marks my first attempt in this pursuit.

The startling point was Blogspot, oh yeah. First I started to type HTML by hand. Then it led to me find a JavaScript library to syntax highlight the code I share. Finally, I found myself trying to escape HTML characters within the shared code snippets. At some point I decided to use [Gist](https://gist.github.com/)s. Later a reader complaint pointed out that shared Gists were not properly displayed on mobile browsers.

After some research, I met with [nanoc](http://nanoc.ws/). A tiny static site generator written in Ruby. I have never used Ruby before but it didn't take long for me to built this website in a couple of days. Thanks to the excellent documentation and the active community of nanoc. I might talk more about the obstacles that I experience during the transition, but to be honest none of the friction was due to the nanoc. (The words of [Bob Ross](http://en.wikipedia.org/wiki/Bob_Ross) describes this best: _"We don't make mistakes, just happy little accidents"_.) Instead, I invite you to check [the code](https://github.com/vy/vy.github.io/tree/source) by yourself. I hope it helps other nanoc users out there.
