# About

This branch contains the sources for generating my personal web site. You can
either [view it online](https://vlkan.com/) or
[browse the generated content](https://github.com/vy/vy.github.io/tree/master/).

# Installation

You can easily bootstrap a development environment by using `./docker.sh build`.
Once the Docker image is built, you can run it via `./docker.sh run` and browse
to `/app` directory to access the sources.

Then you are safe to go.

    $ nanoc co
    $ nanoc view

By default, `nanoc view` uses port 3000, which is also forwarded to the host
machine. Hence, you can view the website by browsing to `http://localhost:3000/`
on your host system.

# License

This work by Volkan Yazıcı is licensed under a [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/deed.en_US).

[![Creative Commons License](http://i.creativecommons.org/l/by/3.0/80x15.png)](http://creativecommons.org/licenses/by/3.0/deed.en_US)
