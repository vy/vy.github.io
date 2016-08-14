---
kind: article
created_at: 2016-08-12 17:53 CET
title: Programmatically Taking Heap and Thread Dumps in HotSpot
tags:
  - hotspot
  - java
---

While taking heap and thread dumps are one click away using modern JVM
toolset, in many cases the deployment environment access restrictions render
these options unusable. Hence, you might end up exposing these functionalities
in certain ways like an internal REST interface. This implies a new nasty
obstacle: You need to know how to programmatically take heap and thread dumps
in a Java application. Unfortunately, there does not exist a standard
interface to access these functionalities within the VM as of date. But if you
are only concerned about HotSpot, then you are in luck!

Heap Dumps
==========

For heap dumps, once you get your teeth into a
[HotSpotDiagnosticMXBean](https://docs.oracle.com/javase/8/docs/jre/api/management/extension/com/sun/management/HotSpotDiagnosticMXBean.html),
you are safe to go. It already exposes a
[dumpHeap()](https://docs.oracle.com/javase/8/docs/jre/api/management/extension/com/sun/management/HotSpotDiagnosticMXBean.html#dumpHeap-java.lang.String-boolean-)
method ready to be used.

    #!java
    import com.sun.management.HotSpotDiagnosticMXBean;

    import javax.management.MBeanServer;
    import java.io.File;
    import java.io.IOException;
    import java.lang.management.ManagementFactory;

    public enum HotSpotHeapDumps {;

        private static final HotSpotDiagnosticMXBean HOT_SPOT_DIAGNOSTIC_MX_BEAN =
                getHotspotDiagnosticMxBean();

        private static HotSpotDiagnosticMXBean getHotspotDiagnosticMxBean() {
            MBeanServer server = ManagementFactory.getPlatformMBeanServer();
            try {
                return ManagementFactory.newPlatformMXBeanProxy(
                    server, HOT_SPOT_DIAGNOSTIC_MX_BEAN_NAME, HotSpotDiagnosticMXBean.class);
            } catch (IOException error) {
                throw new RuntimeException("failed getting Hotspot Diagnostic MX bean", error);
            }
        }

        public void create(File file, boolean live) throws IOException {
            HOT_SPOT_DIAGNOSTIC_MX_BEAN.dumpHeap(file.getAbsolutePath(), live);
        }

    }

The second argument of `dumpHeap` denotes live objects, that is, objects that
are reachable from others.

Note that many real-world Java applications occupy quite some memory. As a
result of this, created heap dump generally end up consuming significant
amount of disk space. You need to come up with your own custom clean up
mechanism to tackle this problem. (For instance, in a JAX-RS resource, you can
purpose a custom `MessageBodyWriter` to delete the file after writing the
entire file to the output stream.)

Thread Dumps
============

When you think first about thread dumps, they just contain simple plain text
data.

    2016-08-12 18:40:46
    Full thread dump OpenJDK 64-Bit Server VM (25.76-b198 mixed mode):

    "RMI TCP Connection(266)-127.0.0.1" #24884 daemon prio=9 os_prio=0 tid=0x00007f9474010000 nid=0x2cee runnable [0x00007f941571b000]
       java.lang.Thread.State: RUNNABLE
        at java.net.SocketInputStream.socketRead0(Native Method)
        at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
        at java.net.SocketInputStream.read(SocketInputStream.java:170)
        at java.net.SocketInputStream.read(SocketInputStream.java:141)
        at java.io.BufferedInputStream.fill(BufferedInputStream.java:246)
        at java.io.BufferedInputStream.read(BufferedInputStream.java:265)
        - locked <0x00000005c086e8b0> (a java.io.BufferedInputStream)
        at java.io.FilterInputStream.read(FilterInputStream.java:83)
        at sun.rmi.transport.tcp.TCPTransport.handleMessages(TCPTransport.java:550)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler.run0(TCPTransport.java:826)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler.lambda$run$0(TCPTransport.java:683)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$83/628845041.run(Unknown Source)
        at java.security.AccessController.doPrivileged(Native Method)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler.run(TCPTransport.java:682)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1142)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
        at java.lang.Thread.run(Thread.java:745)

       Locked ownable synchronizers:
        - <0x00000005c0489198> (a java.util.concurrent.ThreadPoolExecutor$Worker)

    "JobScheduler FJ pool 0/4" #24883 daemon prio=6 os_prio=0 tid=0x00007f946415d800 nid=0x2ced waiting on condition [0x00007f94093d2000]
       java.lang.Thread.State: TIMED_WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x00000005d8a5f9e0> (a jsr166e.ForkJoinPool)
        at jsr166e.ForkJoinPool.awaitWork(ForkJoinPool.java:1756)
        at jsr166e.ForkJoinPool.scan(ForkJoinPool.java:1694)
        at jsr166e.ForkJoinPool.runWorker(ForkJoinPool.java:1642)
        at jsr166e.ForkJoinWorkerThread.run(ForkJoinWorkerThread.java:108)

       Locked ownable synchronizers:
        - None

Unfortunately, thread dumps do not have a standard syntax. While there are
various ways to produce this output, thread dump analysis software does not
play well with them. For instance, [IBM Thread and Monitor Dump Analyzer for
Java](https://www.ibm.com/developerworks/community/groups/service/html/communityview?communityUuid=2245aa39-fa5c-4475-b891-14c205f7333c)
cannot parse thread dumps created by VisualVM using JMX. At the end of the
day, I always needed to fall back to a HotSpot thread dump.

`tools.jar` shipped with JDKs (>=1.6) provide the magical
`HotSpotVirtualMachine` class containing our saviour `remoteDataDump()`
method. First add the following lines to your `pom.xml`:

    #!xml
    <dependencyManagement>
        <dependencies>

            <dependency>
                <groupId>com.sun</groupId>
                <artifactId>tools</artifactId>
                <version>${java.version}</version>
                <scope>system</scope>
                <systemPath>${tools.jar}</systemPath>
            </dependency>

        </dependencies>
    </dependencyManagement>

    <profiles>

        <!-- tools.jar path for GNU/Linux and Windows -->
        <profile>
            <id>default-tools.jar</id>
            <activation>
                <file>
                    <exists>${java.home}/../lib/tools.jar</exists>
                </file>
            </activation>
            <properties>
                <tools.jar>${java.home}/../lib/tools.jar</tools.jar>
            </properties>
        </profile>

        <!-- tools.jar path for OSX -->
        <profile>
            <id>default-tools.jar-mac</id>
            <activation>
                <file>
                    <exists>${java.home}/../Classes/classes.jar</exists>
                </file>
            </activation>
            <properties>
                <tools.jar>${java.home}/../Classes/classes.jar</tools.jar>
            </properties>
        </profile>

    </profiles>

Then the rest is a matter of accessing to `HotSpotVirtualMachine` class:

    #!java
    import com.google.common.io.ByteStreams;
    import com.sun.management.HotSpotDiagnosticMXBean;
    import com.sun.tools.attach.AttachNotSupportedException;
    import com.sun.tools.attach.VirtualMachine;
    import sun.tools.attach.HotSpotVirtualMachine;

    import java.io.IOException;
    import java.io.InputStream;
    import java.lang.management.ManagementFactory;

    public enum HotSpotThreadDumps {;

        public String create() throws AttachNotSupportedException, IOException {

            // Get the PID of the current JVM process.
            String selfName = ManagementFactory.getRuntimeMXBean().getName();
            String selfPid = selfName.substring(0, selfName.indexOf('@'));

            // Attach to the VM.
            VirtualMachine vm = VirtualMachine.attach(selfPid);
            HotSpotVirtualMachine hotSpotVm = (HotSpotVirtualMachine) vm;

            // Request a thread dump.
            try (InputStream inputStream = hotSpotVm.remoteDataDump()) {
                byte[] bytes = ByteStreams.toByteArray(inputStream);
                return new String(bytes);
            }

        }

    }

You finished writing this code, you clicked on the Run button of the IDE, and
it worked like a charm. This get you so excited that you wanted to add this
functionality to your JEE service! Or better: Turn this into a JAR and pass it
to your client's machine and watch them take their part in the joy of
thread-dump-oriented debugging! And this is what you get in return:

    java.lang.NoClassDefFoundError: com/sun/tools/attach/AttachNotSupportedException

Which indicates that you did not pay attention my words: *`tools.jar` is
shipped with JDKs.* So neither your flashy JEE application server, nor your
client's machine has a JDK, but a JRE. Rings a bell? Yes, you indeed can add
`tools.jar` into the final WAR/JAR of your project:

    #!xml
    <build>
        <plugins>

            <!-- copy tools.jar from JAVA_HOME -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-dependency-plugin</artifactId>
                <executions>
                    <execution>
                        <id>copy-system-dependencies</id>
                        <phase>prepare-package</phase>
                        <goals>
                            <goal>copy-dependencies</goal>
                        </goals>
                        <configuration>
                            <outputDirectory>${project.build.directory}/${project.build.finalName}/WEB-INF/lib</outputDirectory>
                            <includeScope>system</includeScope>
                        </configuration>
                    </execution>
                </executions>
            </plugin>

        </plugins>
    </build>

Note that this approach incorporates a JDK-specific JAR into your application
and assumes that the application will run on a HotSpot VM. But unfortunately
this is the only way that I know of to produce a thread dump that works with
thread dump analysis software. If you don't have such a need and just want a
crude JMX generated thread dump, check out
[JmxSupport.java](https://java.net/projects/visualvm/sources/svn/content/branches/release134/visualvm/jmx/src/com/sun/tools/visualvm/jmx/impl/JmxSupport.java)
shipped with VisualVM.
