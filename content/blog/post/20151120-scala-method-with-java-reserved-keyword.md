---
kind: article
created_at: 2015-11-20 07:00 CEST
title: Calling a Scala Method with a Java Reserved Keyword
tags:
  - java
  - scala
---

At work, there are a couple of JAX-RS microservices I develop and maintain.
Fortunately, all of these services and their consumers are written in Scala.
Up until now, I have never needed to access the service APIs from Java. But
some other team recently needed to do that! And that was where shit hit the
fan. Consider the following `ScalaApi` class:

	#!scala
	class ScalaApi {

	  def default: String = "test"

	}

Did you notice something wrong with the class methods? While it is perfectly
legitimate to use `default` as a keyword in the JVM byte code, it is not
allowed by the [Java Language Specification
3.9](http://docs.oracle.com/javase/specs/jls/se8/html/jls-3.html#jls-3.9).
(Another slightly related discussion: [Reserved words as variable or method
names](http://stackoverflow.com/questions/423994/reserved-words-as-variable-or-method-names).)
Hence, you cannot access it via a simple `new ScalaApi().default()` call in
Java. To the best of my knowledge, your only safe bet becomes using Java's
Reflection API:

	#!java
	import java.lang.reflect.Method;

	public class Consumer {

	    public static void main(String[] args) {
	        ScalaApi scalaApi = new ScalaApi();
	        String scalaApiDefault = scalaApiDefault(scalaApi);
	        System.out.println("ScalaApi#default: " + scalaApiDefault);
	    }

	    private static String scalaApiDefault(ScalaApi scalaApi) {
	        try {
	            Method method = scalaApi.getClass().getDeclaredMethod("default");
	            return (String) method.invoke(scalaApi);
	        } catch (NoSuchMethodException | InvocationTargetException | IllegalAccessException cause) {
	            throw new RuntimeException(cause);
	        }
	    }

	}

This issue raised the following question: *Where did I make a mistake?* I
believe, it is not possible to come up with a universally legitimate API
targeting all available languages that compile to JVM byte code. I think that
is one of the reasons why programming languages provide constructs to use
reserved keywords in the source code, such as ``reserved`` in Scala or
`@reserved` in C#, etc.
