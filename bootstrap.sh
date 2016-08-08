#!/usr/bin/env bash

locale-gen UTF-8
add-apt-repository -y ppa:brightbox/ruby-ng-experimental
apt-get update
apt-get install -y zlib1g-dev python-pip ruby2.2 ruby2.2-dev
pip install Pygments
gem install \
	adsf:1.2.0 \
	builder:3.2.2 \
	colored:1.2 \
	cri:2.7.0 \
	jsmin:1.0.1 \
	kramdown:1.9.0 \
	mini_portile:0.6.2 \
	nanoc:3.8.0 \
	nanoc-toolbox:0.2.1 \
	nokogiri:1.6.6.4 \
	posix-spawn:0.3.11 \
	pygments.rb:0.6.3 \
	rack:1.6.4 \
	sass:3.4.19 \
	yajl-ruby:1.2.1
