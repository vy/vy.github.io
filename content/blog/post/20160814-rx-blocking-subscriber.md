---
kind: article
created_at: 2016-08-14 22:49 CET
title: Testing Rx Observables Using a Blocking Subscriber
tags:
  - java
  - rx
  - test
---

Asynchronous event-driven programming model advocated by
[Rx](http://reactivex.io/) can make it gruelling and tedious to test your
applications.
[TestSubscriber](https://labs.ribot.co.uk/unit-testing-rxjava-6e9540d4a329)
provided by Rx is a good programmer companion to mitigate this problem and
ease unit testing of such applications. But what if you are testing against
asynchronously triggered events in a separate thread? Consider the following
case.

    #!java
    import com.google.common.base.Throwables;
    import rx.Observable;
    import rx.subjects.PublishSubject;

    public class DelayedPublisher {

        private final PublishSubject<Double> subject = PublishSubject.create();

        public void publish() {
            new Thread() {
                @Override
                public void run() {
                    try { Thread.sleep(1000); }
                    catch (InterruptedException error) { Throwables.propagate(error); }
                    double next = Math.random();
                    subject.onNext(next);
                }
            }.start();
        }

        public Observable<Double> asObservable() {
            return subject;
        }

    }

How would you test `DelayedPublisher`? Let's try to put `TestSubscriber` into
use:

    #!java
    import org.junit.Test;
    import rx.Observable;
    import rx.observers.TestSubscriber;

    import java.util.List;

    import static org.assertj.core.api.Assertions.assertThat;

    public class DelayedPublisherTest {

        @Test
        public void shouldPublish() {

            // Create a delayed publisher.
            DelayedPublisher publisher = new DelayedPublisher();
            Observable<Double> observable = publisher.asObservable();

            // Subscribe to the publisher using Rx TestSubscriber.
            TestSubscriber<Double> subscriber = TestSubscriber.create();
            observable.subscribe(subscriber);

            // Try to observe a publish.
            publisher.publish();
            List<Double> events = subscriber.getOnNextEvents();
            assertThat(events).isNotNull().isNotEmpty();

        }

    }

As expected, the assertion will fail since `subscriber.getOnNextEvents()` runs
immediatly after `publisher.publish()` without a delay. But internally publish
kicks in 1 second after the `publisher.publish()` call. Hence,
`TestSubscriber` returns an empty list and serves no purpose in this case.

If you Google for possible solutions, you might stumble across approaches like
[replacing all Rx schedulers with
Schedulers.immediate()](http://fedepaol.github.io/blog/2015/09/13/testing-rxjava-observables-subscriptions/),
which I personally find a sort of hack and more importantly, does not cover
the above presented case.

An alternative approach that you can take is just *acting like the actual
consumer*, and hence blocking whenever needed, as the actual consumer would
also do. For this purpose, I come up with the following `RxBlockingSubscriber`
in a similar fashion to the `TestSubscriber`:

    #!java
    import com.google.common.base.Throwables;
    import org.slf4j.Logger;
    import org.slf4j.LoggerFactory;
    import rx.Subscriber;

    import java.util.concurrent.ArrayBlockingQueue;
    import java.util.concurrent.BlockingQueue;
    import java.util.concurrent.TimeUnit;
    import java.util.concurrent.TimeoutException;
    import java.util.stream.IntStream;

    import static com.google.common.base.Preconditions.checkArgument;

    /**
     * Unit test friendly Rx subscriber backed by a BlockingQueue.
     */
    public class RxBlockingSubscriber<T> extends Subscriber<T> {

        private static final Logger LOGGER = LoggerFactory.getLogger(RxBlockingSubscriber.class);

        private final BlockingQueue<Object> events;

        private final int timeoutMillis;

        private boolean completed = false;

        /**
         * @param bufferSize queue size
         * @param timeoutMillis timeout for queue push/pop calls
         */
        public RxBlockingSubscriber(int bufferSize, int timeoutMillis) {
            checkArgument(bufferSize > 0, "bufferSize > 0, found: %d", bufferSize);
            checkArgument(timeoutMillis > 0, "timeoutMillis > 0, found: %d", timeoutMillis);
            this.events = new ArrayBlockingQueue<>(bufferSize);
            this.timeoutMillis = timeoutMillis;
        }

        @Override
        public synchronized void onCompleted() {
            LOGGER.trace("completed");
            completed = true;
        }

        @Override
        public void onError(Throwable error) {
            offer(error);
        }

        @Override
        public void onNext(T next) {
            offer(next);
        }

        private synchronized void offer(Object event) {
            if (!completed) {
                try { events.offer(event, timeoutMillis, TimeUnit.MILLISECONDS); }
                catch (InterruptedException error) { throw Throwables.propagate(error); }
            }
        }

        /**
         * Blocks until getting the next emitted item (can be an error as well) and returns it.
         */
        public Object take() {
            try {
                Object next = events.poll(timeoutMillis, TimeUnit.MILLISECONDS);
                if (next == null) { throw new TimeoutException(); }
                return next;
            } catch (InterruptedException | TimeoutException error) {
                throw Throwables.propagate(error);
            }
        }

        /**
         * Calls {@link RxBlockingSubscriber#take()} {@code count} times.
         */
        public void skip(int count) {
            checkArgument(count > 0, "count > 0, found: %d", count);
            IntStream.range(0, count).forEach(ignored -> take());
        }

    }

Let's try testing `DelayedPublish` using `RxBlockingSubscriber`:

    #!java
    import org.junit.Test;
    import rx.Observable;

    import static org.assertj.core.api.Assertions.assertThat;

    public class DelayedPublisherTest {

        @Test
        public void shouldPublish() {

            // Create a delayed publisher.
            DelayedPublisher publisher = new DelayedPublisher();
            Observable<Double> observable = publisher.asObservable();

            // Subscribe to the publisher using RxBlockingSubscriber.
            RxBlockingSubscriber<Double> subscriber = new RxBlockingSubscriber<>(1, 1500);
            observable.subscribe(subscriber);

            // Try to observe a publish.
            publisher.publish();
            Object item = subscriber.take();
            assertThat(item).isNotNull().isInstanceOf(Double.class);

        }

    }

Note that in the above test we just employed `RxBlockingSubscriber#take()`
method. But you can similarly use `onNext()`, `onError()`, and `onCompleted()`
as well in a similar fashion to `TestSubscriber`.
