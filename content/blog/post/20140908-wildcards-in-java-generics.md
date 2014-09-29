---
kind: article
created_at: 2014-09-08 16:42 EET
title: Wildcards in Java Generics
tags:
  - java
---

I always had a hard time with understanding wildcarded generics in Java, as in
`<? extends A>` or `<? super A>`. While [More Fun with
Wildcards](http://docs.oracle.com/javase/tutorial/extra/generics/morefun.html)
is a good place for start, you come to a *TL;DR* point after some time. Lucky
for me, Heikki (fizzie) Kallasjoki provided me a succinct and complete code
snippet that summarizes the entire issue on [freenode](http://freenode.net/)
`##java` channel.

First, let's assume we have two classes `A` and `B` as follows.

    #!java
    class A {}

    class B extends A {}

And here is the code snippet that summarizes the entire issue with wildcarded
generics in Java.

    #!java
    static void f(List<? extends A> l) {
        A a = l.get(0); /* okay */
        l.add(new A()); /* not okay, l can be of type List<B> */
    }

    static void g(List<A> l) {
        A a = l.get(0); /* okay */
        l.add(new A()); /* okay */
    }

    static void h(List<? super A> l) {
        A a = l.get(0); /* not okay, l can be of type List<Object> */
        l.add(new A()); /* okay */
    }

    static {
        List<B> l = new ArrayList<>();
        f(l);           /* okay */
        g(l);           /* not okay, List<B> is not of type List<A> */
        h(l);           /* not okay, List<B> is not of type List<? super A> */

        List<Object> l2 = new ArrayList<>();
        f(l2);          /* not okay, List<Object> is not of type List<? extends A> */
        g(l2);          /* not okay, List<Object> is not of type List<A> */
        h(l2);          /* okay */
    }

Hope that helps.
