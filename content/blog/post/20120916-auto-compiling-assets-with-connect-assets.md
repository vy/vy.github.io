---
kind: article
created_at: 2012-09-16 12:19 EET
title: Auto-Compiling Assets with connect-assets
tags:
  - coffeescript
  - expressjs
  - javascript
  - nodejs
  - railwayjs
---

I have been using [RailwayJS](http://www.railwayjs.com/) for a couple of weeks with great satisfaction and joy. Its built-in support for CoffeeScript files is fantastic. That being said, like a majority of other [NodeJS](http://www.nodejs.org) web frameworks (e.g. [Geddy](http://geddyjs.org/), [Tower.js](http://towerjs.org/), [SocketStream](http://www.socketstream.org/), [FlatIron](http://flatironjs.org/)) it doesn't provide a way to ship client-side CoffeeScript files. (In this context, [Meteor](http://www.meteor.com/) represents a notable exception, where it is capable of handling CoffeeScript files both at the server- and client-side.)

To establish a complete CoffeeScript experience both at the server- and client-side, one can use [connect-assets](https://github.com/TrevorBurnham/connect-assets) by [Trevor Burnham](http://trevorburnham.com/) to auto-compile *assets* (i.e., CoffeeScript, Stylus, LESS files) on-the-fly. For this purpose, you just need to (1) add a `app.use require('connect-assets')()` line to your `environment.coffee`, (2) create `js` and `css` folders under `assets` directory, and you are ready to go.

One minor glitch that you need to pay attention is, while using connect-assets, you *must* include asset files using accessor functions -- `js()` and `css()` -- provided by connect-assets. These functions in addition to generating necessary `<script src="..."></script>` tag, also register the file into the asset processor service. connect-assets auto-compiles an asset the first time it is called and caches the produced output in memory; later calls will be served from the cache. (It also provides options to write produced outputs to disk and watch file changes.) For instance, say you want to use `/assets/js/main.coffee` in `/app/views/main/index.ejs` file. For this purpose, you need to add `<%%- js('main') %>` into your view for enabling connect-assets serving your `main.coffee` file.

As a final note, since connect-assets is a [Connect](http://www.senchalabs.org/connect/) plugin, you should be able to run it on any other web framework that runs on Connect or [ExpressJS](http://expressjs.com/).
