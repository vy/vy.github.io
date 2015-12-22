---
kind: article
created_at: 2014-02-14 14:22 EET
title: Safe Object Publication in Java
tags:
  - concurrency
  - java
---

I have just finished reading [Java Concurrency in Practice](http://jcip.net/) yesterday and would like to share some excerpts from the book on safe object publication in Java. Before stepping into the details, I would like to state that I found every single page of the book quite useful and found numerous places that I can enhance my existing code base during my daily coding routine. Thanks to [@BrianGoetz](https://twitter.com/BrianGoetz) et al for such a comprehensive and practical guide. (For those who want to go further up to its extremes, I strongly recommend you to check [Aleksey Shipilёv](http://shipilev.net/)'s [Safe Publication and Safe Initialization in Java](http://shipilev.net/blog/2014/safe-public-construction/) article -- a must read on the subject.)

*(Presented excerpts are copied directly, sometimes with slight changes, from [Java Concurrency in Practice](http://jcip.net/).)*

Safe Construction Practices
===========================

An object is in a predictable, consistent state only after its constructor returns, so publishing an object from within its constructor can publish an incompletely constructed object. This is true *even if the publication is the last statement in the constructor*. If the `this` reference escapes during construction, the object is considered *not properly constructed*.

    #!java
    public class ThisEscape {
        public ThisEscape(EventSource source) {
            source.registerListener(
                new EventListener() {
                    public void onEvent(Event event) {
                        doSomething(event);
                    }
                });
        }
    }

Here, when `ThisEscape` publishes the `EventListener`, it implicitly publishes the enclosing `ThisEscape` instance as well, because inner class instances contain a hidden reference to the enclosing instance.

If you are tempted to register an event listener or start a thread from a constructor, you can avoid the improper construction by using a private constructor and a public factory method, as shown in `SafeListener` below.

    #!java
    public class SafeListener {
        private final EventListener listener;

        private SafeListener() {
            listener = new EventListener() {
                public void onEvent(Event event) {
                    doSomething(event);
                }
            }
        }

        public static SafeListener newInstance(EventSource source) {
            SafeListener safe = new SafeListener();
            source.registerListener(safe.listener);
            return safe;
        }
    }

Lazy Initialization
===================

Unsafe publication can happen as a result of an incorrect lazy initialization as follows.

    #!java
    @NotThreadSafe
    public class UnsafeLazyInitialization {
        private static Resource resource;

        public static Resource getInstance() {
            if (resource == null)
                resource = new Resource();
            return resource;
        }
    }

Under certain circumstances, such as when all instances of the `Resource` are identical, you might be willing to overlook these (along with the inefficiency of possibly creating the `Resource` more than once). Unfortunately, even if these defects are overlooked, `UnsafeLazyInitialization` is still not safe, because another thread could observe a reference to a partially constructed `Resource`.

Suppose thread `A` is the first to invoke `getInstance`. It sees that `resource` is `null`, instantiates a new `Resource`, and sets `resource` to reference it. When thread `B` later calls `getInstance`, it might see that `resource` already has a non-null value and just use the already constructed `Resource`. This might look harmless at first, but *there is no happens-before ordering between the writing of `resource` in `A` and the reading of `resource` in `B`*. A data race has been used to publish the object, and therefore `B` is not guaranteed to see the correct state of the `Resource`.

The `Resource` constructor changes the fields of the freshly allocated `Resource` from their default values (written by the `Object` constructor) to their initial values. Since neither thread used synchronization, `B` could possible see `A`'s actions in a different order than `A` performed them. So even though `A` initialized the `Resource` before setting `resource` to reference it, `B` could see the write to `resource` as occuring *before* the writes to the fields of the `Resource`. `B` could thus see a partially constructed `Resource` that may well be in an invalid state -- and whose state may unexpectedly change later.

`UnsafeLazyInitialization` can be fixed by making the `getResource` method `synchronized` as follows.

    #!java
    @ThreadSafe
    public class SafeLazyInitialization {
        private static Resource resource;

        public synchronized static Resource getInstance() {
            if (resource == null)
                resource = new Resource();
            return resource;
        }
    }

Because the code path through the `getInstance` is fairly short (a test and a predicted branch), if `getInstance` is not called frequently by many threads, there is a little enough contention for the `SafeLazyInitialization` lock that this approach offers adequate performance.

The treatment of static fields with initializers (or fields whose value is initialized in a static initialization block \[JPL 2.2.1 and 2.5.3\]) is somewhat special and offers additional thread-safety guarantees. Static initializers are run by the JVM at class initialization time, after class loading but before the class is used by any thread. Because the JVM acquires a lock during initialization \[JSL 12.4.2\] and this lock is acquired by each thread at least once to ensure that the class has been loaded, memory writes made during static initialization are automatically visible to all threads. Thus statically initialized objects require no explicit synchronization either during construction or when being referenced. However, this applies only to the *as-constructed* state -- if the object is mutable, synchronization is still required by both readers and writers to make subsequent modifications visible to avoid data corruption.

    #!java
    @ThreadSafe
    public class EagerInitialization {
        private static Resource resource = new Resource();

        public static Resource getResource() { return resource; }
    }

Using eager initialization eliminates the synchronization cost incurred on each call to `getInstace` in `SafeLazyInitialization`. This technique can be combined with the JVM's lazy class loading to create a lazy initialization technique that does not require synchronization on the common code path. The *lazy initialization holder class* idiom \[EJ Item 48\] presented below uses a class whose only purpose is to initialize the `Resource`.

    #!java
    @ThreadSafe
    public class ResourceFactory {
        private static class ResourceHolder {
            public static Resource resource = new Resource();
        }

        public static Resource getResource() {
            return ResourceHolder.resource;
        }
    }

Here the JVM defers initializing the `ResourceHolder` class until it is actually used \[JLS 12.4.1\], and because the `Resource` is initialized with a static initializer, no additional synchronization is needed. The first call to `getResource` by any thread causes `ResourceHolder` to be loaded and initialized, at which time the initialization of the `Resource` happens through the static initializer.
