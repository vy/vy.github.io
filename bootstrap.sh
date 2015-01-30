#!/usr/bin/env bash

locale-gen UTF-8
apt-get update
apt-get install -y zlib1g-dev python-pip ruby-dev
pip install Pygments
gem install nanoc nanoc-toolbox builder kramdown pygments.rb sass adsf
