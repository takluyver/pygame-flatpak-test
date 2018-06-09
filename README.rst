Flatpak packaging for pygame

`Flatpak <http://flatpak.org/>`__ is a sandboxed application packaging system
for Linux (`developer docs <http://docs.flatpak.org/en/latest/index.html>`__).
Pygame is a framework for making games.

June 2018
---------

I've focused on using ``flatpak-builder`` with JSON manifests,
rather than the Python tool I started last year.
Apps hosted on `Flathub <https://flathub.org/home>`_ have to be built this way.

The main files of interest are:

``org.pygame.baseapp.json``
  A 'base app' with all pygame's dependencies
``org.pygame.baseapp-py35.json``
  A 'base app' building on the previous one by adding pygame itself.
  This uses the Freedesktop 1.6 runtime, which contains Python 3.5.
``org.pygame.aliens.json``
  A sample application which launches the *Aliens* example game included with
  pygame.

-------------

March 2017
----------

This is an *experimental* tool to make Flatpak packages for pygame games. To use
it:

1. You will need a Linux system with Flatpak >= 0.8 installed, such as Fedora 25
   or Ubuntu 17.10.
2. Install using ``pip install pygame_fpak``. The tool needs Python 3 to run,
   even if your game uses Python 2.
3. Create a ``pygame-fpak.toml`` config file like this:

   .. code-block:: toml
   
       # At the moment, you can specify "3.6", "3.4" or "2.7".
       # 3.6 produces a somewhat bigger app to download.
       python = "3.6"
       # User-visible name
       name = "Solarwolf"
       # Identifier based on a reverse domain name you control. E.g. if your
       # project is on Github, you could use io.github.username.reponame
       appid = "org.pygame.solarwolf"
       # Files/directories needed to run the game - relative paths from where
       # the config file lives.
       files = [
         "solarwolf"
       ]
       # The function to start your game. This will be called like:
       # from solarwolf.cli import main; main()
       entry-point = "solarwolf.cli:main"

       # Icons in different sizes. Icons should be square, sizes are pixels
       # along one side of a square. 32, 48 and 64 are common.
       [icons]
       64 = "dist/solarwolf.png"

4. Run ``python3 -m pygame_fpak pygame-fpak.toml``.

------

The other code in this repo builds the base apps for the tool described above.
To build & install them:

.. code-block:: shell

    # Slow, but only needed once:
    make install-runtime
    
    # Build the base applications and install them:
    make install-baseapp-py36.done
    make install-baseapp-py34.done
    make install-baseapp-py27.done

There are three variants of the base application:

- ``-py36`` includes Python 3.6 as ``/app/bin/python3``. This is approximately
  30 MiB to download, and 140 MiB when installed. The *Aliens* example is built
  on this by default.
- ``-py34`` uses Python 3.4, which is provided by the freedesktop.org runtime.
  This makes it smaller - about 7 MiB to download, and 40 MiB installed - but
  you can't use the latest Python features in your code.
- ``py27`` uses Python 2.7. It is a similar size to the Python 3.4 base app.

Flatpak applications use a *runtime*, a bundle of common libraries and
executables. If your application is the first a user installs with a given
runtime, Flatpak will download the runtime as well. Hopefully most apps will
share a few runtimes, so that installation is quick and easy.
