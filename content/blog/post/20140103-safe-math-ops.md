---
kind: article
created_at: 2014-01-03 20:13 EET
title: Detecting Overflows in Java Arithmetic Operators
tags:
  - java
---

A couple of months ago I came across [The CERT Oracle Secure Coding Standard for Java](https://www.securecoding.cert.org/confluence/display/java/The+CERT+Oracle+Secure+Coding+Standard+for+Java). It is suprising how come I did not find this fascinating resource before. I first skimmed through the chapters and figured out that the recommended conventions are so practical that I can even directly use some of them in my existing code base. Right at that time I was working on a routing engine, which performs some arithmetic operators over link costs. It was a good place to apply the conventions metioned in the chapter [NUM00-J. Detect or prevent integer overflow](https://www.securecoding.cert.org/confluence/display/java/NUM00-J.+Detect+or+prevent+integer+overflow). Hence, I directly copied safe versions of arithmetic operators into my `util` package. (Everybody does have a `util`, right?)

    #!java
    public static int safeAdd(int l, int r) throws OverflowException {
        if (r > 0
                ? l > Integer.MAX_VALUE - r
                : l < Integer.MIN_VALUE - r)
            throw new ArithmeticException(String.format(
                    "Integer overflow: %d + %d", l, r));
        return l + r;
    }

    public static int safeMultiply(int l, int r)
            throws ArithmeticException {
        if (r > 0
                ? l > Integer.MAX_VALUE/r || l < Integer.MIN_VALUE/r
                : (r < -1
                    ? l > Integer.MIN_VALUE/r || l < Integer.MAX_VALUE/r
                    : r == -1 && l == Integer.MIN_VALUE))
            throw new ArithmeticException(String.format(
                    "Integer overflow: %d x %d", l, r));
        return l * r;
    }

To my suprise, I observed integer overflow error messages in the server logs today. Yay! Further examination of the problem revealed that I cause an integer overflow while taking the square of link costs for a particular routing algorithm. Some might argue about the overhead of replacing operators with methods, but let's think about this: How would I ever figure this problem out if I would not be using these safe arithmetic operators. No need to mention about the problem's consequences.
