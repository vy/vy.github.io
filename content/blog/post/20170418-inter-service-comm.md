---
kind: article
created_at: 2017-04-18 17:22 CET
title: On Sadness and Inter-Microservice Communication
tags:
  - java
  - programming
---

Let me get this straight: **Every single line of code that needs to
communicate with a remote microservice is the most bizarre, annoying, sad, and
hopeless experience in my daily coding routine.** And the worst is: Most of
the time its *my client* code communicating with *my services*, so there is no
one else to blame that would sooth my anger. But I did not end up here out of
blue.

In my freshman years, I was given the responsibility of further development of
a microservice, where both the server and its driver (API models, HTTP client,
etc.) were written in Scala. Because Scala was still a cool buzzword back then
and the team wanted to experiment with it. (No, this won't be a Scala FUD
post.) It was using an in-house built HTTP client, which is more or less yet
another buggy wrapper over an ancient version of [Ning
async-http-client](https://github.com/ning/async-http-client). I implemented a
(yes, another!) thin wrapper over it to expose the HTTP response models as
`scala.concurrent.Future`s, so we can compose them via Scala's
for-comprehensions. (It did not take long for me to figure out that exposing
the API in Scala was one of the worst possible design decisions one could have
made in an ecosystem dominated by Java consumers.)

Later on as a team we adopted another critical microservice comprising a giant
Java client with Spring fizz and buzz, caching, Guava immutables all under the
hood with insanely strict `checkNotNull`/`checkArgument`-powered model
validation, etc. This comet created its own fan clubs. There are two types of
people in the company who are consuming this service:

1. ones that bite the bullet and use the gigantic driver we
   provide (say hello to a truck load of artifacts in your
   not-sufficiently-sucking dependency hell) or

2. ones that prefer to implement his/her own HTTP driver hosting an empire of
   bugs by manually building/parsing query request/response models formatted
   in JSON/XML/Protobuf.

Later on I said enough is enough! Let's stick to a standard: JEE HTTP client,
that is, Jersey JAX-RS Client with Jackson cream on it. I still needed to
create all the API models and verify them myself every time. It was bearable
to some extent. But here comes the perfect storm: JAX-RS Client 2.0 (which
supports proper HTTP connection pooling with sanely configurable
socket+connection timeout support, which weren't sanely available in 1.x)
requires `javax.ws.rs-api` 2.x, which is binary incompatible with 1.x, which
is used by 80% of microservices in the ecosystem. So in practice no other
microservice will be able to use my driver without the developer losing half
of his/her hairs.

Later on I kept repeating "enough is enough"! Let's use [Google's
async-http-client](https://github.com/AsyncHttpClient/async-http-client). It
is pluggable all around the place: the HTTP connector (Apache HC, etc.),
marshaller (Jackson, Gson, etc.). The project is more or less undocumented.
But thanks to an army of Android users, there is plenty of blog posts and
source code to discover your own personal bugs, so you can keep on blog
posting about it. Anyway... It worked. I still need to motivate myself to dive
into the source code to comprehend how it works under the hood, but it worked.

Today... When I need to talk to one of these services I need to pick a lousy,
juice, smelly sh*t of my preference:

- Inject the entire Scala milky way into your 1-file Java microservice, which
  could have been delivered as a 5MB fat-JAR before Scala space-warping it
  into 50MB. And don't forget to pat your IDE in the back every time it needs
  to auto-complete a Scala class. Oh, by the way, have you ever tried
  accessing a `scala.Option` from Java? Boy! It is fun! I hope your service
  consumers think likewise.

- Let the giant Java driver bring all its feature-rich functionality together
  with its cousins, its nephews, its uncle, its grandma, its grandpa, its
  friends from the school, its ex, and of course with spring-core. All you
  wanted is to make a `GET` to `/v1/user/<id>`, but now you have the entire
  Pivotal art gallery decorating your `mvn dependency:tree` output on the
  wall.

- You can of course purpose maven-shade-plugin to shade and relocate the
  entire `javax.ws.rs-api`, Jersey dependencies, together with the entire
  universe. I know you can do that.

- Browse to Google's `async-http-client` webpage and try to find the page that
  explains how to make a simple fscking `GET` request.

- Embrace the old Ning client wrapper, welcome bugs (the first time I needed
  to use it I found out that `setHeaders()` wasn't working as expected), stick
  to JAX-RS 1.x and an ancient Netty version, which causes a JAR Hell with any
  recent library, e.g., Elasticsearch. (Please refer back to
  maven-shade-plugin item.)

I can hear you shouting about compile-time generated HTTP clients based on
Swagger or WADL specs. But weren't we just cursing WSDL and trying to run away
from it? [Retrofit](square.github.io/retrofit/)?
[Finagle](https://twitter.github.io/finagle/)? [gRPC](http://www.grpc.io/)? I
bet it is a matter of time until you end up needing to consume two clients
which have transitive dependencies to two binary incompatible versions of
Retrofit/Finagle/gRPC. You can blame the Java class loader mechanism. But that
doesn't make the problem fade away. Oh! I was just about to forget! Wait until
I migrate to `rx.Completable` from `rx.Single<Void>`, which I migrated from
`rx.Observable<Void>`.

I am exhausted and demotiviated to write yet another single line of code that
needs to communicate with a remote microservice and which could have been
simple fucking RPC. I don't have a solution for the mud ball in my hands. Even
if I do have, I am not sure whether it will survive a couple of years or not.
But at the back of my head, I keep on cursing the Java Platform SE guys: How
difficult could it be to come up with a proper pluggable HTTP client? Compared
to `NPE`, Java's HTTP client is not *the* billion dollar mistake, but a really
close one.
