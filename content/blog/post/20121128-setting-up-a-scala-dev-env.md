---
kind: article
created_at: 2012-11-28 06:46 EET
title: Scala Development Environment with Intellij IDEA and SBT
tags:
  - intellij
  - java
  - sbt
  - scala
---

Resisting against the [Functional Programming Principles in Scala](https://class.coursera.org/progfun-2012-001/) buzz was meaningless. After all, this or that way I know I would be repeating those steps on my own regardless of the presence of such a lecture. To warm up, I looked around for an appropriate development environment for Scala. The last time (~2 years ago) I repeated this same step ended up with a desperate search. Fortunately, reading dozens of blog posts, forum/mailing-list threads, GitHub README's, repeating try-and-fail procedures leaded me to a working setup. To mitigate the friction at least to an extent for new comers, I put up this blog post to make a list of steps in order to setup a working Scala development environment on top of [IntelliJ IDEA](http://www.jetbrains.com/idea) with [SBT](http://www.scala-sbt.org/) integration.

Is there a Scala plugin available for IDEA?
===========================================

Good news, yes. [It](http://confluence.jetbrains.net/display/SCA/Scala+Plugin+for+IntelliJ+IDEA) is under active development, works way better than its alternatives, has a responsive maintainer and an active [community](http://devnet.jetbrains.net/community/idea/scala?view=discussions). Plugin lets you create Scala projects, compile/run/debug Scala source files, scripts, and worksheets. Navigation, refactoring, tab-completion, code snippets are included as well. (Note that it is *strongly* advised to use an [EAP](http://confluence.jetbrains.net/display/IDEADEV/EAP) version for a smooth experience.)

Is there a quick start guide for IDEA Scala plugin?
===================================================

Yes, see [Getting Started with IntelliJ IDEA Scala Plugin](http://confluence.jetbrains.net/display/SCA/Getting+Started+with+IntelliJ+IDEA+Scala+Plugin).

How do I manage project dependencies?
=====================================

While one can setup a Maven/Ivy/Ant configuration for a Scala project, [SBT](http://www.scala-sbt.org/) is known to be the de-facto tool for build management throughout the Scala community. (Otherwise, you will need to set explicit scala-compiler and scala-library dependencies in XML mazes.) Fortunately, there is an [SBT plugin](http://plugins.intellij.net/plugin?pr=idea&amp;pluginId=5007) for IDEA. It offers a console where SBT commands can be entered interactively, and a *Before Launch* task to delegate project compilation to SBT, as an alternative to the built in IntelliJ Make.

Is there a quick start guide for SBT?
=====================================

Yes, see [Hello, World](http://www.scala-sbt.org/release/docs/Getting-Started/Hello.html) in [SBT documentation](http://www.scala-sbt.org/release/docs/index.html).

How can I integrate libraries installed by SBT to IDEA?
=======================================================

At its core, SBT uses [Apache Ivy](http://ant.apache.org/ivy/), which has its own nasty ways of dealing with downloaded JARs under `~/.ivy2`. Instead of manually defining IDEA module dependencies for each JAR a project uses, lucky for us, there exists an SBT plugin for this purpose: [sbt-idea](https://github.com/mpeltonen/sbt-idea). Basically, sbt-idea enhances SBT with a new task, called *gen-idea*, which creates IDEA project files with necessary module dependencies induced by SBT. That is,

1. Add your dependencies to your SBT configuration,
2. Call `sbt update` to download/update project dependencies,
3. Call `sbt gen-idea` to create IDEA project files,
4. Open created project from IDEA.

What are the IDEA modules created by sbt-idea?
==============================================

In addition to below directories, SBT dependencies are added to the IDEA module configuration.

- **Source Folders:** `src/main/{scala,java,resources}`
- **Test Source Folders:** `src/test/{scala,java,resources}`

What about testing?
===================

SBT supports a couple of testing frameworks, e.g., [specs2](http://etorreborre.github.com/specs2/), [ScalaCheck](http://code.google.com/p/scalacheck/), and
[ScalaTest](http://www.artima.com/scalatest/). See [Testing](http://www.scala-sbt.org/release/docs/Detailed-Topics/Testing.html) section of the SBT documentation for a detailed discussion.

What about my `.gitignore`?
=========================

Here you go.

    /.idea
    /.idea_modules
    target/

I read enough, gimme the code!
==============================

Create a project directory.

    #!bash
    $ export PROJECT_DIR=~/scala/ScalaHelloWorld
    $ mkdir $PROJECT_DIR

Create `$PROJECT_DIR/build.sbt` as follows. (In this example, I used ScalaTest framework.)

    #!scala
    name := "ScalaHelloWorld"
     
    version := "0.0.1"
     
    scalaVersion := "2.9.2"
     
    libraryDependencies += "org.scalatest" %% "scalatest" % "1.8" % "test"

Create `$PROJECT_DIR/project` directory and add below lines to `$PROJECT_DIR/project/plugins.sbt` to add sbt-idea plugin.

    #!scala
    resolvers += "Sonatype snapshots" at "http://oss.sonatype.org/content/repositories/snapshots/"
     
    addSbtPlugin("com.github.mpeltonen" % "sbt-idea" % "1.2.0-SNAPSHOT")

Run `sbt` in `$PROJECT_DIR` and execute `gen-idea` task.

    #!bash
    $ sbt
    [info] Loading project definition from /home/vy/scala/ScalaHelloWorld/project
    [info] Updating {file:/home/vy/scala/ScalaHelloWorld/project/}default-70d248...
    [info] Resolving org.scala-sbt#precompiled-2_10_0-m7;0.12.1 ...
    [info] Done updating.
    [info] Set current project to ScalaHelloWorld (in build file:/home/vy/scala/ScalaHelloWorld/)
    > gen-idea
    [info] Trying to create an Idea module ScalaHelloWorld
    [info] Updating {file:/home/vy/scala/ScalaHelloWorld/}default-3005c4...
    [info] Resolving org.scalatest#scalatest_2.9.2;1.8 ...
    [info] Done updating.
    [info] Resolving org.scalatest#scalatest_2.9.2;1.8 ...
    [info] Excluding folder target
    [info] Created /home/vy/scala/ScalaHelloWorld/.idea/IdeaProject.iml
    [info] Created /home/vy/scala/ScalaHelloWorld/.idea
    [info] Excluding folder /home/vy/scala/ScalaHelloWorld/target
    [info] Created /home/vy/scala/ScalaHelloWorld/.idea_modules/ScalaHelloWorld.iml
    [info] Created /home/vy/scala/ScalaHelloWorld/.idea_modules/ScalaHelloWorld-build.iml
    >

In `src/main/scala/Main.scala`, create a `main()` stub with a testable function in it.

    #!scala
    object Main {
      def main(args: Array[String]) {
        println("Hello, World!")
        println("# of arguments: %d" format count(args))
      }
    
      def count[T](it: Iterable[T]): Int = it.size
    }

In `src/test/scala/MainSuite.scala`, create a sample test suite.

    #!scala
    import org.scalatest.FunSuite
    
    class MainSuite extends FunSuite {
      test("counting an empty collection") {
        assert(Main.count(Array[Int]()) == 0)
        assert(Main.count(Map()) == 0)
        assert(Main.count(Set()) == 0)
      }
    
      test("counting a non-empty collection") {
        assert(Main.count(Array(1)) == 1)
        assert(Main.count(Map(1 -> 1)) == 1)
        assert(Main.count(Set(1)) == 1)
      }
    }

Enjoy the rest by either creating your own IDEA run configurations, or manually running tasks within the SBT console. (As a final note, while creating IDEA run configurations, you can use SBT *Before Launch* task provided by IDEA SBT plugin.)
