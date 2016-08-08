---
kind: article
created_at: 2015-09-09 18:56 CEST
title: Enforcing a Locking Context on Variables in Scala
tags:
  - concurrency
  - scala
---

Accessing variables that need synchronization necessitates book keeping by
programmers. Since it is not something explicitly enforced by the language
mechanics, programmer needs to make sure that such variables are not accessed
out of a synchronization scope. Consider the following innocent user store:

    #!scala
    case class User(id: Int, name: String, manager: Boolean)
    
    // Use with caution! Can be accessed by multiple threads.
    private var users: Map[Int, User] = Map[Int, User]()

The safest approach would be encapsulating every access to `users` variables
in a `synchronized` block:

    #!scala
    def save(user: User): Unit = synchronized { users += user.id -> user }
    
    def findById(id: Int): Option[User] = synchronized { users.get(id) }

You can even go further and use a `ReadWriteLock` to boost read-only queries:

    #!scala
    private val lock: ReadWriteLock = new ReentrantReadWriteLock()
    
    def save(user: User): Unit = {
      lock.writeLock().lock()
      try { users += user.id -> user }
      finally { lock.writeLock().unlock() }
    }
    
    def findById(id: Int): Option[User] = {
      lock.readLock().lock()
      try { users.get(id) }
      finally { lock.readLock().unlock() }
    }

Now you think you are safe. And it does not take a couple of VCS commits for
somebody (most probably you) to mess up the entire synchronization scheme:

    #!scala
    // Violating thread-safety on `users`.
    override def toString: String = s"There are ${users.size} user(s)."

Oops! There can arise a lot more complicated subtle bugs. Shit can even hit
the fan when you introduce multiple variables or make nested calls, that is,
functions calling functions calling functions which are accessing `users`. It
is obvious that you are doomed. Now good luck with your chasing the
[Heisenbug](https://en.wikipedia.org/wiki/Heisenbug) journey!

Then it occured to me, can't we make the compiler enforce a certain lock
context while accessing to a particular set of variables? What if compiler
would not allow you to read `users` if your thread did not already acquire
`lock.readLock()`? Or similarly would not allow you to mutate it if you did
not already acquire `lock.writeLock()`? Here is the solution that I came up
with to these questions:

    #!scala
    import java.util.concurrent.locks.Lock
    import java.util.concurrent.locks.ReentrantReadWriteLock
    
    trait SynchronizedAccess {
    
      import SynchronizedAccess._
    
      protected val instanceLock: ReentrantReadWriteLock =
        new ReentrantReadWriteLock()
    
      protected val instanceReadLock: ReadLock =
        new ReadLock(instanceLock.readLock())
    
      protected val instanceReadWriteLock: ReadWriteLock =
        new ReadWriteLock(instanceLock.readLock(), instanceLock.writeLock())
    
      protected case class Synchronized[T](private var value: T) {
    
        def apply()(implicit readLock: ReadLock): T = {
          validateLock(readLock, instanceReadLock, instanceReadWriteLock)
          value
        }
    
        def update(newValue: T)(implicit readWriteLock: ReadWriteLock): Unit = {
          validateLock(readWriteLock, instanceReadWriteLock)
          value = newValue
        }
    
        private def validateLock(lock: TypedLock, allowedLocks: TypedLock*): Unit = {
          require(allowedLocks.contains(lock), "cannot be accessed from another synchronization scope")
          require(lock.tryLock(), "cannot be accessed out of a synchronization scope")
          lock.unlock()
        }
    
      }
    
      protected def synchronizeRead[T](body: ReadLock => T): T =
        synchronizeOperation(instanceReadLock)(body)
    
      protected def synchronizeReadWrite[T](body: ReadWriteLock => T): T =
        synchronizeOperation(instanceReadWriteLock)(body)
    
      protected def synchronizeOperation[T, L <: TypedLock](lock: L)(body: L => T): T = {
        lock.lock()
        try { body(lock) }
        finally { lock.unlock() }
      }
    
    }
    
    object SynchronizedAccess {
    
      sealed trait TypedLock {
    
        protected val instance: Lock
    
        def lock(): Unit = instance.lock()
    
        def unlock(): Unit = instance.unlock()
    
        def tryLock(): Boolean = instance.tryLock()
    
      }
    
      sealed class ReadLock(readLock: ReentrantReadWriteLock.ReadLock) extends TypedLock {
    
        override protected val instance: Lock = readLock
    
      }
    
      sealed class ReadWriteLock
      (readLock: ReentrantReadWriteLock.ReadLock,
       writeLock: ReentrantReadWriteLock.WriteLock)
        extends ReadLock(readLock) {
    
        override protected val instance: Lock = writeLock
    
      }
    
    }

Looks complicated? See me while I dance with it:

    #!scala
    class UserService extends SynchronizedAccess {
    
      private val users: Synchronized[Map[Int, User]] = Synchronized(Map[Int, User]())
    
      private val managerCount: Synchronized[Int] = Synchronized(0)
    
      def save(user: User): Unit =
        // Note that `users` and `managerCount` variables will be updated
        // atomically while the rest waits for the `ReadWrite` lock.
        synchronizeReadWrite { implicit lock =>
          users() += user.id -> user
          if (user.manager)
            managerCount() += 1
        }
    
      def findById(id: Int): Option[User] =
        synchronizeRead { implicit lock =>
          users().get(id)
        }
    
      def findAllNames(): Seq[String] =
        synchronizeRead { implicit lock =>
          findAll.map(_.name)
        }
    
      // Note that findAll() requires a `ReadLock` context in order to access `users`.
      private def findAll(implicit lock: ReadLock): Seq[User] =
        users().values.toSeq
    
      def findManagerCount(): Int = 
        synchronizeRead { implicit lock =>
          managerCount()
        }
    
    }

In a nutshell, what did `SynchronizedAccess` trait really bring us? *It
enforces a **typed** and **unique** locking context on the variables of type
`Synchronized[T]`.* It is *typed* because read and read-write operations are
distinct from each other in the function decleration via implicit `ReadLock`
and `ReadWriteLock` parameters. It is *unique* because `Synchronized`
variables can only be accessed by the instance lock inherited from
`SynchronizedAccess` trait.

Here is your free lunch. [Eet smaaklijk!](https://translate.google.com/#nl/en/eet%20smakelijk)

Common Confusions
=================

I sadly observed that there are some common confusions about `Synchronized[T]`
type. Let me try to address them here.

- **I could have used a `ConcurrentMap` instead!** `Map` usage in the examples
  above is just there for demonstration purposes. It does not have to be a
  collection at all. If you have just one variable and it is a collection,
  then going with a synchronized/concurrent implementation is totally fine.

- **I could have used a `ConcurrentMap` and an `AtomicInteger` instead!** No,
  you cannot. Then you would totally spoil the *atomic* read-write operations.
  You will still need a *transaction*-like mechanism ala in SQL.
