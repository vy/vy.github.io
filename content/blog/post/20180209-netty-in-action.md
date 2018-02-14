---
kind: article
created_at: 2018-02-09 20:34 CET
title: Notes on "Netty in Action"
modules:
  - twitter
tags:
  - java
  - networking
  - programming
---

Those who had priviledge to read my <%=
link_to "frustration chronicles on intra-microservice communication", \
        @items["/blog/post/20170418-inter-service-comm/"] %> would easily
recall me pointing my finger to Java Platform SE guys for not shipping a
proper HTTP client. There my fury went to an extent calling it as one of the
closest candidates for the billion dollar mistake. Unfortunately screaming out
loud in a blog post does not give much of a relief, because it doesn't take
more than a month for me to find myself in precisely the same technical
mudpot. Indeed after a couple of months later I wrote that post, I was chasing
yet another performance problem in one of our aggregation services. In
essence, each incoming HTTP request is served by aggregating multiple sources
collected again over HTTP. This simple fairy tale architecture gets
slaughtered on production by 200 Tomcat threads intertwined with Rx
computation and I/O threads resting in the shades of a dozen other thread
pools dedicated for so-called-asynchronous HTTP clients for aggregated remote
services. And I saved the best for last: there were leaking `TIME_WAIT`
sockets.

