---
kind: article
created_at: 2019-01-26 20:25 CET
title: Notes on "Reactive Programming in Spring 5"
tags:
  - java
  - concurrency
  - programming
  - reactive
---

> **TL;DR** -- Already have your hands dirty with Spring? Wondering
> how reactive will play along with Spring and how they will shape
> each other? Read this book. You will get crushed under the load of
> information trying to get covered, but will have no regrets.

![Reactive Programming in Spring 5](cover.jpg)

I tend to avoid reading books whose subject is about a certain library
or tool, unless I think it will provide some insight into a certain
domain in addition to the software's internals. And as you may guess,
many [Spring](https://spring.io/)-related books do not pass this
test. Though [Reactive Programming in Spring
5](https://www.packtpub.com/application-development/hands-reactive-programming-spring-5)
was an exception due to following reasons:

* [Oleh Dokuka](https://twitter.com/OlehDokuka), one of the two
  authors of the book, is a contributor to many Spring projects, in
  particular to [Reactor](http://projectreactor.io/). He is further a
  pretty active figure in [Reactor Gitter
  channel](https://gitter.im/reactor/reactor) where he is serving a
  fantastic public service. I personally am really interested in
  hearing anything he would say about [Reactive
  Streams](http://www.reactive-streams.org/) in general.

* Love it, hate it, but almost the entire Java train is fueled by
  Spring framework. In my day to day work, I am swamped into Spring
  too. If you would pay close attention, particularly after the recent
  [SpringOne 2018](https://springoneplatform.io/2018/sessions), Spring
  is full steam moving towards a reactive interface supported by all
  its whistles and bells -- [RSocket](http://rsocket.io/),
  [R2DBC](https://r2dbc.io/), [WebFlux and
  WebClient](https://docs.spring.io/spring-framework/docs/5.0.0.BUILD-SNAPSHOT/spring-framework-reference/html/web-reactive.html),
  Reactor, etc. Though sometimes it is really difficult to see how the
  entire machine is progressing given the excessive amount of
  sub-projects. I expected the book to provide a 2,000 ft overview to
  the roadmap of this beast.

Overview
========

If you are dealing with Spring while taking your daily dose of Java,
**read this book!** The book manages to deliver an outstanding
coverage of both reactive streams and its integration to almost all of
the existing Spring components. In a nutshell, it lays out the
following subjects in order:

- fundamentals of reactive programming (observer pattern)
- its historical development in the presence of RxJava, Reactive Streams, and Reactor
- pull, push, and pull-push streaming
- backpressure
- theoratical foundations of reactive programming (Little's and Amdahl's laws)
- WebFlux versus Web MVC
- introduction to Reactor
- reactive
  - Spring Data
  - Spring Cloud Stream
  - Spring Cloud Flow
  - Spring Boot
- RSocket
- testing
- deployment to cloud

In conclusion, authors did a splendid job in compiling an exhaustive
content covering almost every aspect of reactive programming in Spring
5. They possess an in-depth understanding of the material they are
talking about and present it in a digestable form to the user. While
this thick compilation has the potential of crushing the reader, it is
definitely a rewarding read.

Pros
----

After finishing the book, a cover-to-cover marathon of 538 pages, I
felt like I know everything there is to know about reactive
programming in Spring.

![I know reactive Spring!](i-know.jpg)

The extent of the covered content was astonishingly huge. I knew about
RxJava, Reactive Streams, and Reactor individually, but not how they
relate to each other. The presented historical perspective cleared out
the missing pieces of the puzzle for me. I really enjoyed how the
prose builds up by examining the problem, introducing the solution,
laying out caveats of certain approaches, and drawing real-world
comparisons. They repeated this pragmatic pattern for almost any
project (Reactor, WebFlux, Spring Data, Spring Cloud Stream, etc.)
they introduced.

I was not expecting an in-depth Reactor content, though the authors
delivered a perfect job here given the book's main subject is not just
Reactor.

Investigation of pull, push, pull-push streaming, stress of
backpressure, and reinforcement of the content with some theory
(Little's and Amdahl's laws) was pretty enlightening to read. While
many would consider these subjects boring, I found it pretty
interesting and practical.

Cons
----

The book is too long to a point of becoming exhausting. Many material
(Vert.x, Ratpack integration, Reactive Streams TCK, transactions in
distributed messaging systems, etc.) could have been left out and then
the main juice would fit into ~300 pages. Even then, it is still
long. I would have split the book into two: *Project Reactor in
Action* and *Reactive Programming in Spring 5*. While reading, I also
felt such a split as well.

While 90% of the book is pretty objective, certain subjects were
presented with bias. Particularly, RSocket-vs-gRPC comparison and
using message brokers over system-to-system communication chapters
were really opinionated. (I further explained this problem in my notes
shared below.)

The presented content is always excercised using Apache Kafka and
MongoDB. I suppose this is due to the fact that these two are the only
tools that have almost perfect reactive coverage by Spring family of
projects.

Notes
=====

Below I share my notes ranging from a grammar mistake to a code typo,
incorrect or ambiguous information to a thought provoking know-how,
practical tip, etc. I further classify them in 4 groups:
<span class="note-correction">corrections</span>,
<span class="note-improvement">improvements</span>,
<span class="note-question">questions</span>, and
<span class="note-other">other</span>.

* <span class="note-correction">\[p11]</span> Shared `processRequest()`
  method is missing a `return` statement.

* <span class="note-correction">\[p12]</span> As a coroutine/fiber
  fanboy, I could not have passed through the following statement:
  
  > In some languages, such as C#, Go, and Kotlin, the same code \[a
  > simple inter-microservice communication over HTTP] might be
  > non-blocking when green threads are used. However, in pure Java,
  > we do not have such features yet. Consequently, the actual thread
  > will be blocked in such cases.
  
  I forgot how many times I needed to correct this false misbelief,
  but I will repeat it here one more time: For any language X
  compiling to JVM bytecode, if a Java standard library call is
  \[thread] blocking, access to it in X is going to be blocking as
  well. Kotlin coroutines is no exception to this. Further every
  convenience X provides, say coroutines, except syntatic sugars, has
  already been at the exposure of Java via solid libraries like
  [Kilim](https://github.com/nqzero/kilim) (since 2006) and
  [Quasar](https://github.com/puniverse/quasar) (since 2013).
  
  Additionally, the rules of the game will totally change in a couple
  of years after the release of [Project
  Loom](http://openjdk.java.net/projects/loom/).

* <span class="note-improvements">\[p16]</span> In Diagram 1.4, what
  is the difference between solid and dashed lines? I am surprised to
  see that the image is advertising Apache Kafka while the rest of the
  components are free from such specification.

* <span class="note-improvements">\[p18]</span> In Diagram 1.5, texts
  are not readable. (Unfortunately, many of the image texts are not
  readable in the hardcopy. I don't know about the e-book though.)

* <span class="note-correction">\[p28]</span> *all cross-service
  communication is non-blocking anymore.* &rarr; *... is not blocking
  anymore.*

* <span class="note-correction">\[p46]</span> *the actual request
  processing continues until `SseEnitter.complete()`* &rarr;
  *... until `SseEmitter.complete()`*

* <span class="note-improvement">\[p46]</span> Justification of why
  `@Async` is necessary here is missing.

* <span class="note-correction">\[p59]</span> *The `count` operator is
  pretty descriptive, it emits the only value ...* &rarr; *... emits
  only one value ...*

* <span class="note-question">\[p62]</span> Chapter starts with

      #!java
      public interface SearchEngine {
	      List<URL> search(String query, int limit);
      }
  
  interface, improves it with

      #!java
      public interface InterableSearchEngine {
	      Iterable<URL> search(String query, int limit);
      }
  
  and
  
      #!java
	  public interface FutureSearchEngine {
	      CompletableFuture<List<URL>> search(String query, int limit);
	  }
  
  After piling up enough motivation, justifies the victory of
  `Observable`s:
  
      #!java
	  public interface RxSearchEngine {
	      Observable<URL> search(String query, int limit);
	  }
  
  As a reader, let me ask the obvious question: Why not using a
  `Stream<URL>` return type instead?

* <span class="note-question">\[p103]</span> In the following
  explanation,
  
  > Note that `ScheduledPublisher` is effectively an infinite stream
  > and the completion of the merged `Publisher` is ignored.
  
  What does *merged `Publisher`* refer to? `NewsPreparationOperator`?
  
* <span class="note-correction">\[p106]</span> *Unfortunately, building a
  proper test suit* &rarr; *... test suite*

* <span class="note-improvement">\[p114]</span> Rather than focusing
  this much on the TCK, which is most of the time more relevant for
  library authors compared to users, I wish the authors would have had
  spared some pages on pitfalls and patterns of processors, which is
  bread and butter of reactive stream users and sadly skipped in the
  previous chapter.

* <span class="note-improvement">\[p123-129]</span> I don't think the
  readers really care about reactive streams adjustments for Vert.x,
  Ratpack or MongoDB reactive streams driver. I find these pages
  irrelevant and distracting.

* <span class="note-improvement">\[p133]</span> It is page 133 and the
  reader is newly getting exposed to Project Reactor. Sort of too
  late, I think.

* <span class="note-improvement">\[p133]</span> *Project Reactor, the
  most famous library in the reactive landscape, ...* Really? Putting
  aside I favor Reactor over RxJava, the IT community that I know of
  does not give me such an impression to back this claim up.

* <span class="note-correction">\[p141]</span> *investigating its reach
  API.* &rarr; *... its rich API*

* <span class="note-improvement">\[p149]</span> Speaking of `defer()`,
  it allows retries, which is, I think, of uttermost importance mostly
  overlooked by many and aligns better with reactive streams semantic
  compliance. Consider the following code:
  
      #!java
	  <T> Mono<T> f(Mono<T> mono) {
	      Stopwatch stopwatch = Stopwatch.createUnstarted();
		  return mono
		          .doOnSubscribe(ignored -> stopwatch.start())
				  .doOnTerminate(() -> LOGGER.log("{}", stopwatch));
	  }
  
  versus the alternative below
  
      #!java
      <T> Mono<T> f(Mono<T> mono) {
          return Mono.defer(() -> {
              Stopwatch stopwatch = Stopwatch.createUnstarted();
              return mono
                      .doOnSubscribe(ignored -> stopwatch.start())
                      .doTerminate(() -> LOGGER.log("{}", stopwatch));
          });
      }

  Also this is a good spot to talk about assembly-vs-runtime overhead
  of operator chaining.

* <span class="note-correction">\[p149]</span> The word wrapping of
  paragraph starting with *Summing this up, Project reactor allows
  ...* is broken.

* <span class="note-correction">\[p150]</span> *..., we may still request
  `Long.MAX_VALUE).`* &rarr; *request `Long.MAX_VALUE.`*

* <span class="note-improvement">\[p154]</span> The first paragraph of
  the page (*However, the described approach for defining subscription
  ...*) is an eye opener gem. Given many seasoned RS users fell into
  this trap at least once, a couple of paragraphs detailing these
  caveats would come really handy.

* <span class="note-improvement">\[p169]</span> Speaking of
  `Flux#flatMap()` operator, `concurrency` parameter might have been
  slightly mentioned here.

* <span class="note-question">\[p171]</span> Given we are executing
  `doOn...()` methods (`doOnNext()`, `doOnComplete()`,
  `doOnSubscribe()`, etc.) for their side effects, what does happen
  when they throw an exception?

* <span class="note-improvement">\[p173]</span> Provide a couple of
  examples for `log()` operator, please! Many people, particularly
  coming from RxJava, do not know of its existence.

* <span class="note-correction">\[p174]</span> *However, this allows
  forthe sending ...* &rarr; *... allows for the sending ...*

* <span class="note-question">\[p174]</span> In the `Flux.create()`
  example, I am puzzled about how does it handle the backpressure.

* <span class="note-improvement">\[p183]</span> I think *exponential
  backoff* deserves an explanation here. What does it mean? Further, I
  would have used seconds rather than milliseconds in the example,
  since the latter does not expose the backoff periods clearly at
  first sight.

* <span class="note-correction">\[p188]</span> *`Flux<Integer>
  cachedSource = source.share();`* Here and in the rest, all of the
  occurences of `cachedSource` should be replaced with `sharedSource`.

* <span class="note-improvement">\[p191]</span> The used *assembly
  phase* term will be described in next chapters, hence using it here
  is sort of confusing. Further, the given explanation for
  `transform()` has still some room for improvement. Additionally, I
  would prefer to see a "when to use `compose()`, when to use
  `transform()`" guide.

* <span class="note-improvement">\[p196-197]</span> There are 3 places
  where *assemble-time* is used, though it used to be referred as
  *assembly-time*".

* <span class="note-correction">\[p198]</span> *... passing
  `Subscription` through ever `Subscriber`s ...* &rarr; *... passing
  `Subscription` through `Subscriber`s ...*

* <span class="note-other">\[p200]</span> The last paragraph of p199
  goes as follows:
  
  > THe importance of understanding this phase is that during runtime
  > we may apply optimization that may reduce amount of signals
  > exchange. \["the amount of signals exchanged"?] For example, as we
  > are going to see in the next sections, we may reduce the number of
  > `Subscription#request` calls and improve, therefore, performance
  > of the stream.
  
  Then the following tip opens the p200:

  > ... the invocation of `Subscription#request` method causes a write
  > to the `volatile` field that holds demand. Such a write is an
  > expensive operation from computation perspective, so it is better
  > to avoid it if possible.

  Hrm... I thought the main overhead of `Subscription#request` calls
  was unnecessary individual requests which could have been
  batched. Compared to this, write to a `volatile` does not really
  sound like an overhead.

* <span class="note-improvement">\[p200]</span> Diagram 4.8 is missing
  some explanation.

* <span class="note-question">\[p204]</span> In Diagram 4.11, how is
  backpressure preserved given there is an external buffer employed
  by `publishOn`. Who maintains this buffer? Is it the task queue of
  the `ScheduledExecutionService` used under the hood?

* <span class="note-question">\[p206]</span> Totally lost with the
  following sentence: *Under the hood, `subscribeOn` executes the
  subscription to the parent `Publisher` into `Runnable`, which is the
  scheduler for a specified `Scheduler`.*

* <span class="note-correction">\[p207]</span> In the shared code
  snippet, `.map()` and `.filter()` are missing `...` as input
  arguments.

* <span class="note-question">\[p208]</span> How does
  `SingleScheduler` handle blocking functions spoiling time-sensitive
  executions?

* <span class="note-improvement">\[p209]</span> *... so the execution
  is attache to ...* &rarr; *... so the execution is attached to ...*

* <span class="note-improvement">\[p209]</span> In the next page, it
  has been admitted that the shared code snippet does not demonstrate
  a good usage of `ThreadLocal`s. So why not sharing a proper use of
  `ThreadLocal`s?

* <span class="note-correction">\[p211]</span> I think *Such design
  decision ... have its own `Context`.* part of the last paragraph
  needs a rewrite.

* <span class="note-correction">\[p213]</span> *... bottom (with id
  initial) has empty Context at all.* &rarr; *... bottom (with id
  `initial`) has empty `Context` at all.*

* <span class="note-correction">\[p214]</span> *The preciding code show a
  ...* &rarr; *The preciding code shows a ...*

* <span class="note-correction">\[p215]</span> *... we mentioned another
  sample of such ...* &rarr; *... we mentioned another example of such
  ...*

* <span class="note-correction">\[p217]</span> In Diagram 4.15, the box
  at the bottom should be titled `subscribe()` instead of `flatMap()`.

* <span class="note-correction">\[p225]</span> *Preview Online Code
  Files* at the bottom looks to be a typo.

* <span class="note-question">\[p230]</span> *... the WebFlux module
  provides built-in backpressure support ...* Cool! But how does it do
  that?

* <span class="note-correction">\[p254]</span> *... using the
  `PasswordEncoder#matchs` ...* &rarr; *... using the
  `PasswordEncoder#matches` ...*

* <span class="note-question">\[p254]</span> In the shared snippet,
  which scheduler executes the `map(p ->
  passwordEncoder.matches(...))` line? Netty I/O loop thread? If so
  (or some other scheduler of similar importance), is it wise perform
  `passwordEncoder#matches` here?

* <span class="note-correction">\[p255]</span> In the shared code
  snippet, isn't `flatMap(isMatched -> ...)` should be replaced with
  `map(isMatched -> ...)`?

* <span class="note-correction">\[p278]</span> *`else
  if(resposne.statusCode() == EXPECTATION_FAILD) {`* &rarr; *`else
  if(response.statusCode() == EXPECTATION_FAILED) {`*

* <span class="note-correction">\[p267]</span> *... template has a
  placeholder, `dataSource`, ...* &rarr; *... template has a
  placeholder, `playList`, ...*

* <span class="note-correction">\[p273-274]</span> All apperances of
  *Albom* and *albom* should be replaced with *Album* and *album*,
  respectively.

* <span class="note-correction">\[p278]</span> *As we can observe from
  the preciding diagram, with an increase in parallelization, the
  throughput of the system starts becoming slower and slower.*
  Hrm... Actually the throughput keeps on increasing, though the gain
  is slowing down. Does it mean *the increase in throughput*?

* <span class="note-improvement">\[p281]</span> The definitions of
  contention and coherence are left pretty ambiguous. A couple of
  practical examples would come really handy.

* <span class="note-correction">\[p292]</span> Diagram 6.16 misses the
  legend. The caption can be reworked to fix this as follows: *WebFlux
  (dash) versis WebMVC (plus) throughput...* This applies to the rest
  of diagrams with multiple lines in the following pages.

* <span class="note-improvement">\[p301-303]</span> I would rather use
  a bar chart for performance figures rather than a table.

* <span class="note-improvement">\[p308]</span> Diagram 6.25 looks
  like a [mspaint.exe](https://en.wikipedia.org/wiki/Microsoft_Paint)
  101 assignment submission.

* <span class="note-correction">\[p311]</span> *... the system has four
  central components ...* &rarr; *... the system has three central
  components ...*

* <span class="note-correction">\[p349]</span> *... EclipseLink, Spring
  Data JDBC, and Spring Data JDBC, ...* &rarr; *... EclipseLink,
  Spring Data JDBC, and Spring JDBC, ...*

* <span class="note-correction">\[p356-357]</span> All occurences of
  `updatedBook...` should be replaced with `updateBook...`.

* <span class="note-improvement">\[p379]</span> What is the point of
  *Distributed transactions with the SAGA pattern* here?

* <span class="note-improvement">\[p405]</span> In Diagram 8.1, there
  is plenty of space that could have been used and the texts are so
  small to the point of becoming unreadable.

* <span class="note-other">\[p418]</span> This page concludes the
  *Scaling up with Cloud Streams* chapter by announcing its triumph
  over previously mentioned service-to-service architectures. I sadly
  find this conclusion pretty biased and far from reflecting the
  reality. There is no silver bullet for such problems and as has
  always been the case, *it depends*. Further, almost all of the
  listed so-called improvements to message broker-based solutions are
  either as is or with similar approaches applicable to
  service-to-service architectures as well. It is also surprising to
  see no mention of practical hurdles one need to overcome while
  scaling brokers too. You can easily Google and find dozens of Kafka
  horror stories. For a book that spent chapters on backpressure
  problems, the question of how is it affected by the delegation of
  the communication to a broker is totally ignored. Given how
  objective and well-equiped the authors were throughout the entire
  book, I am really amazed to see such a hype-oriented conclusion at
  the end of this chapter.

* <span class="note-improvement">\[p425]</span> In the shared code
  snippet, used `messagesStream` and `statisticStream` are neither
  described, nor defined.

* <span class="note-improvement">\[p430]</span> For a book published
  in October 2018, it is better to not limit the list of cloud
  providers offering serverless deployments with AWS Lambda. To the
  best of my knowledge, GCP, Azure, and many others provide similar
  functionalities.

* <span class="note-correction">\[p435]</span> *`ClassLoad`* &rarr;
  *`ClassLoader`*

* <span class="note-question">\[p437]</span> It is noted that authors
  escaped `<` and `>` characters in the URL they pass to `curl` with
  `%3C` and `%3E`, respectively. Though, AFAIK, `curl` already does
  that if you pass the URL in quotes. Isn't it?

* <span class="note-correction">\[p440]</span> *... represent independent
  ClassLoaders.* &rarr; *... represent independent `ClassLoader`s.*

* <span class="note-correction">\[p441]</span> *`implements
  Function<Payment, Payment>`* &rarr; *`implements Function<Payment,
  PaymentValidation>`*

* <span class="note-correction">\[p441]</span> *`public Payment
  apply(Payment payment) { ... }`* &rarr; *`public PaymentValidation
  apply(Payment payment) { ... }`*

* <span class="note-correction">\[p448]</span> A dashed arrow is missing
  from Service B's `request(1)` line to Service A's `request(10)`
  line.

* <span class="note-improvement">\[p449]</span> Page contains a pretty
  well wrapped comparison of Reactive Streams versus TCP for flow
  control. Given HTTP/3 is almost ready to be served and is employing
  UDP rather than TCP, a *Reactive Streams versus HTTP/3* comparison
  would be really thought-provoking.

* <span class="note-correction">\[p450]</span> `request(3)` under Service
  A's adapter is, I believe, mistakenly placed.

* <span class="note-other">\[p454]</span> In the shared code snippet,
  isn't `Flux.interval(Duration.ofMillis(100))` too harsh for service
  discovery?

* <span class="note-other">\[p456]</span> I am aware of the fact that
  the design of gRPC incurs [serious flow control
  problems](https://github.com/grpc/grpc-java/issues/1549), though in
  a section where you compare contenders like RSocket and gRPC, there
  is no place for such a vague and ungrounded statement:
  
  > Looking at the preciding code, we may get the feeling that gRPC,
  > along with asynchronous message passing, gives backpressure
  > control support as well. However, that part is a bit tricky.

  Is backpressure is not handled at all or what? One should not pass
  over such a claim by hand waving.

* <span class="note-correction">\[p457]</span> *`public static class
  TestApplication`* &rarr; *`public class TestApplication`*

* <span class="note-question">\[p457]</span> The RSocket endpoint is
  annotated with `@RequestManyMapping(value = "/stream1", mimeType =
  "application/json")`. Given RSocket is a wire protocol, what is the
  purpose of the provided path and MIME type here?

* <span class="note-other">\[p461]</span> The summary repeats the
  triumph of message brokers over service-to-service communication one
  more time. Again, this is a really subjective statement. There are
  many advantages and disadvantages to each approach. Announcing a
  winner is a pretty dangerous generalization.

* <span class="note-improvement">\[p471]</span> Shared
  `StepVerifier.withVirtualTime()` trick only works unless you use a
  custom scheduler in `interval()` and `timeout()` calls.

* <span class="note-other">\[p478]</span> Here authors share a hack to
  work around the problem of Spring Boot 2.0 `WebClient` not providing
  the mocking support for outgoing HTTP interactions. I would rather
  share this trick in a Stack Overflow post, because the readers of
  the book will take it for granted, and rather share the
  aforementioned WireMock approach.

* <span class="note-other">\[p480]</span> *Testing
  WebSocket*... Again, this is a hack rather than a solution. I would
  not share it in the book.

* <span class="note-correction">\[p491]</span> Diagram 10.1 is totally
  irrelevant to the content of the page.

* <span class="note-improvement">\[p492]</span> Some texts in Diagram
  10.3 are not readable.

* <span class="note-correction">\[p503]</span> *... memory usage by
  regions, GC pauses, treads count ...* &rarr; *... memory usage by
  regions, GC pauses, thread counts ...*

* <span class="note-improvement">\[p510]</span> It is wise to note
  that Spring Boot Admin is not an official Spring project.

* <span class="note-improvement">\[p514-515]</span> No mention of
  either GCP or App Engine.

<style type="text/css">
    span.note-correction {
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
