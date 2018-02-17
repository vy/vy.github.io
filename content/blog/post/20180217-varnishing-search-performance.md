---
kind: article
created_at: 2018-02-17 20:42 CEST
title: Varnishing Search Performance
tags:
  - elasticsearch
  - presentation
---

This week [bol.com](http://bol.com) hosted an [Elastic User Group
NL](https://www.meetup.com/Elastic-NL/) meetup titled [bol.com: Changing the
(search) engine of a racecar going 300 km/h](https://www.meetup.com/Elastic-NL/events/247114723/).
The abstract of the presentations were as follows:

> Almost 2 years ago bol.com decided to move towards an
> Elasticsearch-powered search engine. But how do you approach such a
> project? Who do you involve and what do you need to (not) do? The
> engineers at bol.com would like to share their experiences about this
> migration, in 4 short talks.

And among those 4 short talks, I took the stage with *Varnishing Search Performance*.

> Searching is *peanuts*. You setup your Elasticsearch cluster (or better
> find a SaaS partner) and start shooting your search queries against it.
> Well... Not really. If we put the biblical data ingestion story aside, it
> won't take long to realize that even moderately complicated queries can
> become a bottleneck for those aiming for &lt;50ms query performance.
> Combine a couple of aggregations, double that for facets of range type,
> add your grandpa's boosting factors to the scoring, and there you go;
> now you are a search query performance bottleneck owner too! Maybe I am
> exaggerating a bit. Why not just start throwing some caches in front of
> it? Hrm... We actually thought of that and did so. Though it brought a
> mountain of problems along with itself, and there goes my story.

The slides are available in [PDF](varnishing-search-performance.pdf) and
[ODP](varnishing-search-performance-org.odp) formats.

<iframe
	src="//www.slideshare.net/slideshow/embed_code/key/4h5JWHH25nHGa4"
	width="476" height="400" frameborder="0" marginwidth="0" marginheight="0"
	scrolling="no">
</iframe>
