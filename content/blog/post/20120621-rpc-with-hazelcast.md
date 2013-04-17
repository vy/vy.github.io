---
kind: article
created_at: 2012-06-21 13:16 EET
title: RPC (Remote Procedure Call) with Hazelcast
tags:
  - hazelcast
  - java
---

Despite the fact that [Hazelcast](http://www.hazelcast.com/) is a data distribution (particularly, peer-to-peer) platform for Java, its group communication mechanics can be utilized for remote procedure calls in a similar fashion to [JGroups remote procedure calls](http://vyazici.blogspot.com/2012/04/rpc-remote-procedure-call-with-jgroups.html). Further, to ease this workflow, Hazelcast provides [distributed executor service](http://hazelcast.com/docs/2.1/manual/multi_html/ch09.html) to execute [`Callable`](http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/Callable.html) and [`Runnable`](http://docs.oracle.com/javase/6/docs/api/java/lang/Runnable.html) instances on the remote cluster members. Now, let's glue things together for making remote procedure calls on Hazelcast cluster members.

Assuming that you have some familiarity with executor services, check out below `SimpleRPC` class, which makes use of the Hazelcast executor service to invoke a `Call` instance on every cluster member.

    #!java
    import com.hazelcast.core.Hazelcast;
    import com.hazelcast.core.MultiTask;
    
    import java.util.Arrays;
    import java.util.Collection;
    import java.util.concurrent.ExecutionException;
    import java.util.concurrent.ExecutorService;
    import java.util.concurrent.TimeUnit;
    import java.util.concurrent.TimeoutException;
    
    public class SimpleRPC {
        private static SimpleRPC instance = null;
    
        private SimpleRPC() {}
    
        public static SimpleRPC getInstance() {
            if (instance == null)
                instance = new SimpleRPC();
            return instance;
        }
    
        @SuppressWarnings("unused")
        public boolean callMe(String input) {
            System.out.println(String.format("callMe('%s') is called!", input));
            return true;
        }
    
        public void callEvery(String input)
                throws ExecutionException, TimeoutException, InterruptedException {
            MultiTask<Boolean> task = new MultiTask<Boolean>(new Call(input),
                    Hazelcast.getCluster().getMembers());
            ExecutorService executorService = Hazelcast.getExecutorService();
            executorService.execute(task);
            Collection<Boolean> results = task.get(3, TimeUnit.SECONDS);
            System.out.println(String.format("callEvery('%s'): %s",
                    input, Arrays.toString(results.toArray())));
        }
    
        public static void main(String[] args) throws Exception {
            SimpleRPC.getInstance().callEvery("foo bar baz");
        }
    }

Since `SimpleRPC` is a singleton, whose instance is accessible via its `getInstance()` method, foreign classes can easily invoke its `callMe()` instance method. Now let's implement the `Call` class, which is anticipated to encapsulate the necessary mechanics to make a call to `SimpleRPC.getInstance().callMe()` on each cluster member.

    #!java
    import java.io.Serializable;
    import java.util.concurrent.Callable;
    
    public class Call implements Callable<Boolean>, Serializable {
        protected String input;
    
        public Call(String input) {
            this.input = input;
        }
    
        public Boolean call() {
            return SimpleRPC.getInstance().callMe(input);
        }
    }

Simple, eh?