All of a sudden the question occurred to me like the roar of rolling boulders
down a steep hill in a far distance: What is the lowest level that I can plumb
a networking application in Java without dealing with protocol intricacies.
Put another way, is there a foundational abstraction exposing both the lowest
(channel with I/O streams) and highest (HTTP headers and body) levels that are
in reach? I rode both Java OIO and NIO (that is, old- and new-I/O) horses in
the past and fell off enough to learn it the hard way that they are definitely
not feasible options in this case. The first attempt in the search of a cure
in Google introduces you to [Netty](http://netty.io/). If you dig long enough,
you also stumble upon [Apache Mina](http://mina.apache.org/) too. Netty is
popular enough in the Java world that it is highly likely you are an indirect
consumer of it, unless you are already directly using it. I was aware of its
presence like dark matter in every single network application that I wrote,
though I have never considered to use it directly. Checking the Netty website
after dealing with crippled network applications at hand revealed an
enlightenment within me: *Hey! I can purpose this to implement some sort of
RPC mechanism using Protocol Buffers in HTTP 2.0 request payloads!* Though
further investigation swipes the dust from the footsteps of giants who had
followed the same path: Google ([gRPC](https://grpc.io/)), Facebook
([Nifty](https://github.com/facebook/nifty)), Twitter
([Finagle](https://twitter.github.io/finagle/)), etc. This finding while
crushing my first excitement, later on left its place to the confidence of
getting confirmed that I am on the right path.

I have always heard good things about both Netty and its community. I have
already been sneakily following the
[presentations](http://normanmaurer.me/presentations/) and [Twitter
updates](https://twitter.com/normanmaurer) of [Norman
Maurer](http://normanmaurer.me/), the Netty shepherd as of date. Though what
triggered me for diving deep with Netty has become the following tweet:

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Challenge accepted! First step is done. Next: Cover to cover study. <a href="https://t.co/Gnfhbi6Ko0">pic.twitter.com/Gnfhbi6Ko0</a></p>&mdash; Volkan Yazıcı (@yazicivo) <a href="https://twitter.com/yazicivo/status/954366672751689728?ref_src=twsrc%5Etfw">January 19, 2018</a></blockquote>

Norman Maurer has always been kind and encouraging to new contributors. So my
plan is to turn this into a relation with mutual benefit: I can contribute and
get tutored while doing that so.

Netty in Action
===============

[The book](https://www.manning.com/books/netty-in-action) (2016 press date) is
definitely a must read for anyone planning to use Netty. It lays out Netty
fundamentals like channels, handlers, encoders, etc. in detail. That being
said, I have got the impression that the content is mostly curated for
beginners. For instance, dozens of pages (and an appendix) are spent (wasted?)
for a Maven crash course, not to mention the space wasted by Maven command
ouputs shared. This felt a little bit disappointing considering the existing
audience of Netty in general. Who would really read a book about Netty? You
have probably had your time with OIO/NIO primitives or client/server
frameworks in the market. You certainly don't want to use yet another library
that promises to make all your problems disappear. So I don't think you can be
qualified as a novice in this battle anymore, and you are indeed in the search
of a scalpel rather than a swiss army knife. Nevertheless, I still think the
book eventually managed to succeed in finding a balance between going too deep
and just scratching the surface.

Things that are well done
-------------------------

* I really enjoyed the presented **historical perspective** on the development
  of Java platforms' networking facilities and Netty itself. Found it quite
  valuable and wanted to read more and more!

* Emphasis on **`ByteBuf`** was really handy. Later on I learnt that there are
  people using Netty just for its sound `ByteBuf` implementation.

* Almost every single conscious decision within the shared **code snippets are
  explained in detail**. While this felt like quite some noise in the
  beginning, later on it turned out be really helpful -- especially while
  manually updating `ByteBuf` reference counts.

* Presented **case studies** were quite interesting to read and inspiring too.

Things that could have been improved
------------------------------------

* I had big hopes to read about how to implement an HTTP client with
  **connection pool** support. I particularly find this feature inevitable in a
  networking application and often not consumed wisely. Though there wasn't a
  single section mentioning about connection pooling of any sort.

* As someone who had studied [Norman Maurer's
  presentations](http://normanmaurer.me/presentations/), I was expecting to
  see waaaay more practical tips about **GC considerations**, updating **socket
  options** (`TCP_NO_DELAY`, `SO_SNDBUF`, `SO_RCVBUF`, `SO_BACKLOG`, etc.),
  mitigating **`TIME_WAIT`** socket problems, and Netty best practices. Maybe
  adding this content would have doubled the size of the book, though I still
  think a book on Netty is incomplete without such practical tips.

* Many inbound requests trigger multiple I/O operations in a typical network
  application. It is crucial to not let these operatins block a running thread,
  which Netty is well aware of and hence ships a fully-fledged `EventExecutor`
  abstraction. This crucial detail is mentioned in many places within the book,
  though none gave a concrete example. Such a common thing could have been
  demonstrated by an example.

Notes
=====

I always take notes while reading a book. Let it be a grammar mistake, code
typo, incorrect or ambiguous information, thought provoking know-how,
practical tip, etc. You name it. Here I will share them in page order. I will
further classify my notes in 3 groups: <span class="note-mistake">mistakes</span>,
<span class="note-improvement">improvements</span>,
<span class="note-question">questions</span>, and
<span class="note-other">other</span>.

* <span class="note-question">\[p19, Listing 2.1\]</span> Why did we use
  `ctx.writeAndFlush(Unpooled.EMPTY_BUFFER)`   rather than just calling
  `ctx.flush()`?

* <span class="note-mistake">\[p21, Listing 2.2\]</span> Typo in
  `throws Exceptio3n`.

* <span class="note-improvement">\[p49, Section 4.3.1\]</span>
  The listed items

  > * A new `Channel` was accepted and is ready.
  > * A `Channel` connection ...

  are an identical repetition of Table 4.3.

* <span class="note-improvement">\[p60\]</span> `CompositeByteBuf` has the
  following remark:

  > Note that Netty optimizes socket I/O operations that employ
  > `CompositeByteBuf`, eliminating whenever possible the performance and
  > memory usage penalties that are incurred with JDK's buffer implementation.
  > This optimization takes place in Netty's core code and is therefore not
  > exposed, but you should be aware of its impact.

  Interesting. Good to know. I should be aware of *its impact*. But how can
  I measure and relate this impact? Maybe I am just nitpicking, tough I would
  love to hear a little bit more.

* <span class="note-question">\[p77, Table 6.3\]</span>
  `channelWritabilityChanged()` method of `ChannelInboundHandler`... How come
  an inbound channel can have a writability notion? I would have expected an
  inbound channel to be just readable.

* <span class="note-improvement">\[p78, Section 6.1.4\]</span> Starts with
  some really intriguing paragraph:

  > A powerful capability of `ChannelOutboundHandler` is to defer an operation
  > or event on demand, which allows for sophisticated approaches to request
  > handling. If writing to the remote peer is suspended, for example, you can
  > defer flush operations and resume them later.

  Though it ends here. No more explanations, not even a single example, etc.
  A total mystery.

* <span class="note-question">\[p79, Table 6.4\]</span> `read()` method of a
  `ChannelOutboundHandler`... Similar to `ChannelInboundHandler#channelWritabilityChanged()`,
  how come an outbound channel can have a read method? What are we reading
  that is supposed to be already originating from us and destined to a remote
  peer?

* <span class="note-improvement">\[p79, Section 6.1.4\]</span>
  It goes as follows:

  > **`ChannelPromise` vs. `ChannelFuture`** Most of the methods in
  > `ChannelOutboutHandler` take a `ChannelPromise` argument to be notified
  > when the operation completes. `ChannelPromise` is a subinterface of
  > `ChannelFuture` that defines the writable methods, such as `setSuccess()`
  > or `setFailure()`, thus making `ChannelFuture` immutable.

  Ok, but why? I know the difference between a `Future` and a `Promise`, though
  I still cannot see the necessity for outbound handlers to employ `Promise`
  instead of a `Future`.

* <span class="note-question">\[p84, Listing 6.5\]</span> While adding handlers
  to a pipeline, what happens in the case of a name conflict?

* <span class="note-improvement">\[p84\]</span> A remark is dropped on the
  **`ChannelHandler` execution and blocking** subject. Just in time! Though
  it misses a demonstration.

* <span class="note-question">\[p86, Listing 6.9\]</span> Again a `read()`
  method for the outbound operations of a `ChannelPipeline`. I am really
  puzzled on the notion of reading from an outbound channel.

* <span class="note-question">\[p94, Listing 6.13\]</span> What happens when
  a `ChannelFuture` completes before adding a listener to it?

* <span class="note-mistake">\[p95, Section 6.5\]</span> Last paragraph goes
  like this:

  > The next chapter will focus on Netty's codec abstraction, which makes
  > writing protocol encoders and decoders much easier than using the
  > underlying `ChannelHandler` implementations directly.

  Though next chapter focuses on `EventLoop` and threading model.

* <span class="note-question">\[p102, Listing 7.3\]</span> Speaking of
  scheduling `Runnable`s to a channel's event loop, what if channel gets
  closed before triggering the scheduled tasks?

* <span class="note-improvement">\[p103\]</span> Page starts with the
  following last paragraph:

  > These examples illustrate the performance gain that can be achieved
  > by taking advantage of Netty's scheduling capabilities.

  Really? Netty's scheduling capabilities are shown by using each function in
  isolation. Though I still don't have a clue on how these capabilities can be
  purposed for a performance gain. This is a **common problem throughout the
  book**: The innocent flashy statement hangs in the air, waiting for a
  demonstration that shares some insight distilled by experience.

* <span class="note-mistake">\[p104, Figure 7.4\]</span> The caption of figure
  is as follows:

  > `EventLoop` allocation for non-blocking transports (such as NIO and AIO)

  AIO? Looks like a typo.

* <span class="note-mistake">\[p107\]</span> Chapter starts with the following
  opening paragraph:

  > Having studied `ChannelPipeline`s, `ChannelHandler`s, and codec classes in
  > depth, ...

  Nope. Nothing has been mentioned so far about codec classes.

* <span class="note-improvement">\[p112\]</span> It is explained that, in the
  context of `Bootstrap`, `bind()`   and `connect()` can throw
  `IllegalStateException` if some combination of   `group()`, `channel()`,
  `channelHandler()`, and/or `handler()` method calls   is missing. Similarly,
  calling `attr()` after `bind()` has no effect. I personally find such
  abstractions poorly designed. I would rather have used the [staged builder
  pattern](https://immutables.github.io/immutable.html#staged-builder) and
  avoid such intricacies at compile-time.

* <span class="note-mistake">\[p117, Listing 8.6\]</span> The 2nd argument to
  `Bootstrap#group()` looks like a typo.

* <span class="note-improvement">\[p120\]</span> Check this end of chapter
  summary out:

  > In this chapter you learned how to bootstrap Netty server and client
  > applications, including those that use connectionless protocols. We
  > covered a number of special cases, including bootstrapping client channels
  > in server applications and using a `ChannelInitializer` to handle the
  > installation of multiple `ChannelHandler`s during bootstrapping. You saw
  > how to specify configuration options on channels and how to attach
  > information to a channel using attributes. Finally, you learned how to
  > shut down an application gracefully to release all resources in an
  > orderly fashion.
  >
  > In the next chapter we'll examine the tools Netty provides to help you
  > test your `ChannelHandler` implementations.

  I have always found such summaries useless, since it is a repetition of
  the chapter introduction, and hence a waste of space. Rather just
  give crucial take aways, preferably in a digestible at a glimpse form.
  For instance, *use `EventLoopGroup.shutdownGracefully()`*, etc.

* <span class="note-improvement">\[p121\]</span> I suppose *Unit Testing*
  chapter used to come after *Codecs* in previous prints and the authors
  have moved it to an earlier stage to establish a certain coherence in
  the introductory chapters. Though, reading *Codecs* reveals that there
  is close to 70% overlap in content, which feels like a poorly structured
  flow. I see the value in authors' attempt, though there is quite some
  room for improvement via tuning the break down of chapters.

* <span class="note-mistake">\[p124, Section 9.2.1\]</span>
  `ByteToMessageDecoder` is used before explained. (See my remark above.)

* <span class="note-improvement">\[p127\]</span> The following bullets
  
  > Here are the steps executed in the code:
  >
  > 1. Writes negative 4-byte integers to a new `ByteBuf`.
  > 2. Creates an `EmbeddedChannel` ...

  is a repetition of the descriptions available in Listing 9.4.

* <span class="note-mistake">\[p138, Listing 10.3\]</span> Comma missing
  after `Integer msg`.

* <span class="note-question">\[p141\]</span> Why do
  `MessageToMessage{Encoder,Decoder}` classes do not have an output type,
  but just `Object`? How do you ensure type safety while chaining them
  along a pipeline?

* <span class="note-mistake">\[p142, Listing 10.6\]</span> Comma missing
  after `Integer msg`.

* <span class="note-mistake">\[p145, Listing 10.7\]</span> Constructor of
  `MyWebSocketFrame` is named incorrectly.

* <span class="note-improvement">\[p151, Section 11.2\]</span> I think
  *Building Netty HTTP/HTTPS applications* deserves its own chapter. And
  a very important subject is missing: connection pooling.

* <span class="note-question">\[p157, Listing 11.6\]</span> While building
  the WebSocket pipeline, which handler addresses ping/pong frames?

* <span class="note-mistake">\[p159, Table 11.4\]</span> The first sentence
  in the description of `WriteTimeoutHandler` is identical to the one in
  `ReadTimeoutHandler`. Supposedly a copy-paste side-effect.

* <span class="note-mistake">\[p171\]</span> Check out the first paragraph:

  > WebSocket is an advanced network protocol that has been developed to
  > improve the performance and responsiveness of web applications. We'll
  > explore Netty's support for *each of them* by writing a sample
  > application.

  Each of them? Who are they?

* <span class="note-mistake">\[p177\]</span> *The call to `retain()` is
  needed because after `channelRead()` ...* &rarr; *The call to `retain()`
  is needed because after `channelRead0()` ...*

* <span class="note-improvement">\[p178, Table 12.1\]</span> Identical to
  Table 11.3.

* <span class="note-mistake">\[p181, Figure 12.3\]</span>
  `ChunkedWriteHandler` is missing.

* <span class="note-question">\[p183, Listing 12.4\]</span> There the shutdown
  of the chat server is realized via `Runtime.getRuntime().addShutdownHook()`.
  Is this a recommended practice?

* <span class="note-mistake">\[p189\]</span> *Figure 14.1 presents a high-level
  view of the ...* &rarr; *Figure 13.1*

* <span class="note-mistake">\[p189\]</span> *Listing 14.1 shows the details
  of this simple POJO.* &rarr; *Listing 13.1*

* <span class="note-improvement">\[p190, Listing 13.1\]</span> `received`
  field is not used at all. Could be removed to increase clarity.
  Interestingly, the field is not even encoded.

* <span class="note-mistake">\[p191, Table 13.1\]</span>
  `extendsDefaultAddressedEnvelope` &rarr; `extends DefaultAddressedEnvelope`

* <span class="note-mistake">\[p191\]</span> *Figure 14.2 shows the
  broadcasting of three log ...* &rarr; *Figure 13.2*

* <span class="note-mistake">\[p192\]</span> *Figure 14.3 represents
  a high-level view of the ...* &rarr; *Figure 13.3*

* <span class="note-improvement">\[p192, Listing 13.2\]</span> A `byte[] file`
  and `byte[] msg` pair is encoded as follows:

      #!java
      buf.writeBytes(file);
      buf.writeBytes(LogEvent.SEPARATOR);
      buf.writeBytes(msg);

  Later on each entry is read back by splitting at `LogEvent.SEPARATOR`. What
  if `file` contains `LogEvent.SEPARATOR`? I think this is a bad encoding
  practice. I would rather do:

      #!java
      buf.writeInt(file.length);
      buf.writeBytes(file);
      buf.writeInt(msg.length);
      buf.writeBytes(msg);

* <span class="note-question">\[p194, Listing 13.3\]</span> Is there a
  constant for `255.255.255.255` broadcast address?

* <span class="note-mistake">\[p195\]</span> *Figure 14.4 depicts the
  `ChannelPipeline` of the `LogEventonitor` ...* &rarr; *Figure 13.4*

* <span class="note-improvement">\[p196\]</span> Check this out:

  > The `LogEventHandler` prints the `LogEvent`s in an easy-to-read
  > format that consists of the following:
  >
  > * The received timestamp in milliseconds.

  Really? I did not know epoch timestamps were *easy-to-read*. Maybe for some
  definition of easy-to-read.

* <span class="note-mistake">\[p195\]</span> *Now we need to install our
  handlers in the `ChannelPipeline`, as seen in figure 14.4.* &rarr;
  *Figure 13.4*

* <span class="note-mistake">\[p205\]</span> *Approach A, optimistic and
  apparently simpler (figure 15.1)* &rarr; *figure 14.1*

* <span class="note-improvement">\[p206\]</span> Half of the page is spent
  for justifying Droplr's preference of approach B (safe and complex) over
  approach A (optimistic and simpler). Call me an idiot, but I am not sold
  to these arguments that the former approach is less safe.

* <span class="note-mistake">\[p207\]</span> Type of `pipelineFactory`
  is missing.

* <span class="note-improvement">\[p210\]</span> There is a bullet for
  tuning JVM. This on its own could have been a really interesting chapter
  of this book.

* <span class="note-other">\[p213\]</span> Firebase is indeed implementing
  TCP-over-long-polling. I wonder if there exists any Java libraries that
  implements user-level TCP over a certain channel abstraction.

* <span class="note-mistake">\[p214\]</span> *Figure 15.4 demonstrates
  how the Firebase long-polling ...* &rarr; *Figure 14.4*

* <span class="note-mistake">\[p215\]</span> *Figure 15.5 illustrates
  how Netty lets Firebase respond to ...* &rarr; *Figure 14.5*

* <span class="note-mistake">\[p216\]</span> *... can start as soon as
  byes come in off the wire.* &rarr; *bytes*

* <span class="note-mistake">\[p217, Listing 14.3\]</span> Last parenthesis
  is missing:

      #!scala
      rxBytes += buf.readableBytes(
                                tryFlush(ctx)

* <span class="note-improvement">\[p217, Listing 14.3\]</span> 70% of the
  intro was about implementing a control flow over long polling, though the
  shared code snippet is about totally something else and almost irrelevant.

* <span class="note-mistake">\[p223\]</span> *In referring to figure 15.1,
  note that two paths ...* &rarr; *figure 14.6*

* <span class="note-mistake">\[p229\]</span> *This request/execution flow is
  shown in figure 16.1.* &rarr; *figure 15.1*

* <span class="note-mistake">\[p230\]</span> *Figure 16.2 shows how pipelined
  requests are handled ...* &rarr; *Figure 15.2*

* <span class="note-mistake">\[p230\]</span> *..., in the required order. See
  figure 16.3.* &rarr; *figure 15.3*

* <span class="note-mistake">\[p232\]</span> *That simple flow (show in figure
  16.4) works...* &rarr; *figure 15.4*

* <span class="note-improvement">\[p232\]</span> *The client call is dispatched
  to the Swift library, ...* What is Swift library? Was not explained anywhere.

* <span class="note-mistake">\[p232\]</span> *This is the flow shown in figure
  16.5.* &rarr; *figure 15.5*

* <span class="note-other">\[p234\]</span> This is a really interesting piece:

  > Before [Nifty](https://github.com/facebook/nifty), many of our major Java
  > services at Facebook used an older, custom NIO-based Thrift server
  > implementation that works similarly to Nifty. That implementation is an
  > older codebase that had more time to mature, but because its asynchronous
  > I/O handling code was built from scratch, and because Nifty is built on
  > the solid foundation of Netty's asynchronous I/O framework, it has had
  > many fewer problems.
  >
  > One of our custom message queuing services had been built using the older
  > framework, and it started to suffer from a kind of socket leak. A lot of
  > connections were sitting around in `CLOSE_WAIT` state, meaning the server
  > had received a notification that the client had closed the socket, but the
  > server never reciprocated by making its own call to close the socket. This
  > left the sockets in a kind of `CLOSE_WAIT` limbo.
  >
  > The problem happened very slowly; across the entire pool of machines
  > handling this service, there might be millions of requests per second,
  > but usually only one socket on one server would enter this state in an
  > hour. It wasn't an urgent issue because it took a long time before a
  > server needed a restart at that rate, but it also complicated tracking
  > down the cause. Extensive digging through the code didn't help much
  > either: initially several places looked suspicious, but everything
  > ultimately checked out and we didn't locate the problem.

* <span class="note-mistake">\[p238\]</span> *Figure 16.6 shows the
  relationship between ...* &rarr; *figure 15.6*

* <span class="note-improvement">\[p239, Listing 15.2\]</span> All presented
  Scala code in this chapter is over-complicated and the complexity does not
  serve any purpose except wasting space and increasing cognitive load. For
  instance, why does `ChannelConnector` extend
  `(SocketAddress => Future[Transport[In, Out]])` rather than just being a
  simple method?

* <span class="note-improvement">\[p239\]</span> *This factory is provided a
  `ChannelPipelineFactory`, which is ...* What is *this factory*?

<style type="text/css">
    span.note-mistake {
        color: red;
    }
    span.note-improvement {
        color: orange;
    }
    span.note-question {
        color: green;
    }
    span.note-other {
        color: silver;
    }
</style>

Conclusion
==========

In summary, [Netty in Action](https://www.manning.com/books/netty-in-action)
is a book that I would recommend to everyone who wants to learn more about
Netty to use it in their applications. Almost the entire set of fundamental
Netty abstractions are covered in detail. The content is a bliss for novice
users in networking domain. Though this in return might make the book
uninteresting for people who already got their hands pretty dirty with
networking facilities available in Java Platform. That being said, the
presented historical perspective and shared case studies are still pretty
attractive even for the most advanced users.

I don't know much about the 2<sup>nd</sup> author of the book, Marvin Allen
Wolfthal. Though, the 1<sup>st</sup> author, Norman Maurer, is a pretty known
figure in the F/OSS ecosystem. If he manages to transfer more juice from his
experience and presentations to the book, I will definitely buy the
2<sup>nd</sup> print of the book too!
