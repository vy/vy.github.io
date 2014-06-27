---
kind: article
created_at: 2014-06-27 16:49 EET
title: Parsing Bitcoin Blockchain Data in Java
tags:
  - bitcoin
  - java
---

Last week I spent some time on collecting certain statistics (e.g., average
number of performed transactions and created blocks per month) over a vast
(~20GB) Bitcoin blockchain dataset. The hardest part for me was to pick the
right tool to parse the raw blockchain data. First, I hit the Google with
*"parse bitcoin blockchain"* keywords. Unfortunately, the returned results
([bitcointools](https://github.com/gavinandresen/bitcointools),
[blockchain](https://code.google.com/p/blockchain/),
[blockparser](https://github.com/znort987/blockparser), etc.) point to almost
undocumented projects, where some appear to not even work. (As a side note,
bitcointools require a running BitcoinQt/bitcoind process in the background,
which I find pretty amusing.) Next, I checked some papers on Google Scholars to
find out how other people solved the problem. A paper leaded me to
[BitcoinArmory](https://github.com/etotheipi/BitcoinArmory) project, which
requires a dozen of manual interventions to get installed. (I did not even
attempt to install it.) Suddenly, it occured me to add a *"java"* keyword to the
search phrase, which led me to [bitcoinj](https://bitcoinj.github.io/) project.
***bitcoinj is far most the best Bitcoin blockchain parser library that I have
ever met.*** It has a rich documentation, developer-friendly (and fully
documented) API and works out of the box. It is composed of a single JAR, no
other requirements, stupid hassles, etc. In addition, its IRC channel at
FreeNode is packed with real people that provide instant support on any Bitcoin
related questions.

Enough with the talk! Let's get our hands dirty with the code. I first included
the bitcoinj Maven dependency in my `pom.xml` as follows:

    #!xml
    <dependency>
        <groupId>com.google</groupId>
        <artifactId>bitcoinj</artifactId>
        <version>0.11.3</version>
        <scope>compile</scope>
    </dependency>

Next, I downloaded a couple of raw blockchain data for test purposes:

* [Sample data composed of 5000 blocks](https://code.google.com/p/blockchain/source/browse/trunk/blk00000.dat) (128 MB)
* [From the genesis block through height 295,000](https://bitfetch.com/static/bootstrap.7z) (4.7 GB)
* [From the genesis block through a recent height](https://bitcoin.org/bin/blockchain/bootstrap.dat.torrent) (~17 GB as of this post)

Here comes the simplest part: the Java code. Below, I calculate the average
number of transactions per block per month.

    #!java
    import com.google.bitcoin.core.Block;
    import com.google.bitcoin.core.NetworkParameters;
    import com.google.bitcoin.core.PrunedException;
    import com.google.bitcoin.core.Transaction;
    import com.google.bitcoin.params.MainNetParams;
    import com.google.bitcoin.store.BlockStoreException;

    import java.io.File;
    import java.util.ArrayList;  
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;

    // Arm the blockchain file loader.
    NetworkParameters np = new MainNetParams();
    List<File> blockChainFiles = new ArrayList<>();
    blockChainFiles.add(new File("/tmp/bootstrap.dat"));
    BlockFileLoader bfl = new BlockFileLoader(np, blockChainFiles);

    // Data structures to keep the statistics.
    Map<String, Integer> monthlyTxCount = new HashMap<>();
    Map<String, Integer> monthlyBlockCount = new HashMap<>();

    // Iterate over the blocks in the dataset.
    for (Block block : bfl) {

        // Extract the month keyword.
        String month = new SimpleDateFormat("yyyy-MM").format(block.getTime());

        // Make sure there exists an entry for the extracted month.
        if (!monthlyBlockCount.containsKey(month)) {
            monthlyBlockCount.put(month, 0);
            monthlyTxCount.put(month, 0);
        }

        // Update the statistics.
        monthlyBlockCount.put(month, 1 + monthlyBlockCount.get(month));
        monthlyTxCount.put(month, block.getTransactions().size() + monthlyTxCount.get(month));

    }

    // Compute the average number of transactions per block per month.
    Map<String, Float> monthlyAvgTxCountPerBlock = new HashMap<>();
    for (String month : monthlyBlockCount.keySet())
        monthlyAvgTxCountPerBlock.put(
                month, (float) monthlyTxCount.get(month) / monthlyBlockCount.get(month));

That's it! In order to appreciate the hassle-free simplicity of the bitcoinj
interface, you ought to take your time and spend a couple of hours on other
tools first. (About the performance, for the sample blockchain dataset of size
4.7 GB, above code snippet completes in less than 2 minutes on my 2.4 GHz
GNU/Linux notebook without any JVM flags. Pretty zippy!)
