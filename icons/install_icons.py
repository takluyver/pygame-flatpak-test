"""Run like:

    python3 install_icons.py org.pygame.aliens
"""
from subprocess import check_call
import sys

name = sys.argv[1]
for size in [32, 48, 64, 96, 128]:
    src = "icons/pygame_snake_{}.png".format(size)
    dest = "/app/share/icons/hicolor/{size}x{size}/apps/{name}.png".format(
            size=size, name=name
    )
    print("Installing", src, dest)
    check_call(['install', '-TD',  src, dest])
