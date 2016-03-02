---
kind: article
created_at: 2016-03-02 19:32 CET
title: Optimizing a Data Center Using Integer Programming
modules:
  - mathjax
tags:
  - algorithm
---

[Optimize a Data
Center](https://hashcode.withgoogle.com/2015/tasks/hashcode2015_qualification_task.pdf)
is a **challenging** programming problem presented in the Qualification Round
of the [Hash Code 2015](https://hashcode.withgoogle.com/past_editions.html).
Among 230 teams, *What's in a name?* from [École normale
supérieure](http://www.ens.fr/) ranked first in the qualification, but third
in the final round. By challenging, I mean it is not possible to come up with
a deterministic polynomial-time optimal answer. I am not in a position to
either provide a rigor proof of its complexity or its reduction to a known
NP-hard problem. But in this blog post I will investigate the following
question: Can we provide an optimal solution using [integer
programming](https://en.wikipedia.org/wiki/Integer_programming)? In practice,
that would allow us to come up with an optimal solution to small-sized
problems. Without further ado, let's start with the problem definition.

The Problem
===========

Here, I will present a brief summary of [the actual
problem](https://hashcode.withgoogle.com/2015/tasks/hashcode2015_qualification_task.pdf).
A data center is modeled as **rows​** of **slots** ​in which servers can be
placed. And some of the slots are known to be **unavailable**.

![Data center rows](rows.jpg)

Each **server** is characterized by its **size** and **capacity​**. Size is
the number of consecutive slots occupied by the machine. Capacity is the total
amount of CPU resources of the machine (an integer value).

![Data center servers](servers.jpg)

Servers in a data center are also logically divided into **pools**. ​Each
server belongs to exactly one pool. The capacity of a pool is the sum of the
capacities of the available ​servers in that pool.

The **guaranteed capacity** ​of a pool is the minimum capacity it will have
when at most one data center row goes down. Given a schema of a data center
and a list of available servers, the goal is to assign servers to slots within
the rows​ and to logical pools ​so that the lowest guaranteed capacity​ of all
pools is maximized.

Consider the following data center schema and a list of available servers. For
simplicity, it is assumed that server capacities are equal to server sizes.

![Example problem](example-prob.jpg)

Following layout is a solution to the above given problem. Here different
pools are denoted in distinct colors.

![Example solution](example-soln.jpg)

Preliminaries
=============

Before modeling the IP (Integer Program), I will start with stating the
problem input.

- $$R$$ ​denotes the number of rows in the data center
- $$S$$ denotes the number of slots in each row of the data center
- $$U \leq RS$$ denotes the number of unavailable slots
- $$P$$ denotes the number of pools to be created
- $$M \leq RS$$ denotes the number of servers to be allocated
- $$z_k$$ and $$c_k$$ denote $$k$$th server's respectively size and capacity
- $$r_i$$ and $$s_i$$ denote $$i$$th unavailable slot's respectively row and
  slot indices

While modeling the formulation, I will need to provide constraints to avoid
placing servers to unavailable slots. Rather than doing that, [Atabey
Kaygun](http://kaygun.tumblr.com/) hinted me to represent the data in
**blocks**. That is, instead of $$U$$, $$r_i$$, and $$s_i$$, I will transform
this data into a single lookup table called $$z(i, j)$$ that denotes the size
of the available slots at $$i$$th row and $$j$$th block. For instance,
consider the following layout:

![Example blocks](blocks.jpg)

Here blocks will look as follows:

$$
z(0, 0) = 10 \\
z(1, 0) = 5,\, z(1, 1) = 3 \\
z(2, 0) = 3,\, z(2, 1) = 4,\, z(2, 2) = 1 \\
z(3, 0) = 6
$$

The Integer Programming Model
=============================

For simplicity, I will adopt the following index notation:

- $$i$$ denotes row indices ($$0 \leq i \leq R$$)
- $$j$$ denotes block (not slot!) indices (varies per row)
- $$k$$ denotes server indices ($$0 \leq k \leq M$$)
- $$\ell$$ denotes pool indices ($$0 \leq \ell \leq P$$)

Given that $$z(i, j)$$ denotes the available blocks, the IP model can be
defined as follows:

$$
\begin{align}

\text{maximize}
& \quad
\min_\ell g(\ell)
\quad \text{(minimum of pool guaranteed capacities)} \\

\text{subject to}

& \quad
\sum_\ell p(k, l) \leq 1, \, \forall k
\quad \text{(a server can be assigned to at most 1 pool)} \\

& \quad
\sum_i \sum_j b(i, j, k) \leq 1, \, \forall k
\quad \text{(a server can be assigned to at most 1 block)} \\

& \quad
\sum_k z_k \, b(i, j, k) \leq z(i, j), \, \forall i, j
\quad \text{(total size of servers within a block cannot exceed block's size)} \\

& \quad
p(k, l) \leq \sum_i \sum_j b(i, j, k), \, \forall k, \ell
\quad \text{(a server can be assigned to a pool if the server is assigned to a block)} \\

\text{where}
& \quad
b(i, j, k) =
\begin{cases}
    1       & \quad \text{if block } (i, j) \text{ contains } k\text{th server} \\
    0  & \quad \text{otherwise} \\
  \end{cases} \\

& \quad
p(k, l) =
\begin{cases}
    1       & \quad \text{if } \ell \text{th pool contains } k\text{th server} \\
    0  & \quad \text{otherwise} \\
  \end{cases} \\

& \quad
g(\ell) = \min_i g(\ell, i)
\quad \text{(guaranteed capacity of } \ell \text{th pool)} \\

& \quad
g(\ell, i) = \sum_k c_k \, p(k, \ell) - \sum_k \sum_j c_k \, p(k, \ell) \, b(i, j, k)
\quad \text{(guaranteed capacity of } \ell \text{th pool for } i \text{th row)} \\

\end{align}
$$

Avoiding Minimax Constraint
===========================

The presented IP model contains a minimax objective, which to the best of my
knowledge is not tractable by popular linear programming optimizers, such as
[CPLEX](http://www-01.ibm.com/software/commerce/optimization/cplex-optimizer/)
or [lpsolve](http://lpsolve.sourceforge.net/). But I have a trick in my pocket
to tackle that. Let's assume that we know the optimal objective, say $$g^*$$.
Then we can model the entire IP as follows:

$$
\begin{align}

\text{maximize}
& \quad
1
\quad \text{(a dummy objective)} \\

\text{subject to}

& \quad
\sum_\ell p(k, l) \leq 1, \, \forall k \\

& \quad
\sum_i \sum_j b(i, j, k) \leq 1, \, \forall k \\

& \quad
\sum_k z_k \, b(i, j, k) \leq z(i, j), \, \forall i, j \\

& \quad
p(k, l) \leq \sum_i \sum_j b(i, j, k), \, \forall k, \ell \\

& \quad
g(\ell, i) \geq g^*, \, \forall \ell, i
\quad \text{(guaranteed capacity must be greater than or equal to } g^* \text{)} \\

\end{align}
$$

What this model states is this: I am not interested in the optimization
objective, return me the first found feasible solution. That is, the optimizer
will return us the first $$b(i, j, k)$$ variable set the moment it finds a
feasible solution satisfying $$g(\ell, i) \geq g^*, \, \forall \ell, i$$
constraints.

Now things are getting interesting. If we can find bounds to $$g^*$$, than we
can use these bounds to bisect the optimal $$g^*$$! For the lower bound, we
know that $$g_i = 0 \leq g^*$$. The upper bound is a little bit tricky, but we
can come up with a quite loose bound: $$g_f = \frac{1}{P} \sum_k c_k \gg
g^*$$. (I will not go into details of how to come up with a stricter upper
bound.) So by picking $$g^* \in (g_i, g_f)$$ we can bisect **the optimal
guaranteed capacity**.

Avoiding Non-Linear Constraints
===============================

Note that due to $$p(k, \ell) \, b(i, j, k)$$ multiplication, the following
constraint in the model is non-linear:

$$
g^* \leq g(\ell, i) = \sum_k c_k \, p(k, \ell) - \sum_k \sum_j c_k \, p(k, \ell) \, b(i, j, k), \, \forall \ell, i
$$

Non-linear constraints are as well not allowed by CPLEX and lpsolve. Luckily,
we can [linearize this binary
multiplication](http://www.leandro-coelho.com/linearization-product-variables/)
by introducing a temporary binary variable $$t(i, j, k, \ell) = p(k, \ell) \,
b(i, j, k)$$:

$$
\begin{align}
g(\ell, i) & = \sum_k c_k \, p(k, \ell) - \sum_k \sum_j c_k \, t(i, j, k, \ell), \, \forall \ell, i \\
t(i, j, k, \ell) & \leq p(k, l), \, \forall i, j, k, \ell \\
t(i, j, k, \ell) & \leq b(i, j, k), \, \forall i, j, k, \ell \\
t(i, j, k, \ell) & \geq p(k, l) + b(i, j, k) - 1, \, \forall i, j, k, \ell \\
\end{align}
$$
