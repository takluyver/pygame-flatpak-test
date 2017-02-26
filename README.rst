Example flatpak packaging for pygame

`Flatpak <http://flatpak.org/>`__ is a sandboxed application packaging system
for Linux (`developer docs <http://docs.flatpak.org/en/latest/index.html>`__).
Pygame is a framework for making games.

The code here builds a flatpak package of the pygame *Aliens* example game. To
try it out on a system with Flatpak::

    make build-dir export reinstall
    flatpak run org.pygame.aliens

Look inside the Makefile for more details of what's going on. It's based on the
`building simple apps <http://docs.flatpak.org/en/latest/building-simple-apps.html>`__
section of the Flatpak docs.
