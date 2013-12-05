---
kind: article
created_at: 2013-12-04 18:44 EET
title: "Key to Parallel Combinations: Enumeration"
modules:
  - mathjax
tags:
  - algorithm
  - concurrency
  - java
---

Combinations have many use cases in the daily life of a programmer: for
testing a given function, for generating the all possible input sets of a
particular problem instance, etc. Writing them down in lexicographic order is
something we all do time to time. For instance, 2-combination of a set
$$(0, 1, 2, 3)$$ can simply be written as follows.

$${(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)}$$

We also have a shortcut to get the total number of combinations for a particular
instance. That is,

$${n \choose r} = \frac{n(n-1)\ldots(n-r+1)}{r(r-1)\dots1}=\frac{n!}{r!(n-r)!},$$

which applies to our above example 4-choose-2 as follows:
$${4 \choose 2} = \frac{4 \times 3}{2} = 6$$.

You might also have noticed the pattern we used to generate the combinations in
lexicographic order. The algorithm finds the rightmost index element that can be
incremented, increments it, and then changes the elements to the right to each
be 1 plus the element on their left. This procedure repeats until there are no
more rooms left to increment. (You might want to check out [Applied
Combinatorics](http://eu.wiley.com/WileyCDA/WileyTitle/productCd-
EHEP001993.html) by Alan Tucker for further details of the algorithm.)

One advantage of generating combinations in lexicographic order using the above
algorithm is that given the $$k$$'th combination, one can easily generate
$$k+1$$'th combination. Which leads us to the fact that one can continue
generating combinations given the combination at a particular position.

The Problem
===========

In the case of a single consumer, one can iterate over a set of combinations
step by step. However, what if there are multiple consumers? In this case, a
single producer can present a central combination queue, where it pushes new
combinations on demand, and then the consumers can poll the queue as they
desire. That being said, in this setup the producer can become the bottleneck.
That is, what if consumers poll the queue at a speed faster than the producer's
push rate? Houston, we have a problem.

Previously we have seen that given the $$k$$'th combination, we can compute the
$$k+1$$'th one. In addition, we also know how to calculate the total number of
combinations, that is, $${n \choose r}$$. With this in mind, we can split the
all possible combinations set $$\{c_1, c_2, \dots\}$$ into two separate parts:

$$
\{c_1, \dots, c_m\} \textrm{ and } \{c_{m+1}, \dots, c_l\}, \\
\textrm{where } l = {n \choose r} \textrm{ and } m = \lfloor ^l/_2 \rfloor.
$$

Going from $$c_1$$ to $$c_m$$ is trivial, we can keep a counter for the
generated combinations up to $$m$$. But what about $$c_{m+1}$$? How can we
compute the $${m+1}$$'th combination without having a prior information about
$$m$$'th one. In other words, can we calculate $$c_{m+1}$$, given just $$n$$ and
$$r$$?

Enumerating Combinations
========================

