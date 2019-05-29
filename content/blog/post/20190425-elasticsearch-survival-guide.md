---
kind: article
created_at: 2019-04-25 11:44 CET
title: Elasticsearch Survival Guide for Developers
tags:
  - elasticsearch
  - java
---

For some months, I have been writing down to my notebook Elasticsearch best
practices that I wish I would have known when I first started developing
applications running against Elasticsearch. Even though the following collection
tries to communicate certain ideas in Java, I believe almost each of such cases
apply to every other programming language with almost no or minor changes. I
tried to avoid repeating content that has already been covered in tutorials and
the Elasticsearch documentation. The listed principles are all derived from my
personal point of view, I strived to share only the ones that I can justify with
either facts or experience.

# Table of Contents

- [Mapping](#mapping)
  - [Avoid `nested` fields](#nested-fields) 
  - [Have a strict mapping](#strict-mapping)
  - [Don't analyze fields of type `string` unless necessary](#analyze)
- [Setting](#setting)
  - [Unlearn every hack for tuning merges](#tuning-merges)
  - [Pay attention to JVM memory settings](#memory)
- [Querying](#querying)
  - [Compare-and-swap over `_version` field is poor man's transactions](#cas)
  - [Try splitting complex queries](#splitting-queries)
  - [Know your numeric types](#numeric-types)
  - [Don't use Elasticsearch Transport/Node client in your Java application (and always use JSON over HTTP)](#transport-client)
  - [Use the official Elasticsearch REST client in your Java application](#rest-client)
  - [Don't use Elasticsearch query models to generate cache keys](#cache-keys)
  - [Don't use HTTP caching for caching Elasticsearch responses](#http-caching)
  - [Use sliced scrolls sorted on `_doc`](#sliced-scrolls)
  - [Prefer `GET /index/type/{id}` over `POST /index/_search` for single document retrieval](#get-by-id)
  - [Use `size: 0` and `includes`/`excludes` wisely](#size0-includes-excludes)
  - [Implement proper backpressure while querying](#backpressure)
  - [Provide explicit timeouts in queries](#explicit-timeouts)
  - [Don't block the Elasticsearch client I/O threads (and know your threads)](#blocking-io-threads)
  - [Don't write Elasticsearch queries with JSON templates injecting variables](#json-templates)
  - [Prefer your own JSON serializer over the one provided by Elasticsearch clients](#json-serializer)
- [Strategy](#strategy)
  - [Always (try to) stick to the latest JVM and Elasticsearch versions](#latest-version)
  - [Use Elasticsearch complete and partial snapshots for backups](#snapshots)
  - [Have a continuous performance test bed](#performance-test-bed)
  - [Use aliases](#aliases)
  - [Avoid having big synonym collections](#synonyms)
  - [Force merge and increase operation bandwidth before enabling replicas](#force-merge)
  - [Record application-level metrics](#metrics)
  - [Invest in CPU!](#cpu)
  - [Avoid writing custom Elasticsearch plugins](#plugins)

<a name="mapping"/>

# Mapping

Here I share Elasticsearch
[mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
related tips.

<a name="nested-fields"/>

## Avoid `nested` fields

- Under the hood, each Elasticsearch document corresponds to a Lucene document,
  almost. Though this promise is broken for fields of type
  [`nested`](https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html).
  There each field is stored as a separate document next to the parent Lucene
  one. This has a couple of particular impacts:

  - Querying on `nested` fields is slower compared to fields in parent document
  - Retrieval of matching `nested` fields adds an extra slowdown
  - Once you update any field of a document containing `nested` fields,
    independent of whether you updated a nested field or not, all the underlying
    Lucene documents (parent and all its `nested` children) need to be marked as
    deleted and rewritten. In addition to slowing down your updates, such an
    operation also creates garbage to be cleaned up by segment merging later on.

- In certain ocassions, you can flatten `nested` fields. For instance, given the
  following document:

      #!json
      {
          "attributes": [
              {"key": "color", "val": "green"},
              {"key": "color", "val": "blue"},
              {"key": "size", "val": "medium"}
          ]
      }
    
  You can flatten it as follows:

      #!json
      {
          "attributes": {
              "color": ["green", "blue"],
              "size": "medium"
          }
      }

<a name="strict-mapping"/>

## Have a strict mapping

Do you know how many times I witnessed a production failure due to a new field
first receiving a `long` value where the rest of the values are of type
`double`? After the first received `long`, Elasticsearch creates the field, sets
its type to `long`, and shares this mapping change with the rest of the nodes in
the cluster. Then the rest of the `double` values are simply rejected due to
type mismatch.

- Have a strict mapping to avoid surprises.
- Don't blacklist, just whitelist.
- Avoid using [dynamic templates](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html)
  -- they are just gateway drugs.
- Disable [date detection](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-field-mapping.html#date-detection),
  which is on by default.

<a name="analyze"/>

## Don't analyze fields of type `string` unless necessary

By default, a freshly inserted string field is assigned of type
[`text`](https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html),
which incurs an analysis cost. Unless you need fuzzy matching but just
filtering, use type `keyword` instead. This is slightly an extension of [strict
mapping](#strict-mapping) bullet.

<a name="setting"/>

# Setting

Here I share Elasticsearch cluster
[settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-update-settings.html)
related tips.

<a name="tuning-merges"/>

## Unlearn every hack for tuning merges

Elasticsearch is in essence yet another distributed
[Lucene](http://lucene.apache.org/) offering, just like
[Solr](http://lucene.apache.org/solr/). Under the hood, every Elasticsearch
document corresponds to a Lucene document, almost. (There are certain exceptions
to this rule like `nested` fields, though this generalization is pretty
accurate.) In Lucene, documents are stored in
[segments](https://lucene.apache.org/core/3_0_3/fileformats.html). Elasticsearch
in the background continuously maintains these Lucene segments by means of the
following two patterns:

- In Lucene, when you delete and/or update a document, the old one gets marked
  as removed and a new one gets created. Elasticsearch keeps track of these dead
  documents and compacts such segments that are highly polluted by rebuilding
  them.

- Newly added documents might yield to segments of imbalanced sizes.
  Elasticsearch might decide to merge these into bigger ones for optimization
  purposes.

This aforementioned compaction is referred as [segment
merges](https://www.elastic.co/guide/en/elasticsearch/guide/current/merge-process.html)
in Elasticsearch terminology. As you can guess, merges are highly disk I/O- and
CPU-bound operations. As a user, you would not want to have them ruining your
Elasticsearch query performance. As a matter of fact, you can achieve this in
certain circumstances: Build the index once and don't change it anymore. Though
this condition might be difficult to meet in many application scenarios. Once
you start to insert new documents or update existing ones, segment merges become
an inevitable part of your life.

An on-going segment merge can significantly damage the overal query performance
of the cluster. Give it a search in the internet, you will find many people
looking for help to work around these and many others sharing certain tunings
that worked for them. Over the last years, there were two particular patterns I
observed in the shared tuning tips: they exist from the incarnation of this
operation (so everybody agrees that it used to hurt and is still hurting) and
the majority of the mentioned settings become deprecated (or even worse, become
unavailable) with the next Elasticsearch release. So my rules of thumb for
tuning merges start as follows:

1. Unlearn every hack you heard about tuning merges. It is an operation pretty
   coupled with the internals of Elasticsearch and subject to change without
   providing a backward compatibility fallback. There is no secret knob to make
   it run faster; it is like the garbage collector in JVM, `VACUUM` in
   PostgreSQL, etc.

2. Find the sweet spot for the
   [translog](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-translog.html)
   flushes. Start first by setting `index.translog.durability` to `async`. This
   suggestion assumes that you are smart enough to either not use Elasticsearch
   as your primary data storage or have necessary recovery measures in place.
   Next relax `index.translog.sync_interval` and
   `index.translog.flush_threshold_size` settings until you don't get any
   benefits for your usage pattern.

3. Adapt `index.refresh_interval` to your needs. Imagine you first bootstrap an
   index and later on occasionally perform small updates on it. In such a case,
   start with a loose (even disabled!) `refresh_interval` and make it tighter
   after bootstrap.

<a name="memory"/>

## Pay attention to JVM memory settings

Elasticsearch can yield dramatic performance characteristics dependending on two
primary memory settings: JVM heap space and the amount of memory left to the
kernel page cache. I am not going to dive into these details here, because they
are pretty well
[documented](https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html).
This is your reminder to not blindly set the Elasticsearch JVM heap size judging
from your past non-Elasticsearch JVM application experiences.

<a name="querying"/>

# Querying

Below I collected tips that you can take advantage of (or better stick to) while
querying Elasticsearch.

<a name="cas"/>

## Compare-and-swap over `_version` field is poor man's transactions

I believe you had already figured that Elasticsearch doesn't support
transactions. Though you can leverage the
[`_version`](https://www.elastic.co/guide/en/elasticsearch/reference/7.0/docs-get.html#get-versioning)
field in a [CAS](https://en.wikipedia.org/wiki/Compare-and-swap)-loop to provide
integrity at least on a single document basis. An example demonstration of this
trick can be summarized as follows:

    #!java
    String id = "123";
    for (;;) {
        EsDocument prevDoc = store.findById(id);
        long prevVersion = prevDoc.getVersion();
        Object prevSource = prevDoc.getSource();
        Object nextSource = update(prevSource);
        boolean updated = store.updateByIdAndVersion(id, prevVersion, nextSource);
        if (updated) {
            break;
        }
    }

Clearly this trick doesn't stretch to multiple indices or [parent/child
relations](https://www.elastic.co/guide/en/elasticsearch/reference/current/parent-join.html).

<a name="splitting-queries"/>

## Try splitting complex queries

If you have complex queries with both, say, filter and aggregation components,
splitting these into mutliple queries and executing them in parallel in most
cases speed up the querying performance. That is, in the first query just get
the hits using the filter, and in the second query, just get the aggregations
without retrieving hits, that is, `size: 0`.

<a name="numeric-types"/>

## Know your numeric types

Many JSON parsers reach for various optimizations to provide efficient
read/write performance. For instance,
[Jackson](https://github.com/FasterXML/jackson), the de facto JSON parser in the
Java world, picks the primitive with the smallest memory footprint that can
store the number passed by JSON. Hence after reading a field value via Jackson,
you might end up getting an `int`, `long`, `double`, etc. Once you get a, say,
`double`, it is highly likely that you had already lost precision and/or will be
losing precision while serializing it back to JSON again. To avoid such
surprises, prefer `BigDecimal` over `float` or `double`. Using `BigInteger` for
integral numbers is a safe bet too. (See
[USE_BIG_DECIMAL_FOR_FLOATS](https://fasterxml.github.io/jackson-databind/javadoc/2.0.0/com/fasterxml/jackson/databind/DeserializationFeature.html#USE_BIG_DECIMAL_FOR_FLOATS)
and
[USE_BIG_INTEGER_FOR_INTS](https://fasterxml.github.io/jackson-databind/javadoc/2.0.0/com/fasterxml/jackson/databind/DeserializationFeature.html#USE_BIG_INTEGER_FOR_INTS)
Jackson configurations for details.)

<a name="transport-client"/>

## Don't use Elasticsearch Transport/Node client in your Java application (and always use JSON over HTTP)

Elasticsearch is written in Java and its query model classes implement custom
(de)serialization methods using Jackson's `JsonGenerator` and `JsonParser`. This
way, thanks to Jackson, a model instance can be (de)serialized to both JSON
(text) and [SMILE](https://en.wikipedia.org/wiki/Smile_%28data_interchange_format%29)
(binary) formats without breaking a sweat. Logically, Elasticsearch uses the
binary format for communication within the cluster due to performance reasons.
Using `JsonParser` for parsing SMILE has a slight caveat: A schema cannot always
be evolved in such a way that the backwards compatibility is kept. Indeed this
is not a problem for an Elasticsearch cluster, all the nodes hopefully run the
same version. Though using SMILE in your application means that you might need
to shutdown your application, upgrade it to a newer version which is using the
models of the new Elasticsearch you are about to deploy in parallel.

What about performance between JSON and SMILE? Even Elastic's own data intensive
products such as Logstash and Kibana have replaced SMILE with JSON. It is highly
unlikely that your bottleneck while querying Elasticsearch would be
serialization. Further [Jackson is an excelling library in JSON serialization
efficiency](https://github.com/fabienrenaud/java-json-benchmark). Hence, to be
on the safe side, just stick to JSON over HTTP.

<a name="rest-client"/>

## Use the official Elasticsearch REST client in your Java application

[The official
driver](https://www.elastic.co/guide/en/elasticsearch/client/java-rest/current/index.html)
will be maintained through the lifetime of the project. It will implement
community approved features from its competitors. Unless something awkwardly
goes wrong, the official one will just either leave no room of additional value
to its competitors or they will just get rusted and disappear. That being said,
the official REST client is a piece of crap for two main reasons:

1. It has a leaky abstraction over [Apache HTTP
   Client](http://hc.apache.org/httpcomponents-client-ga/) whose configurations
   you need to deal with while tuning the client.
2. Do you recall [the query model classes I mentioned above](#transport-client)?
   I have some bad news for you: Model classes are entangled with the server
   code and the REST client uses those classes. So what does this mean for you?
   Well... Adding the REST client in your dependencies will drag the entire
   Elasticsearch milkyway into your JAR Hell.

[Eclipse Vert.x works around this
entanglement](https://github.com/reactiverse/elasticsearch-client) in a yet
another entangled way. Though I doubt if it will have a long lifetime given the
reasons I listed above.

In summary, the official REST client (unfortunately) is still your best bet.

<a name="cache-keys"/>

## Don't use Elasticsearch query models to generate cache keys

Or more specifically,

- \[If you want your hash keys to be consistent between different JVM processes,
  JVM upgrades, and JVM restarts,] don't use `Object#hashCode()`.

- The JSON generated by Elasticsearch query models for semantically identical
  queries are not necessarily identical. It took more than a year to figure this
  out ourselves. Hence, don't take the query model generated JSON as your source
  of hash. (My guess is that somewhere in the `JsonGenerator`-based serializers,
  they are probably iterating over a `java.util.Map` or `java.util.Set` whose
  order for identical content varies under different conditions.)

Ok. So what else is left? How one should do it?

1. You query Elasticsearch due to a request you have just received, right? Does
   that request has its own application level model? Good. There you go. Use
   that one as a hash source.

2. Your application level request model is too complex to generate a proper hash
   key? Doh! Ok. Don't tell anyone that I told you this: Parse Elasticsearch
   generated JSON using Jackson and let Jackson serialize it one more time back
   to JSON, but this time [instruct Jackson to sort the
   keys](https://fasterxml.github.io/jackson-databind/javadoc/2.0.0/com/fasterxml/jackson/databind/SerializationFeature.html#ORDER_MAP_ENTRIES_BY_KEYS).

<a name="http-caching"/>

## Don't use HTTP caching for caching Elasticsearch responses

Many people fall in the trap of fronting their Elasticsearch cluster with an
HTTP cache such as [Varnish](http://varnish-cache.org/) due to its convenience
and low entry barrier. Though this appealing approach has certain shortcomings:

- When using Elasticsearch in production, it is highly likely you will end up
  having multiple clusters due to various reasons: resiliency, experimentation
  room, zero downtime upgrades, etc. Then,

  - once you front each cluster with a dedicated HTTP cache, 99% of the cache
    content will just be duplicated.

  - if you decide to use a single HTTP cache for all clusters, it is really
    difficult to programmatically configure an HTTP cache to adopt the needs of
    the ever changing cluster states. How will you communicate the load to let
    the cache balance the traffic. How will you configure scheduled or manual
    downtimes? How will you let the cache gradually migrate the traffic from one
    to another during maintanence windows?

- As mentioned above, HTTP caches are difficult to command programmatically.
  When you need to manually evict one or more entries, it is not always as easy
  as a `DELETE FROM cache WHERE keys IN (...)` query. And let me warn you, you
  are gonna need that manual eviction.

<a name="sliced-scrolls"/>

## Use sliced scrolls sorted on `_doc`

[Scrolls](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-scroll.html)
are the vehicle that Elasticsearch lets you scan its entire dataset for large
reads. They are functionally (and surprisingly, internally too) pretty much
similar to [RDBMS cursors](https://en.wikipedia.org/wiki/Cursor_(databases)).
Though most people don't get them right in their first attempt. Here are some
basics:

- If you reach for scrolls, you are probably reading quite some data. It is
  highly likely [slicing](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-scroll.html#sliced-scroll) will help you improve the read performance
  significantly.

- The order doesn't matter in your reads? This is your lucky day then! Just sort
  on `_doc` field and there goes your +20% read speed up without any charges.
  (`_doc` is a pseudo field to let Elasticsearch use the order documents are
  laid out on the disk.)

- The `scrollId` might (and does!) change between calls. Hence make sure you are
  always scrolling using the most recently retrieved `scrollId`.

- Reaching for `REINDEX`? Did you enable slicing there too? Good.

<a name="get-by-id"/>

## Prefer `GET /index/type/{id}` over `POST /index/_search` for single document retrieval

Elasticsearch uses different thread pools to handle `GET /index/type/{id}` and
`POST /index/_search` queries. Using `POST /index/_search` with payload `{query:
{"match": {"_id": "123"}}}` (or something similar) occupies your
search-dedicated thread pool. Under heavy load, this will worsen your both
search and single document fetch performance. Simply just stick to `GET
/index/type/{id}`.

<a name="size0-includes-excludes"/>

## Use `size: 0` and `includes`/`excludes` wisely

This tip I guess applies to any storage engine of your preference: Avoid
retrieving (or even storing!) content unless necessary. I have witnessed
Elasticsearch showing dramatic performance differences before and after adding a
`size: 0` clause.

<a name="backpressure"/>

## Implement proper backpressure while querying

Yet another database-independent tip: There is no point in hammering your
database to the point of making it choke. Consider the following Java snippet
employing an imaginary database client:

    #!java
    void findUserById(String id, Callable<User> callback) {
        dbClient.find("user")
                .filter("id", id)
                .first(callback::apply);
    }

Assuming `dbClient` is implemented in a non-blocking and asynchronous fashion --
that is, each request is enqueued to be delivered and each response handler is
enqueued to react on incoming payloads -- what would happen if your database can
handle at most 1 req/sec while your application perfectly receives, handles, and
passes forward 10 req/sec? Let me draw you a shallow probability tree depicting
consequences of such an incident.

1. Your database gets loaded more than it can take. If your database has proper
   backpressure mechanics, which most don't possess, including Elasticsearch,

  - Then it will start choking and eventually throw up. This will get reflected
    as query errors on the application side. If your application is equipped
    with backpressure mechanics as well, it can kindly reflect this back to the
    caller.
 
  - Otherwise,

    1. even the simplest database queries will start suffering due to heavy load.
    
    2. the database process queue will overgrow.

       1. Excessive growth of the queue (that is, no backpressure mechanics in
          place) will start stressing the process memory.

       2. The requests succeed in making from the queue to an executor thread
          will highly likely already become deprecated. That is, database will
          be doing job that is of use to nobody.

    3. above two points drawn from the process queue overgrow of the database,
       apply as is to the application too.

Unfortunately there is no silver bullet or a step-by-step guide of implementing
backpressure for a particular application. This in a way makes sense, each has
its own domain-specific requirements. That being said, I can share my personal
best practices:

- Use performance benchmarks of your application (You have performance
  benchmarks, right?) to estimate an upper bound on the load that your
  application delivers an acceptable performance. Enforce this limit in your
  application via a rate limiter. Please, please, please don't block the carrier
  thread using the rate limiter! Rather just communicate the backpressure to
  your client, for instance, by means of an [HTTP 503 (SERVICE UNAVAILABLE)
  status code](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#5xx_Server_errors).

- Avoid using thread pools with an unbounded task queue. Java programmers, all
  your RxJava/Reactor schedulers are by default backed by a
  `ScheduledThreadPoolExecutor` (the one and only `ScheduledExecutorService`
  implementation in the Java standard library) and that internally uses an
  unbounded task queue, unfortunately. See [this Stack Overflow
  post](https://stackoverflow.com/q/7403764/1278899) and [that
  concurrency-interest
  discussion](http://cs.oswego.edu/pipermail/concurrency-interest/2019-April/016860.html)
  on how to work around that.

- If your application is a pipe between two resources (e.g., from a Pubsub queue
  to an Elasticsearch cluster) make sure your producers react to consumers'
  backpressure. That is, if the consumer latency starts increasing, you better
  start slowing down the producer.

<a name="explicit-timeouts"/>

## Provide explicit timeouts in queries

Almost all Elasticsearch API endpoints allow the user to specify a timeout, use
that. This will help both your application and your Elasticsearch cluster: Spot
and shrug off unpexected long running operations and save associated resources,
establish a stable SLA with no surprises, etc.

<a name="blocking-io-threads"/>

## Don't block the Elasticsearch client I/O threads (and know your threads)

This tip is also database independent: Don't block I/O threads of an external
resource for another external resource. Let me demonstrate this pitfall with a
snippet:

    #!java
    public void enrichUserById(String id, Function<EsDocument, EsDocument> enricher, Runnable callback) {
        esClient.findUserById(id, user -> {
            EsDocument enrichedUser = enricher.apply(user);
            esClient.saveUserById(id, enrichedUser, callback);
        });
    }

What is mostly unintentional here is that: Both `enricher.apply(user)` and
`callback.run()` will get executed in the Elasticsearch client I/O thread. Here
I see two common cases:

- If both functions don't incur any other I/O calls (except the ones that are
  again reaching for Elasticsearch) and this is the only place in the entire
  application where you access to Elasticsearch, then this is a good practice.
  You repurpose Elasticsearch client I/O thread for a CPU-intensive
  post-processing. Almost no thread context-switch costs. On a 4 core machine,
  with 4 threads dedicated to Elasticsearch client I/O, you will get an almost
  optimal performance given your usage pattern.

- If both or any of the functions internally perform other I/O calls and/or
  there are multiple places in the application where Elasticsearch client is
  used for different purposes, then you are occupying the Elasticsearch client
  I/O threads for something unrelated whereas these threads could have just been
  serving yet another Elasticsearch request. In such cases, it is better to
  employ task-specific thread pools and avoid exhausting Elasticsearch client
  I/O loop unnecessarily:

      #!java
      public void enrichUserById(String id, Function<EsDocument, EsDocument> enricher, Runnable callback) {
          esClient.findUserById(id, user -> {
              computationExecutor.submit(() -> {
                EsDocument enrichedUser = enricher.apply(user);
                esClient.saveUserById(id, enrichedUser, () -> {
                    computationExecutor.submit(callback);
                });
              });
          });
      }

<a name="json-templates"/>

## Don't write Elasticsearch queries with JSON templates injecting variables

Don't ever do this:

    #!json
    {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "username": {
                                "value": {{username}}
                            }
                        }
                    },
                    {
                        "term": {
                            "password": {
                                "password": {{password}}
                            }
                        }
                    },
                ]
            }
        }
    }

You are just falling into a half-century old trap: [SQL
injection](https://en.wikipedia.org/wiki/SQL_injection), adopted for
Elasticsearch. No matter how smart your character whitelisting, escaping
routines are, it is just a matter of time someone passes a malicious `username`
and/or `password` input that would expose your entire dataset. I also personally
find it a pretty bad practice to render a curly brace (`{`, `}`) rich structured
text via a templating language (e.g., Moustache, Handlebars) which uses the very
same curly braces for its own directives.

There are two safe approaches that I can recommend to generate dynamic queries:

1. Use the query models provided by the Elasticsearch (official) client. (This
   works for Java pretty well.)
2. Use a JSON library (e.g., [Jackson](https://github.com/FasterXML/jackson)) to
   build the JSON tree and serialize it to JSON.

<a name="json-serializer"/>

## Prefer your own JSON serializer over the one provided by Elasticsearch clients

Many Elasticsearch clients allow you to pass a generic JSON object and serialize
it to JSON before passing it over the wire. For instance, the official
Elasticsearch REST client for Java allows `java.util.Map<String, Object>`
instances as source. Then it uses its own JSON serializer to translate these
models into JSON. While this works fine for vanilla Java, which is most of the
time sufficient to get the message across in tutorials, most real world
applications have more complex class structures that necessitate custom
serialization. For instance, speaking of Java client, how does it serialize
Guava models? What about the new date and time classes introduced in Java 8?
What will happen to all your `@JsonProperty`-, `@JsonSerializes`-, etc.
annotated classes? Hence it is always a better practice to employ your own
serialization and pass a `byte[]` as source to the client. That will save you
from surprises.

<a name="strategy"/>

# Strategy

In this last section I collected convenient *strategic* (whatever that means)
practices which address concerns not covered above.

<a name="latest-version"/>

## Always (try to) stick to the latest JVM and Elasticsearch versions

Elasticsearch is a Java application. (Surprise, surprise!) Like every other Java
application it has its hot paths and garbage collection dues. Almost every new
JVM release will bring you extra optimizations that you can take advantage of
without breaking a sweat. Note that due to the low-level performance hacks
exploited in Lucene, which is internally used by Elasticsearch, Lucene is sort
of fragile to JVM upgrades, particularly involving garbage collector changes.
Fortunately, Elasticsearch has an official page listing supported [JVM
releases](https://www.elastic.co/support/matrix#matrix_jvm) and [garbage
collectors](https://www.elastic.co/guide/en/elasticsearch/guide/current/_don_8217_t_touch_these_settings.html).
Always check these pages out before attempting any JVM upgrades.

Elasticsearch upgrades are also a source of free performance gains. I have never
experienced a regression after Elasticsearch upgrades. That said, your milage
may vary and this is why you should have proper integration tests in place.

<a name="snapshots"/>

## Use Elasticsearch complete and partial snapshots for backups

Elasticsearch lets you easily take
[snapshots](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-snapshots.html)
of an index either completely or partially against an existing snapshot.
Depending on your update patterns and index size, find the best combination for
your use case. That is, for instance, 1 complete snapshot at 00:00 and 3 partial
snapshots at 06:00, 12:00, and 18:00. It is also known to be a good practice to
have them stored at [AWS S3](https://aws.amazon.com/s3/) or [GCP
Storage](https://cloud.google.com/storage/). There exists
[plugins](https://www.elastic.co/guide/en/elasticsearch/plugins/master/repository.html)
to facilitate these scenarios.

As in every backup solution, make sure you can restore them and practice this a
couple of times. In case of a post-failure restoration, you might need to
engineer your own replay mechanisms to reach the last stable state just before
the crash. Leveraging queues supporting custom retention periods (e.g., keep all
the messages received in the last 2 days) for this purpose is a practice
employed a lot.

<a name="performance-test-bed"/>

## Have a continuous performance test bed

Like any other database, Elasticsearch shows varying performance under different
conditions: index, document sizes; update, query patterns; index, cluster
settings; hardware, OS, JVM versions; etc. It is difficult to keep track of each
knob to observe its impact on the overall performance. Make sure you have
(at least) daily performance tests to help you narrow down a recently introduced
change damaging the performance.

This utopic test bed is easier said than done. You will need to make sure that
the test environment has representative data of production, (preferably)
identical configuration to production, complete coverage of use cases, and
provides a clean slate (including the OS cache!) for each test to avoid
retaining the effects of a previous run. I know, quite a list. But it pays off.

<a name="aliases"/>

## Use aliases

Now I am gonna tell you something quite opinionated, though backed by
experience: Never query against indices, but
[alias](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-aliases.html)es.
Aliases are pointers to actual indices. You can group one or more indices under
a single alias. Many Elasticsearch indices have an internal context attached to
the index name, such as, `events-20190515`. Now you have two choices in the
application code while querying against `events-*` indices:

1. Determine the index name on the fly via a certain date pattern:
   `events-YYYYMMDD`. This approach has two major drawbacks:

   - The need to fallback to an index of a particular date necessitates the
     entire code base to be engineered accordingly to support such an operation.

   - Putting all clock synchronization issues aside, at midnight, you need to
     make sure that the next index is there.

2. Create an `events` alias pointing to the `events-*` index you want the
   application to use. The component responsible for the creation of the new
   indices can atomically switch the alias to the new index. This approach will
   bring two notable benefits:

   - It doesn't suffer from the drawbacks of the previous approach.

   - The application code is way more simpler by just pointing to the `events`
     index everywhere.

<a name="synonyms"/>

## Avoid having big synonym collections

Elasticsearch supports both index- and query-time
[synonyms](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-synonym-tokenfilter.html).
These are powerful shotguns with a good track record of shooting its holder in
the foot. No search engine is complete without synonyms, hence they have pretty
valid use cases. Though the following implications need to be kept in mind while
employing them:

- Index-time synonyms increase the index size and creates an extra runtime
  overhead.

- Query-time synonyms doesn't add up to the index size, but as their name
  implies, creates an extra runtime overhead.

- Using synonyms, it is pretty easy to unintentionally break something while
  trying to fix some other thing.

Continuosly monitor the impact of synonyms on the performance and try to write
tests for each synonym added.

<a name="force-merge"/>

## Force merge and increase operation bandwidth before enabling replicas

A really common Elasticsearch use case is to periodically (once every couple of
hours) create an index. There is a really good
[SoundCloud](https://developers.soundcloud.com/blog/how-to-reindex-1-billion-documents-in-1-hour-at-soundcloud)
article on how to achieve the optimal performance. Quoting from that
compilation, there are the following items that I particularly find a "must".

1. Always enable replicas after completing the indexing.
2. Before enabling replicas, make sure you
   - shrinked the index size by [forcing a
     merge](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-forcemerge.html)
     and
   - increased the replica transmission bandwidth, that is,
     [`indices.recovery.max_bytes_per_sec`](https://www.elastic.co/guide/en/elasticsearch/reference/current/recovery.html).

<a name="metrics"/>

## Record application-level metrics

Kibana provides quite solid insights into the Elasticsearch performance:
indexing, search latency and throughput; flush, merge operations; etc. Once you
enhance this view with extra JVM (GC pauses, heap size, etc.) and OS (CPU usage,
disk I/O, kernel caches, etc.) metrics, you will get a rock solid monitoring
dashboard. That said, this is not enough. It is used by a single application or
more, Elasticsearch will get hit by various access patterns. Imagine a part of
your software trying to shovel off 10 million documents of not-so-important user
activity, while another component is trying to update user account details. If
you would look at your shiny Elasticsearch metrics, everything will look fine
since 10 million document updates will make the statistical effect of user
account updates disappear. On the other hand, your users might not be that much
happy with the latency they observe while they are trying to update their
accounts. Hence always expose extra application-level metrics for your
Elasticsearch queries. While Elasticsearch metrics provide sufficient indicators
for the overall cluster performance, they lack the domain-specific context.

<a name="cpu"/>

## Invest in CPU!

I cannot emphasise this enough: **invest in CPU!** Now open your dashboards,
look at the metrics of your most recent Elasticsearch hammering session in
production, and tell me whether you are disk I/O, memory, or CPU bound? I am not
telling you to use a 32-core machine with an inferior SATA disk drive and 8 GB
of memory. Rather what I am talking about is this: get a decent machine with
sufficient memory and SSD (you might want to checkout NVMe cards too depending
on your disk I/O), after that invest in CPU. Judging from my past experiences,
whether it is a write- or read-heavy load, CPU has always been our bottleneck.

<a name="plugins"/>

## Avoid writing custom Elasticsearch plugins

Once I had the opportunity to have the joy of pairing with a colleague to write
an Elasticsearch plugin that exposes synonyms over a REST endpoint. That allowed
us to query synonyms uploaded to an Elasticsearch cluster at runtime and
manipulate it on-the-fly. After having 20 releases where we were convinced that
there are no more concurrency bugs (actually, we had been pretty convinced in
the previous 19 releases too), it worked like a charm. Though the real suffering
started when we tried to upgrade the Elasticsearch supported by the plugin. In a
nutshell, avoid writing custom Elasticsearch plugins, because...

- Many Elasticsearch releases contain significant internal changes. It is highly
  likely the public APIs you erect your plugin on will get backward incompatible
  changes.

- Getting concurrency right in an environment where you are not much accustomed
  to can be daunting.

- You need to tailor your deployment procedure to ship the plugin everytime and
  everywhere it is needed. You cannot just use the vanilla Elasticsearch
  artifacts as is anymore.

- Since your application depends on the specific functionality provided by the
  plugin, the Elasticsearch instances you run during integration tests also need
  to incorporate the plugin as well. Hence you cannot use vanilla, say, Docker
  images out of the box anymore.
