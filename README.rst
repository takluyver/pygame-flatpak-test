Example flatpak packaging for pygame

`Flatpak <http://flatpak.org/>`__ is a sandboxed application packaging system
for Linux (`developer docs <http://docs.flatpak.org/en/latest/index.html>`__).
Pygame is a framework for making games.

The code here builds a flatpak package of the pygame *Aliens* example game. To
try it out on a system with Flatpak, run:

.. code-block:: shell

    # Slow, but only needed once:
    make install-runtime
    
    # Build the base applications and install them:
    make install-baseapp-py36.done
    make install-baseapp-py34.done
    
    # Build and install the 'aliens' example
    make install-aliens
    
    # Play!
    flatpak run org.pygame.aliens

There are two variants of the base application:

- ``-py36`` includes Python 3.6 as ``/app/bin/python3``. This is approximately
  30 MiB to download, and 140 MiB when installed. The *Aliens* example is built
  on this by default.
- ``-py34`` uses Python 3.4, which is provided by the freedesktop.org runtime.
  This makes it smaller - about 7 MiB to download, and 40 MiB installed - but
  you can't use the latest Python features in your code.

Flatpak applications use a *runtime*, a bundle of common libraries and
executables. If your application is the first a user installs with a given
runtime, Flatpak will download the runtime as well. Hopefully most apps will
share a few runtimes, so that installation is quick and easy.
