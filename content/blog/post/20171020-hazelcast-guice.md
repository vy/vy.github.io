---
kind: article
created_at: 2017-04-18 17:22 CET
title: Guice Integration in Hazelcast
tags:
  - guice
  - hazelcast
  - java
---

For many occassions I find the distributed `ExecutorService` of Hazelcast
(aka. `IExecutorService`) pretty convenient to turn a set of nodes into a
tamed cluster waiting for orders. You just submit an either `Runnable` or
`Callable<T>` and Hazelcast takes care of the rest -- executing the task on
remote members, acknowledging the response(s) back, etc. Though note that
since the method and its response will be delivered over the wire, it is no
surprise that they all need to be `Serializable`.

    #!java
    import com.hazelcast.core.Hazelcast;
    import com.hazelcast.core.HazelcastInstance;
    import com.hazelcast.core.IExecutorService;
    import com.hazelcast.core.Member;
    import com.hazelcast.core.MultiExecutionCallback;

    import java.io.Serializable;
    import java.util.Map;
    import java.util.concurrent.Callable;
    import java.util.concurrent.CompletableFuture;
    import java.util.concurrent.TimeUnit;

    public enum HzGuiceDemo {;

        public static class ProcessorCountTask implements Serializable, Callable<Integer> {

            @Override
            public Integer call() {
                return Runtime.getRuntime().availableProcessors();
            }

        }

        public static void main(String[] args) throws Throwable {
            HazelcastInstance hzInstance = Hazelcast.newHazelcastInstance();
            IExecutorService hzExecutorService = hzInstance.getExecutorService("ballpark");
            CompletableFuture<Integer> totalProcessorCountFuture = new CompletableFuture<>();
            hzExecutorService.submitToAllMembers(
                    new ProcessorCountTask(),
                    new MultiExecutionCallback() {

                        @Override
                        public void onResponse(Member member, Object value) {
                            // Ignored.
                        }

                        @Override
                        public void onComplete(Map<Member, Object> values) {
                            int totalProcessorCount = values
                                .values()
                                .stream()
                                .mapToInt(object -> (int) object)
                                .sum();
                            totalProcessorCountFuture.complete(totalProcessorCount);
                        }

                    });
            int totalProcessorCount = totalProcessorCountFuture.get(10, TimeUnit.SECONDS);
            System.out.format("there are %d processors in total%n", totalProcessorCount);
            hzInstance.shutdown();
        }

    }

Unfortunately many of our tasks are not isolated from the rest of the
application state (i.e., *stateless*) as `ProcessorCountTask` given above.
Most of the time the functional requirements necessitate access to the remote
node state that is available through beans provided by the underlying
dependency injection framework. Consider the following stateful `PizzaService`
that is responsible for cooking pizzas to its users.

    #!java
    import javax.inject.Singleton;

    import static com.google.common.base.Preconditions.checkArgument;

    @Singleton
    public static class PizzaService {

        private volatile int totalPizzaCount = 0;

        public synchronized int cook(int amount) {
            checkArgument(amount > 0, "expecting: amount > 0, found: %s", amount);
            availablePizzaCount += amount;
            System.out.format("🍕 cooking %d pizza(s)%n", amount);
        }

    }

We further have a task class to remotely command `PizzaService` to cook:

    #!java
    import java.io.Serializable;

    public static class PizzaCookTask implements Serializable, Runnable {

        @Inject
        private PizzaService pizzaService;

        private final int amount;

        public PizzaMakeTask(int amount) {
            this.amount = amount;
        }

        @Override
        public void run() {
            pizzaService.cook(amount);
        }

    }

A naive approach to run this task on an `IExecutorService` would result in the
following code:

    #!java
    import com.hazelcast.core.Hazelcast;
    import com.hazelcast.core.HazelcastInstance;
    import com.hazelcast.core.IExecutorService;

    import java.util.concurrent.CompletableFuture;
    import java.util.concurrent.TimeUnit;

    public enum HzGuiceDemo {;

        public static void main(String[] args) throws Throwable {
            HazelcastInstance hzInstance = Hazelcast.newHazelcastInstance();
            IExecutorService hzExecutorService = hzInstance.getExecutorService("ballpark");
            hzExecutorService.executeOnAllMembers(new PizzaCookTask(1));
            hzInstance.shutdown();
        }

    }

which fails with a sweet `NullPointerException` as follows:


    Exception in thread "main" java.util.concurrent.ExecutionException: java.util.concurrent.ExecutionException: java.lang.NullPointerException
      at java.util.concurrent.CompletableFuture.reportGet(CompletableFuture.java:357)
      at java.util.concurrent.CompletableFuture.get(CompletableFuture.java:1915)
      at com.vlkan.hzguicedemo.HzGuiceDemo.main(HzGuiceDemo.java:??)
    Caused by: java.util.concurrent.ExecutionException: java.lang.NullPointerException
      at java.util.concurrent.FutureTask.report(FutureTask.java:122)
      at java.util.concurrent.FutureTask.get(FutureTask.java:192)
      at com.hazelcast.executor.DistributedExecutorService$CallableProcessor.run(DistributedExecutorService.java:189)
      at com.hazelcast.util.executor.CachedExecutorServiceDelegate$Worker.run(CachedExecutorServiceDelegate.java:186)
      at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1142)
      at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
      at java.lang.Thread.run(Thread.java:745)
      at com.hazelcast.util.executor.HazelcastManagedThread.executeRun(HazelcastManagedThread.java:76)
      at com.hazelcast.util.executor.HazelcastManagedThread.run(HazelcastManagedThread.java:92)
    Caused by: java.lang.NullPointerException
      at com.vlkan.hzguicedemo.HzGuiceDemo$PizzaCookTask.call(HzGuiceDemo.java:??)
      at com.vlkan.hzguicedemo.HzGuiceDemo$PizzaCookTask.call(HzGuiceDemo.java:??)

What is really happening here is that Hazelcast does not have a magical ball
to guess the dependency injection framework you are using to process the
`@Inject`-annotated properties of the `PizzaCookTask`. Though Hazelcast has
something else:
[ManagedContext](http://docs.hazelcast.org/docs/2.3/manual/html/ch14s02.html).
In a nutshell, `ManagedContext` provides means to intercept class
instantiation at deserialization. We can leverage this functionality to come
up with a `ManagedContext` implementation that bakes Guice dependency
injection into the Hazelcast class instantiation process.

    #!java
    import com.google.inject.Injector;
    import com.hazelcast.core.ManagedContext;

    import javax.inject.Inject;
    import javax.inject.Singleton;

    @Singleton
    public class HazelcastGuiceManagedContext implements ManagedContext {

        private final Injector injector;

        @Inject
        public HazelcastGuiceManagedContext(Injector injector) {
            this.injector = injector;
        }

        @Override
        public Object initialize(Object instance) {
            injector.injectMembers(instance);
            return instance;
        }

    }

Next all you need to do is to use this `ManagedContext` while creating your
`HazelcastInstance`:

    #!java
    Injector injector = Guice.createInjector();
    HazelcastGuiceManagedContext guiceManagedContext = injector.getInstance(HazelcastGuiceManagedContext.class);
    Config hzConfig = new Config();
    hzConfig.setManagedContext(guiceManagedContext);
    HazelcastInstance hzInstance = Hazelcast.newHazelcastInstance(hzConfig);

While I have provided an example for Guice, this method is applicable to any
dependency injection framework that provides an equivalent to
`Injector#injectMembers()` of Guice. Needless to say, but Spring folks are
already covered by `SpringManagedContext` shipped with Hazelcast.
