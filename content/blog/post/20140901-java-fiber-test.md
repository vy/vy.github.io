---
kind: article
created_at: 2014-08-07 09:28 EET
title: Testing Fiber Implementations in JVM
modules:
  - canvasjs
  - mathjax
tags:
  - akka
  - java
  - quasar
---

I have always been interested in concurrent programming through the use of
threads. This inclination did not originate from a need to exploit the
parallelism at the hardware level for performance reasons, but rather due to the
fact that I believe it establishes a model of reasoning about your code that
provides a more convenient and natural way for encapsulating concurrency in the
overall program flow. I cannot express the relief I felt when I first ported an
asynchronous piece of networking code to
[PThreads](http://en.wikipedia.org/wiki/POSIX_Threads). But my joy did not last
long -- context switching, memory, cache miss costs and more importantly the
physical constraints that bounds the number of threads were waiting for me at
the end of the tunnel. Lucky for me, it did not take much time to figure out the
notion of [Light-weight
processes](http://en.wikipedia.org/wiki/Light-weight_process), which later
introduced me to [Protothreads](http://dunkels.com/adam/pt/). That being said, I
should have admit that I fell back to my single-threaded asynchronous event loop
many times rather than a Protothreads flavored PThreads spaghetti. I suppose
every programmer had once dreamed about having light-weight threads that maps to
a multitude of physical CPU cores via some sort of mechanism in the background,
many similar efforts in the literature ([Plan9
rfork](http://swtch.com/plan9port/man/man3/rfork.html), [Solaris
LWP](http://www.princeton.edu/~unix/Solaris/troubleshoot/process.html), [NetBSD
lwp_create](http://www.daemon-systems.org/man/_lwp_create.2.html)) backs this
claim, I suppose.

Threads, Coroutines, and Fibers
===============================

The heart of the problem lies in the question of mapping $$m$$ light-weight
threads to $$n$$ physical processor cores ($$m \gg n$$) given that the operating
system has no prior knowledge on what is going on at the application level. As
an inevitable consequence of this problem, developers come up with the idea of
providing application level constructs to hint the underlying process scheduling
mechanism about the concurrency operating at the application level. Among many
other attempts, [coroutines](http://en.wikipedia.org/wiki/Coroutine) and
[fibers](http://en.wikipedia.org/wiki/Fiber_(computer_science)) are the two
well-known examples emanated from this research. Quoting from
[Wikipedia](http://en.wikipedia.org/wiki/Fiber_(computer_science)),

> Fibers describe essentially the same concept as coroutines. The distinction,
> if there is any, is that coroutines are a language-level construct, a form of
> control flow, while fibers are a systems-level construct, viewed as threads
> that happen not to run concurrently. Priority is contentious; fibers may be
> viewed as an implementation of coroutines, or as a substrate on which to
> implement coroutines.

If I would try to restate the given description from a more naive perspective
targeting the Java Virtual Machine, _coroutines are language-level constructs to
form a way of cooperative execution of multiple tasks, whereas fibers are
light-weight threads scheduled preemptively by the virtual machine_. There is [a
set of coroutine
implementations](http://stackoverflow.com/questions/2846428/available-coroutine-libraries-in-java)
available for JVM, but in this post I will try to stick with two particular
fiber implementations: [Akka](http://akka.io/) from
[Typesafe](http://typesafe.com/) and
[Quasar](http://docs.paralleluniverse.co/quasar/) from [Parallel
Universe](http://paralleluniverse.co/).

Akka and Quasar
===============

Last year I had a plenty amount of time to play around with
[Akka](http://akka.io/) during the [The Principles of Reactive
Programming](https://www.coursera.org/course/reactive) course. Claiming that
Akka is just a toolkit to realize fibers on the JVM would be a fairly incomplete
definition -- it is totally much more than that. Designed for resiliency from
top to ground, a gigantic toolbox of common messaging pattern shortcuts,
adaptive load balancing, routing, partitioning, and configuration-driven
remoting, etc. just to name a few. Additionally, one should note that it is
battle-tested with real-world work loads by means of both as a standalone
application and a compound to the [Typesafe
Platform](https://typesafe.com/platform).

On the other hand, [Quasar](http://docs.paralleluniverse.co/quasar/) is a
relatively new player in this league. That being said, it is implemented as a
compact library with -- in my opinion -- a relatively sufficient set of
features. Though it has a lot to go to catch Akka in terms of out of the box
features. In addition, while Akka just provides
[actor](http://en.wikipedia.org/wiki/Actor_model) abstractions at the
programming language level, Quasar ships both actors and fibers. (Actually,
Quasar actors are built on top of fibers.) Quoting from Quasar core developer
Ron Pressler's
[post](https://groups.google.com/d/msg/quasar-pulsar-user/NrYOyUTqdcg/MFPl6S0USigJ):

> Quasar and Akka provide completely different abstractions. Quasar provides
> fibers while Akka provides an asynchronous-programming framework based on
> callbacks. Both libraries then implement actors using their respective
> abstractions. \[...\] fibers are lightweight threads, which
> means that their most important property -- even before being light-weight --
> is being threads. The thread abstraction is a series of sequential
> computations with the ability to block -- on IO or synchronization. Callbacks,
> on the other hand, are a completely different abstraction. Akka’s callbacks
> (and therefore actors), are not allowed to block, and therefore do not provide
> a thread abstraction; hence they’re not fibers.
>
> Quasar’s main design goal was the desire to make the simple, familiar,
> threading abstraction (i.e., synchronous, blocking code) cheap, as kernel
> threads are expensive, and blocking a kernel thread carries a lot of overhead.
> Quasar is used to run servlets that serve hundreds of thousands of concurrent
> requests -- instead of mere thousands -- all without changing your existing
> Java code. We want developers get the full performance benefits of
> asynchronous code -- which Akka also offers -- while keeping their APIs and
> synchronous programming model -- which Akka certainly doesn’t. Quasar makes
> threading cheap, while Akka abandons the thread abstraction altogether. In
> that respect, Quasar is a lot more similar to Erlang and Go (which, of course,
> provided the inspiration to Quasar), which also use the thread abstraction but
> provide a lightweight thread implementation.
>
> Akka’s design goals are different, and we think Quasar is far simpler to use
> than Akka, requires less mental overhead and far-less re-engineering, while at
> the same time being more feature-rich.

The Benchmark
=============

In order to have an idea on how two implementations compare to each other in
terms of performance, I put together a small benchmark suite
([fiber-test](https://github.com/vy/fiber-test/)) that employs both Akka (2.3.5)
and Quasar (0.6.0) for the well-known
[thread-ring](http://www.sics.se/~joe/ericsson/du98024.html) problem. ($$n$$
threads are spawned and connected as a ring structure. Through this ring a
message -- an integer comprising 4 bytes -- is circulated involving $$m$$
message passings.) In addition, I included a version of the benchmark that uses
Java Threads to establish a base line.

In [fiber-test](https://github.com/vy/fiber-test/), you will observe that
[benchmark.sh](https://github.com/vy/fiber-test/blob/master/benchmark.sh)
employs [taskset](http://linux.die.net/man/1/taskset) to bond the JVM to a given
set of CPUs on the system. However, for small number (1-2) of CPUs, Quasar
freezes randomly and Java Threads become totally unresponsive. Hence, I get rid
off of the `taskset` for the figures presented here.

Tests are deployed on a Ubuntu GNU/Linux 14.04 (LTS) system running on a 6
physical core Intel(R) Xeon(R) E5645 2.40GHz processor, where 64-bit Java
HotSpot VM (build 1.8.0_20-ea-b05) is used.
[JMH](http://openjdk.java.net/projects/code-tools/jmh/) is set to run 5+5 warmup
and regular iterations using 3 JVM forks. There are 503 threads in each
benchmark and 1e7 message passings. Results are in milliseconds per benchmark.

<table id="results">
	<thead>
		<tr>
			<th>Fiber Impl.</th>
			<th>Min.</th>
			<th colspan="2">Avg.</th>
			<th>Max.</th>
			<th>Stddev.</th>
			<th colspan="3">Confidence Interval</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>Quasar Fibers</td>
			<td>695.613</td>
			<td>29x</td>
			<td>721.457</td>
			<td>758.231</td>
			<td>20.796</td>
			<td>99.9%</td>
			<td>699.226</td>
			<td>743.689</td>
		</tr>
		<tr>
			<td>Akka Actors</td>
			<td>856.807</td>
			<td>23x</td>
			<td>911.295</td>
			<td>963.403</td>
			<td>34.345</td>
			<td>99.9%</td>
			<td>874.578</td>
			<td>948.012</td>
		</tr>
		<tr>
			<td>Quasar Actors</td>
			<td>1553.224</td>
			<td>13x</td>
			<td>1606.718</td>
			<td>1660.329</td>
			<td>35.756</td>
			<td>99.9%</td>
			<td>1568.492</td>
			<td>1644.943</td>
		</tr>
		<tr>
			<td>Java Threads</td>
			<td>15730.028</td>
			<td>1x</td>
			<td>20709.233</td>
			<td>33084.117</td>
			<td>4338.423</td>
			<td>99.9%</td>
			<td>16071.196</td>
			<td>25347.270</td>
		</tr>
	</tbody>
</table>
<style type="text/css">
table#results tbody tr td { text-align: right; }
table#results thead tr th { text-align: center; }
table#results td { padding: 1px; }
</style>

<div id="chartContainer" style="margin: 0 auto; height: 100px; width: 75%"></div>
<script type="text/javascript">
asyncLoadRequests.push(function() {
	var chart = new CanvasJS.Chart("chartContainer", {
			backgroundColor: "transparent",
			creditText: null,
			axisX: {
				interval: 1,
				gridThickness: 0,
				labelFontSize: 10,
				labelFontStyle: "normal",
				labelFontWeight: "normal",
				labelFontFamily: "'Arial', sans"
			},
			axisY2: {
				labelFontSize: 10,
				labelFontStyle: "normal",
				labelFontWeight: "normal",
				labelFontFamily: "'Arial', sans",
				interlacedColor: "rgba(1,77,101,.2)",
				gridColor: "rgba(1,77,101,.1)"
			},
			data: [{
				type: "bar",
                name: "companies",
				axisYType: "secondary",
				color: "#014D65",
				dataPoints: [
					{y: 20709.233, label: "Java Threads"},
					{y: 1606.718, label: "Quasar Actors"},
					{y: 911.295, label: "Akka Actors"},
					{y: 721.457, label: "Quasar Fibers"}
				]
			}]
		});
	chart.render();
});
</script>

Results point out that even in the worst case (which corresponds to Quasar
Actors in the figures) fiber implementation on the average performs 13 times
better compared to native Java threads. In addition, Akka Actors and Quasar
Fibers improve this level up to 23x and 29x, respectively. All that being said
and done, I could not reason about the performance difference between Quasar
Fibers and Actors, given that actors are implemented using fibers in Quasar. In
order to further investigate the problem, I profiled the benchmarks using
`-agentlib:hprof=cpu=samples,interval=20,depth=3`. (See
[HPROF](http://docs.oracle.com/javase/7/docs/technotes/samples/hprof.html)
documentation for further information on the parameters.)

<table id="hprof">
	<thead>
		<tr>
			<th>rank</th>
			<th>self</th>
			<th>accum</th>
			<th>count</th>
			<th>trace</th>
			<th>method</th>
		</tr>
	</thead>
	<tbody>
		<tr><th colspan="6">Quasar Fibers</th></tr>
		<tr class="highlight"><td>1</td><td>47,55%</td><td>47,55%</td><td>67286</td><td>300366</td><td>co.paralleluniverse.fibers.Fiber.run1</td></tr>
		<tr><td>2</td><td>47,48%</td><td>95,04%</td><td>67186</td><td>300364</td><td>com.github.vy.fibertest.QuasarFiberRingBenchmark$InternalFiber.run</td></tr>
		<tr><td>3</td><td>3,37%</td><td>98,40%</td><td>4765</td><td>300372</td><td>com.github.vy.fibertest.QuasarFiberRingBenchmark$InternalFiber.run</td></tr>
		<tr><th colspan="6">Quasar Actors</th></tr>
		<tr><td>1</td><td>22,17%</td><td>22,17%</td><td>77787</td><td>300526</td><td>co.paralleluniverse.fibers.Fiber.park1</td></tr>
		<tr><td>2</td><td>18,53%</td><td>40,69%</td><td>65011</td><td>300508</td><td>co.paralleluniverse.fibers.Fiber.run</td></tr>
		<tr class="highlight"><td>3</td><td>18,32%</td><td>59,01%</td><td>64292</td><td>300527</td><td>co.paralleluniverse.strands.channels.SingleConsumerQueueChannel.receive</td></tr>
		<tr><td>4</td><td>18,27%</td><td>77,28%</td><td>64114</td><td>300517</td><td>com.github.vy.fibertest.QuasarActorRingBenchmark$InternalActor.doRun</td></tr>
		<tr><td>5</td><td>17,39%</td><td>94,67%</td><td>61009</td><td>300528</td><td>co.paralleluniverse.actors.ActorRunner.run</td></tr>
		<tr><th colspan="6">Akka Actors</th></tr>
		<tr class="highlight"><td>1</td><td>64,09%</td><td>64,09%</td><td>5158</td><td>300307</td><td>scala.concurrent.forkjoin.ForkJoinPool.runWorker</td></tr>
		<tr><td>2</td><td>12,51%</td><td>76,60%</td><td>1007</td><td>300298</td><td>sun.misc.Unsafe.park</td></tr>
		<tr><td>3</td><td>10,69%</td><td>87,29%</td><td>860</td><td>300309</td><td>sun.misc.Unsafe.unpark</td></tr>
		<tr><td>4</td><td>2,65%</td><td>89,94%</td><td>213</td><td>300300</td><td>scala.concurrent.forkjoin.ForkJoinPool.scan</td></tr>
		<tr><td>5</td><td>1,12%</td><td>91,05%</td><td>90</td><td>300316</td><td>akka.dispatch.Dispatcher.dispatch</td></tr>
		<tr><th colspan="6">Java Threads</th></tr>
		<tr class="highlight"><td>1</td><td>94,33%</td><td>94,33%</td><td>10373</td><td>300057</td><td>sun.misc.Unsafe.unpark</td></tr>
		<tr><td>2</td><td>5,59%</td><td>99,93%</td><td>615</td><td>300058</td><td>sun.misc.Unsafe.park</td></tr>
	</tbody>
</table>
<style type="text/css">
table#hprof tr.highlight td { color: red; }
table#hprof td { padding: 1px; }
</style>

As anticipated, Java Threads were bitten by `park`/`unpark` methods in
`sun.misc.Unsafe`. Whereas, Akka Actors and Quasar Fibers perform some sort of
interleaving between routines to avoid these calls and that totally rocks.
Unfortunately, it turns out that the channel mechanisms (e.g.,
`co.paralleluniverse.strands.channels.SingleConsumerQueueChannel`) in Quasar
Actors somehow trigger the Quasar core to employ `park` calls in between the
message receivers and that predominantly consumes the majority of the fiber
runtime.

The Conclusion
==============

Observing that fiber implementations perform superior compared to standard Java
Threads is nothing new. However, seeing Quasar Fibers showing up impressive
performance is not something I was expecting, considering that the project is in
its very early stages. That being said, it appears that channels in Quasar
Actors have a certain room for improvement and might borrow some ideas from its
Akka counterpart. In the overall, both fiber implementations show stable and
noteworthy performance figures and stand as a perfect standard Java Thread
replacement for a considerable amount of use cases.