Lucky for us, there exists a vast literature for [combinatorial number
system](http://en.wikipedia.org/wiki/Combinatorial_number_system), where people
come up with a way to enumerate combinations. Long story short, combinatorial
number system presents a mapping between natural numbers (taken to include 0)
and the combinations. To begin with, we first need to talk about *combinadics*.

In a combinatorial number system of degree $$r$$, each natural number
$$b\in\mathbb{N}$$ map to a one and only one *combinadic*
$$[d_1, d_2, \dots, d_k]$$ given in the following equation.

$$
b = {d_1 \choose r} + {d_2 \choose r-1} + \dots + {d_r \choose 1},\\
\textrm{ where } d_1 > d_2 > \dots > d_r.
$$

For instance, let $$b=8$$ and $$r=2$$. Here $$b$$ corresponds to the combinadic
$$[4, 2]$$ in combinatorial number system of degree $$r$$ with the following
equality.

$$8 = {4 \choose 2} + {2 \choose 1}$$

So far so good. Let's do the magic. Suppose that we want to enumerate the
combinations of 5-choose-2. That is, we want the following mapping.

$$
0 \rightarrow [0, 1] \quad 5 \rightarrow [1, 3] \\
1 \rightarrow [0, 2] \quad 6 \rightarrow [1, 4] \\
2 \rightarrow [0, 3] \quad 7 \rightarrow [2, 3] \\
3 \rightarrow [0, 4] \quad 8 \rightarrow [2, 4] \\
4 \rightarrow [1, 2] \quad 9 \rightarrow [3, 4]
$$

We know that $${5 \choose 2} = 10$$, hence we have 10 combinations enumerated
from 0 to 9. Let's try to find the 3rd combination in this sequence from
scratch.

1. First, we set $$i$$ to the index of the combination we are interested in: $$i=3$$
2. Second, we set $$j$$ to the dual index of $$i$$ in $${5 \choose 2}$$ system:
   $$j = {5 \choose 2} - i - 1 = 6$$.
3. Now let's find the combinadic of $$j$$: $$6 = {4 \choose 2} + {0 \choose 1}$$,
   that is, the combinadic corresponding to $$j=6$$ is $$[4, 0]$$.
4. Next we subtract the found comdinadic from the mask $$[4, 4]$$, where 4's
   comes from $$5-1$$: $$[4, 4] - [4, 0] = [0, 4]$$.

Yay! 3rd combination of $${5 \choose 2}$$ system is $$[0, 4]$$! Hrm... Was that
a coincidence? Let's give it another try with 8th combination this time.

1. First, we set $$i$$ to the index of the combination we are interested in: $$i=8$$
2. Second, we set $$j$$ to the dual index of $$i$$ in $${5 \choose 2}$$ system:
   $$j = {5 \choose 2} - i - 1 = 1$$.
3. Now let's find the combinadic of $$j$$: $$1 = {2 \choose 2} + {0 \choose 1}$$,
   that is, the combinadic corresponding to $$j=1$$ is $$[2, 0]$$.
4. Next we subtract the found comdinadic from the mask $$[4, 4]$$:
   $$[4, 4] - [2, 0] = [2, 4]$$.

8th combination turns out to be $$[2, 4]$$. Eureka!

Conclusion
==========

We have shown that using combinadics one can compute the $$k$$'th combination
among the lexicographically ordered set of combinations of $$n$$-choose-$$r$$,
where $$0 \leq k \lt {n \choose r}$$. Using this method we can partition the
space of all combinations into multiple subsets and generate each of them
individually. For this purpose, I put together a Java library:
[combination](https://github.com/vy/combination). Here is a sample snippet.

    #!java
    public class Main {
    
        public static void main(String[] args) {
            Combination c52 = new Combination(5, 2);
            long l = c52.size();
            println("size(c52): %d", l);
            println("c52", (CombinationIterator) c52.iterator());
            /*
             * size(c52): 10
             * c52:
             * -> [0, 1]
             * -> [0, 2]
             * -> [0, 3]
             * -> [0, 4]
             * -> [1, 2]
             * -> [1, 3]
             * -> [1, 4]
             * -> [2, 3]
             * -> [2, 4]
             * -> [3, 4]
             */

            long m = l / 2;
            CombinationIterator c52_lhs = new CombinationIterator(5, 2, 0, m);
            CombinationIterator c52_rhs = new CombinationIterator(5, 2, m + 1);

            println("c52_lhs", c52_lhs);
            /*
             * c52_lhs:
             * -> [0, 1]
             * -> [0, 2]
             * -> [0, 3]
             * -> [0, 4]
             * -> [1, 2]
             */

            println("c52_rhs", c52_rhs);
            /*
             * c52_rhs:
             * -> [2, 3]
             * -> [2, 4]
             * -> [3, 4]
             * -> [3, 4]
             */

            println("5C2: %d", Combination.choose(5, 2));
            /*
             * 5C2: 10
             */

            int[] c = new int[2];
            Combination.get(5, 2, 3, c);
            println("3rd combination of 5C2: %s", Arrays.toString(c));
            /*
             * 3rd combination of 5C2: [0, 4]
             */

            Combination.get(5, 2, 8, c);
            println("8th combination of 5C2: %s", Arrays.toString(c));
            /*
             * 8th combination of 5C2: [2, 4]
             */
        }

        private static void println(String fmt, Object... args) {
            System.out.println(String.format(fmt, args));
        }

        private static void println(String caption, CombinationIterator ci) {
            println("%s:", caption);
            while (ci.hasNext())
                println("-> %s", Arrays.toString(ci.next()));
        }
    }

References
==========

I started my pursuit with Wikipedia page of [combinatorial number
system](http://en.wikipedia.org/wiki/Combinatorial_number_system). In the
beginning it did not make much sense. Later I found the enlightening 2004 post
[Generating the mth Lexicographical Element of a Mathematical
Combination](http://msdn.microsoft.com/en-us/library/aa289166%28VS.71%29.aspx)
by James McCaffrey, which cleared out the things and made me start to understand
the Wikipedia page.
