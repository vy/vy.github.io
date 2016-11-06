---
kind: article
created_at: 2016-10-04 18:40 CET
title: Notes on "Coders at Work"
tags:
  - programming
---

There is nothing like thinking about work while your are on vacation. And that
was indeed what I did: Reading [Coders at Work: Reflections on the Craft of
Programming](http://www.codersatwork.com/) in a tango-themed Buenos Aires
trip.

I had already met with Peter Seibel in his well-known splendid work:
[Practical Common Lisp](http://www.gigamonkeys.com/book/). He definitely has a
knack for transforming technically challenging problems into a pedagogically
digestable [nootropic](https://en.wikipedia.org/wiki/Nootropic). This uncanny
ability was placidly lurid in Coders at Work as well. Motivated by the mind
provoking exquisite content, I felt an urge to keep a record of its
reflections on me.

On the Content
==============

I totally enjoyed the book and read it cover to cover. Nevertheless, I believe
the following subtleties could have been addressed in a better way.

- A majority of the interviewed *coders* are not actively *coding* any more. I
  find this a little bit contradictory with the title of the book. While the
  content still makes a great deal about the historical progress of
  programming and programmers, I find the detachment of the interviewees from
  the modern computing slightly unexpected.

- Given the back that the book examines the events dating back to more than
  half a century, I sometimes find myself lost in the time context. Additional
  footnotes to enhance these kind of ambiguities could have been useful.

Highligts
=========

Below I collected my personal highligts on certain statements that are shared
by certain interviewees.

- In general, *coders* do not practice software testing extensively. Further,
  I had the impression that that they do not read much programming books
  either. This issue sometimes acclaimed to the lack of necessary set of
  fundamental books at the early stages of their career.

- Among the entire deck, I find Joshua Bloch, Bernie Cosell, and Donald Knuth
  the ones with the most sensible and to-the-earth statements.

- A notable subset of the interviewees dragged into computers not by a
  deliberate decision, but by chosing a yet another career path that was
  available to them. (For instance, Fran Allen got a Fortran instructor
  position in IBM in order to finance her school loans to be able to continue
  her math teacher career pursuit.)

- None believes that reading Knuth's [The Art of Computer
  Programming](https://en.wikipedia.org/wiki/The_Art_of_Computer_Programming)
  is a must read for programmers, nevertheless they acknowledge that it is
  good to have it under your hand for reference.

- Except Knuth himself, nobody practices literate programming. (I am astounded
  to observe how Seibel is biased to ask this non-sense question which
  delivers no practical value at all to every single candidate.)

- Majority agrees that programming is a way more complicated and challenging
  occupation than it once used to be in the past.

- More than half thinks that good writing skills are a big plus (some even
  state necessity) for programming.

- `printf` is the clear winner as the debugging tool of preference among
  interviewees.

Quotes
======

Below you can find some snippets that I find worth mentioning from the book.

Jamie Zawinski
--------------

I wish I would have known this when I was in high school. Could not agree
more.

> **Zawinski:** When you're in high school, everyone tells you, "There's a lot
> of repetitive bullshit and standardized tests; it'll all be better once
> you're in college." And then you get to your first year of college and
> they're like, "Oh, no -- it gets better when you're in grad school." So it's
> just same shit, different day -- I couldn't take it. \[p5\]

His comments on C++, which are shared by many other interviewees throughout
the book:

> **Zawinski:** ... when you're programming C++ no one can ever agree on which
> ten percent of the language is safe to use. \[p20\]

The sad truth about F/OSS:

> **Seibel:** Isn't it exactly this thing -- someone comes along and says, "I
> can't understand this stuff. I'll just rewrite it" -- that leads to the
> endless rewriting you bemoan in open-source development?
>
> **Zawinski:** Yeah. But there's also another aspect of that which is,
> efficiency aside, it's just more fun to write your own code than to figure
> out someone else's. So it is easy to understand why that happens. But the
> whole Linux/GNOME side of things is straddling this line between someone's
> hobby and a product. Is this a research project where we're deciding what
> desktops should look like and we're experimenting? Or are we competing with
> Macintosh? Which is it? Hard to do both. \[p23\]

Brad Fitzpatrick
----------------

His thoughts on finishing a project, which I sadly share as well:

> **Fitzpatrick:** The projects that I never finish ... it's because I did the
> hard part and I learned what I wanted to learn and I never got around to
> doing the boring stuff. \[p20\]

He is also poisoned by LWN, Reddit, etc.

> **Fitzpatrick:** I like working alone but I just bounce all over the place
> when I do. On a plane I'll bring extra laptop batteries and I have a whole
> development environment with local web servers and I'll be in a web browser,
> testing stuff. But I'll still be hitting new tabs, and typing "reddit" or
> "lwn" -- sites I read. Autocomplete and hit Enter, and then -- error
> message. I'll do this multiple times within a minute. Holy fuck! Do I do
> this at work? Am I reading web site this often that I don't even think about
> it? It's scary. I had a friend, who had some iptables rule, that on
> connection to a certain IP address between certain hours of the day would
> redirect to a "You should be working" page. I haven't got around to doing
> that, but I need to do something like it, probably. \[p73\]

Douglas Crockford
-----------------

Why programming is difficult?

> **Crockford:** Part of what makes programming difficult is most of the time
> we're doing stuff we've never done before. \[p110\]

He talks about his preferred way for interviewing job candidates, which is also
shared by other coders in the book.

> **Crockford:** The approach I've taken now is to do a code reading. I invite
> the candidate to bring in a piece of code he's really proud of and walk us
> through it. \[p129\]

Brendan Eich
------------

Nothing noteworthy, you may guess why.

Joshua Bloch
------------

Is Java off in the weeds?

> **Seibel:** ... is Java off in the weeds a little bit? Is it getting more
> complex faster than it's getting better?
>
> **Bloch:** That's a very difficult question. In particular, the Java 5
> changes added far more complexity than we ever intended. I had no
> understanding of just how much complexity generics and, in particular,
> wildcards were going to add to the language. I have to give credit where is
> due -- Graham Hamilton did understand this at the time and I didn't.
>
> The funny things is, he fought against it for years, trying to keep generics
> out of the language. But the notion of variance -- the idea behind wildcards
> -- came into fashion during the years when generics were successfully being
> kept out of Java. If they had gone in earlier, without variance, we might
> have had a simpler, more tractable language today.
>
> That said, there are real benefits to wildcards. There's a fundamental
> impedance mismatch between subtyping and generics, and wildcards go a long
> way towards rectifying the mismatch. But at a significant cost in terms of
> complexity. THere are some people who believe that declaration-site, as
> opposed to use-site, variance is a better solution, but I'm not so sure.
>
> The jury is basically still out on anything that hasn't been tested by a
> huge quantity of programmers under real-world conditions. Often languages
> only succeed in some niche and people say, "Oh, they're great and it's such
> a pity they didn't become the successful language in the world." But often
> there are reasons they didn't. Hopefully some language that does use
> declaration-site variance, like Scala or C# 4.0, will answer this question
> once and for all. \[p191\]

On "obviously no deficiencies" versus "no obvious deficiencies":

> **Bloch:** There's a brilliant quote by Tony Hoare in his Turing Award
> speech about how there are two ways to design a system: "One way is to make
> it so simple that there are *obviously* no deficiencies and the other way is
> to make it is so complicated that there are no *obvious* deficiencies."
>
> The paragraph that follows is equally brilliant, though it isn't as
> well-known: "The first method is far more difficult. It demands the same
> skill, devotion, insight, and even inspiration as the discovery of the
> simple physical laws which underlie the complex phenomena of nature. It also
> requires a willingness to accept objectives which are limited by physical,
> logical, and technological constraints, and to accept a compromise when
> conflicting objectives cannot be met. No committee will ever do this until
> it is too late." \[p197\]

Smart people and programming:

> **Seibel:** Speaking of writing intricate code, I've noticed that people who
> are too smart, in a certain dimension anyway, make the worst code. Because
> they can actually fit the whole thing in their head they can write these
> great reams of spaghetti code.
>
> **Bloch:** I agree with you that people who are both smart enough to cope
> with enormous complexity and lack empathy with the rest of use may fail prey
> to that. They think, "I can understand this and I can use it, so it has to
> be good." \[p202\]
>
> ...
>
> There's this problem, which is, programming is so much of an intellectual
> meritocracy and often these people are the smartest people in the
> organization; therefore they figure they should be allowed to make all the
> decisions. But merely the fact that they're the smartest people in the
> organization doesn't mean they should be making all the decisions, because
> intelligence is not a scalar quantity; it's a vector quantity. And if you
> lack empathy or emotional intelligence, then you shouldn't be designing APIs
> or GUIs or languages. \[p203\]

Joe Armstrong
-------------

On paralyses of choice:

> **Armstrong:** The funny thing is, thinking back, I don't think all these
> modern gizmos actually make you any more productive. Hierarchical file
> systems -- how do they make you more productive? Most of software
> development goes on in your head anyway. I think having worked with that
> simpler system imposes a kind of disciplined way of thinking. If you haven't
> got a directory system and you have to put all the files in one directory,
> you have to be fairly disciplined. If you haven't got a revision control
> system, you have to be fairly disciplined. Given that you apply that
> discipline to what you're doing it doesn't seem to me to be any better to
> have hierarchical file systems and revision control. They don't solve the
> fundamental problem of solving your problem. They probably make it easier
> for groups of people to work together. For individuals I don't see any
> difference.
>
> Also, I think today we're kind of overburdened by choice. I mean, I just had
> Fortran. I don't think we even had shell scripts. We just had batch files so
> you could run things, a compiler, and Fortran. And assembler possibly, if
> you really needed it. So there wasn't this agony of choice. Being a young
> programmer today must be awful -- you can choose 20 different programming
> languages, dozens of framework and operating systemsand you're paralyzed by
> choice. There was no paralysis of choice then. You just start doing it
> because the decision as to which language and things is just made -- there's
> no thinking about what you should do, you just go and do it. \[p210\]

Simon Peyton Jones
------------------

Testing an API in Microsoft:

> **Peyton Jones:** Well, they also do some interesting work on testing APIs.
> Steven Clarke and his colleagues at Redmond have made systematic attempts to
> watch programmers, given a new API, talk through what they're trying to do.
> And they get the people who designed the API to sit behind a glass screen
> and watch them.
>
> And the guys sitting there behind the glass screen say, "No, no, don't do
> that! That's not the right way!" But it's soundproof. That turns out often
> to be very instructive. They go and change their API. \[p253\]

Peter Norvig
------------

On the traditional master and apprentice approach:

> **Norvig:** But I think part of the reasons why you had master and
> apprentice is because the materials were rarer. When you were doing
> goldsmithing, there's only so much gold. Or when the surgeon's operating,
> there's only one heart, and so you want the best person on that and you want
> the other guys just helping. With coding, it's not like that. You've got
> plenty of terminals. You've got plenty of keyboards. You don't have to
> ration it. \[p295\]

Why programming is not an art, but a craft:

> **Seibel:** As a programmer, do you consider yourself a scientist, an
> engineer, an artist, or a craftsman?
>
> **Norvig:** Well, I know when you compare the various titles of books and so
> on, I always thought the "craft" was the right answer. So I thought art was
> a little pretentious because the purpose of art is to be beautiful or to
> have an emotional contact or emotional impact, and I don't feel like that's
> anything that I try to do. Certainly I want programs to be pretty in some
> ways, and sometimes I feel like I spend too much time doing that. I've been
> in a position where I've had the luxury to say, "Gee, I have time to go back
> and pretty this up a little bit." And places where I've been able to write
> for a publication, you spend more time doing that than you would if it was
> just for your own professional growth.
>
> But I don't think of that as art. I think *craft* is really the right word
> for it. You can make a chair, and it's good looking, but it's mostly
> functional -- it's a chair. \[p319\]

Guy Steele
----------

On the difficulty of getting a program right:

> **Steele:** I'll give you another example -- suppose I were to tell my smart
> computer, "OK, I've got this address book and I want the addresses to always
> be in sorted order," and it responds by throwing away everything but the
> first entry. Now the address book is sorted. But that's not what you wanted.
> It turns out that just specifying something as simple as "a list is in
> sorted order and I haven't lost any of the data and nothing has been
> duplicated" is actually a fairly tricky specification to write. \[p361\]

Dan Ingalls
-----------

Was a nice read, though I could not find anything particularly interesting
worth sharing. Nevertheless, along the lines Seibel says something that I have
never heard of:

> **Seibel:** Alan Kay has said that both Lisp and Smalltalk have the problem
> that they're so good they eat their children. If you had known Lisp, then
> Smalltalk would have been the first eaten child. \[p378\]

L Peter Deutsch
---------------

On getting data structures right:

> **Deutsch:** ... if you get the data structures and their invariants right,
> most of the code will just kind of write itself. \[p420\]

Conceptualization of software and memory pointers:

> **Deutsch:** ... I don't look around and see anything that looks like an
> address or a pointer. We have objects; we don't have these weird things that
> computer scientists misname "objects."
>
> **Seibel:** To say nothing of the scale. Two to the 64th of anything is a
> lot, and things happening billions of times a second is fast.
>
> **Deutsch:** But that doesn't bother us here in the real world. You know
> Avogadro's number, right? Ten to the 23rd? So, we're looking here around at
> a world that has incredible numbers of little things all clumped together
> and happening at the same time. It doesn't bother us because the world is
> such that you don't have to understand this table at a subatomic level. The
> physical properties of matter are such that 99.9 percent of the time you can
> understand it in aggregate. And everything you have to know about it, you
> can understand from dealing with it in aggregate. To a great extent, that is
> not true in the world of software.
>
> People keep trying to do modularization structures for software. And the
> state of that art has been improving over time, but it's still, in my
> opinion, very far away from the ease with which we look around and see
> things that have, whatever it is, 10 to the 23rd atoms in them, and it
> doesn't even faze us.
>
> Software is a discipline of detail, and that is a deep, horrendous
> fundamental problem with software. Until we understand how to conceptualize
> and organize software in a way that we don't have to think about how every
> little piece interacts with every other piece, things are not going to get a
> whole lot better. And we're very far from being there. \[p424\]

Ken Thompson
------------

On teaching:

> **Thompson:** ... I love the teaching: the hard work of a first class, the
> fun of the second class. Then the misery of the third. \[p455\]

What I am supposed to do and what I am actually doing:

> **Thompson:** We were supposed to be doing basic research but there was some
> basic research we should be doing and some basic research we shouldn't be
> doing. And just coming out of the ashes of MULTICS, operating systems was
> one of those basic research things we shouldn't be doing. Because we tried
> it, it didn't work, it was a huge failure, it was expensive; let's drop it.
> So I kind of expected that for what I was doing I was going to eventually
> get fired. I didn't. \[p458\]

Code rots:

> **Thompson:** Code by itself almost rots and it's gotta be rewritten. Even
> when nothing has changed, for some reason it rots. \[p460\]

10 percent of the work:

> **Thompson:** NELIAC was a system-programming version of Algol 58.
>
> Seibel: Was Bliss also from that era?
>
> **Thompson:** Bliss I think was after. And their emphasis was trying to
> compile well. I think it was pretty clear from the beginning that you
> shouldn't kill yourself compiling well. You should do well but not really
> good. And the reason is that in the time it takes you to go from well to
> really good, Moore's law has already surpassed you. You can pick up 10
> percent but while you're picking up that 10 percent, computers have gotten
> twice as fast and maybe with some other stuff that matters more for
> optimization, like caches. I think it's largely a waste of time to do really
> well. It's really hard; you generate as many bugs as you fix. You should
> stop, not take that extra 100 percent of time to do 10 percent of the work.
> \[p462\]

Writing an OS to test a file system:

> **Seibel:** So you basically wrote an OS so you'd have a better environment
> to test your file system.
>
> **Thompson:** Yes. Halfway through there that I realized it was a real time-
> sharing system. I was writing the shell to drive the file system. And then I
> was writing a couple other programs that drove the file system. And right
> about there I said, "All I need is an editor and I've got an operating
> system." \[p465\]

Economics of deciding on introducing a bag:

> **Thompson:** Certainly every time I've written one of these non-compare
> subroutine calls, strcpy and stuff like that, I know that I'm writing a bug.
> And I somehow take the economic decision of whether the bug is worth the
> extra arguments. \[p468\]

On testing:

> **Thompson:** ... Mostly just
> regression tests.
>
> **Seibel:** By things that are harder to test, you mean things like device
> drivers or networking protocols?
>
> **Thompson:** Well, they're run all the time when you're actually running an
> operating system.
>
> **Seibel:** So you figure you'll shake the bugs out that way?
>
> **Thompson:** Oh, absolutely. I mean, what's better as a test of an
> operating system than people beating on it? \[p469\]

Code at Google:

> **Thompson:** I guess way more than 50 percent of the code is the what-if
> kind. \[p473\]

On literate programming:

> **Seibel:** When I interviewed him, Knuth said the key to technical writing
> is to say everything twice in complementary ways. So I think he sees that as
> a feature of literate programming, not a bug.
>
> **Thompson:** Well if you have two ways, one of them is real: what the
> machine executes. \[p477\]

Fran Allen
----------

What makes a program beautiful?

> **Allen:** That it is a simple straightforward solution to a problem; that
> has some intrinsic structure and obviousness about it that isn't obvious
> from the problem itself. \[p489\]

Bernie Cosell
-------------

Should we teach Knuth to students?

> **Cosell:** I would not teach students Knuth per se for two reasons. First,
> it's got all this mathematical stuff where he's not just trying to present
> the algorithms but to derive whether they're good or bad. I'm not sure you
> need that. I understand a little bit of it and I'm not sure I need any of
> it. But getting a feel for what's fast and what's slow and when, that's an
> important thing to do even if you don't know how much faster or how much
> slower.
>
> The second problem is once students get sensitive to that, they get too
> clever by half. They start optimizing little parts of the program because,
> "This is the ideal place to do an AB unbalanced 2-3 double reverse backward
> pointer cube thing and I always wanted to write one of those." So they spend
> a week or two tuning an obscure part of a program that doesn't need
> anything, which is now more complicated and didn't make the program any
> better. So they need a tempered understanding that there are all these
> algorithms, how they work, and how to apply them. It's really more of a case
> of how to pick the right one for the job you're trying to do as opposed to
> knowing that this one is an order n-cubed plus three and this one is just
> order n-squared times four. \[p527\]

Writing programs and learning how to program:

> **Cosell:** The binary bits are what computers want and the text file is for
> me. I would get people -- bright, really good people, right out of college,
> tops of their classes -- on one of my projects. And they would know all
> about programming and I would give them some piece of the project to work
> on. And we would start crossing swords at our project-review meetings. They
> would say, "Why are you complaining about the fact that I have my global
> variables here, that I'm not doing this, that you don't like the way the
> subroutines are laid out? The program works."
>
> They'd be stunned when I tell them, "I don't care that the program works.
> The fact that you're working here at all means that I expect you to be able
> to write programs that work. Writing programs that work is a skilled craft
> and you're good at it. Now, you have to learn how to program." \[p543\]

Convictions:

> **Cosell:** I had two convictions, which actually served me well: that
> programs ought to make sense and there are very, very few inherently hard
> problems. \[p549\]

How long is it going to take you to put this change in?

> **Cosell:** So when they ask, "How long is it going to take you to put this
> change in?" you have three answers. The first is the absolute shortest way,
> changing the one line of code. The second answer is how long it would be
> using my simple rule of rewriting the subroutine as if you were not going to
> make that mistake. Then the third answer is how long if you fix that bug if
> you were actually writing this subroutine in the better version of the
> program. \[p550\]

Artistry in programming:

> **Cosell:** Part of what I call the artistry of the computer program is how
> easy it is for future people to be able to change it without breaking it.
> \[p555\]

Difficulty of programming and C:

> **Cosell:** ... programmers just can't be careful enough. They don't see all
> the places. And C makes too many places. Too scary for me, and I guess it's
> fair to say I've programmed C only about five years less than Ken has. We're
> not in the same league, but I have a long track record with C and know how
> difficult it is and I think C is a big part of the problem. \[p559\]

75 million run-of-the-mill programmers and Java:

> **Cosell:** When I first messed with Java -- this was when it was little
> baby language, of course -- I said, "Oh, this is just another one of those
> languages to help not-so-good programmers go down the straight and narrow by
> restricting what they can do." But maybe we've come to a point where that's
> the right thing. Maybe the world has gotten so dangerous you can't have a
> good, flexible language that one percent or two percent of the programmers
> will use to make great art because the world is now populated with 75
> million run-of-the-mill programmers building these incredibly complicated
> applications and they need more help than that. So maybe Java's the right
> thing. I don't know. \[p560\]

Not-so-good programmers and C:

> **Cosell:** I don't want to say that C has outlived its usefulness, but I
> think it was used by too many good programmers so that now not-good-enough
> programmers are using it to build applications and the bottom line is
> they're not good enough and they can't. Maybe C is the perfect language for
> really good systems programmers, but unfortunately not-so-good systems and
> applications programmers are using it and they shouldn't be. \[p560\]

Donald Knuth
------------

Teaching a class, writing a book, and programming:

> **Knuth:** I could teach classes full-time and write a book full-time but
> software required so much attention to detail. It filled that much of my
> brain to the exclusion of other stuff. So it gave me a special admiration
> for people who do large software projects -- I would never have guessed it
> without having been faced with that myself. \[p572\]

Why isn't everybody a super programmer and super writer?

> **Knuth:** Now, why hasn't this spread over the whole world and why isn't
> everybody doing it? I'm not sure who it was who hit the nail on the head --
> I think it was Jon Bentley. Simplified it is like this: only two percent of
> the world's population is born to be super programmers. And only two percent
> of the population is born to be super writers. And Knuth is expecting
> everybody to be both. \[p574\]

Use of pointers in C:

> **Knuth:** To me one of the most important revolutions in programming
> languages was the use of pointers in the C language. When you have
> nontrivial data structures, you often need one part of the structure to
> point to another part, and people played around with different ways to put
> that into a higher- level language. Tony Hoare, for example, had a pretty
> nice clean system but the thing that the C language added -- which at first
> I thought was a big mistake and then it turned out I loved it -- was that
> when x is a pointer and then you say, x + 1 , that doesn't mean one more
> byte after x but it means one more node after x , depending on what x points
> to: if it points to a big node, x
> + 1 jumps by a large amount; if x points to a small thing, x + 1 just moves
> a little. That, to me, is one of the most amazing improvements in notation.
> \[p585\]

I did not know about Knuth's *change files*. But it seemed like an
inconvenient overkill:

> **Knuth:** I had written TeX and Metafont and people started asking for it.
> And they had 200 or 300 combinations of programming language and operating
> system and computer, so I wanted to make it easy to adapt my code to
> anybody's system. So we came up with the solution that I would write a
> master program that worked at Stanford and then there was this add-on called
> a change file which could customize it to anybody else's machine.
> 
> A change file is a very simple thing. It consists of a bunch of little blobs
> of changes. Each change starts out with a few lines of code. You match until
> you find the first line in the master file that agrees with the first line
> of your change. When you get to the end of the part of the change that was
> supposed to match the master file, then comes the part which says, "Replace
> that by these lines instead." \[p586\]
> 
> The extreme example of this was when TeX was adapted to Unicode. They had a
> change file maybe 10 times as long as the master program. In other words,
> they changed from an 8-bit program to a 16-bit program but instead of going
> through and redoing my master program, they were so into change files that
> they just wrote their whole draft of what they called Omega as change files,
> as a million lines of change files to TeX's 20,000 lines of code or
> something. So that's the extreme. \[p587\]

Is programming fun any more?

> **Knuth:** So there's that change and then there's the change that I'm
> really worried about: that the way a lot of programming goes today isn't any
> fun because it's just plugging in magic incantations -- combine somebody
> else's software and start it up. It doesn't have much creativity. I'm
> worried that it's becoming too boring because you don't have a chance to do
> anything much new. \[p594\]

Code reading:

> **Knuth:** ... don't only read the people who code like you. \[p601\]
