"""This is copied into the project directory and run in the flatpak build environment.

It installs the necessary files for the game into the /app prefix.
"""

import json
import os
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns
import sys

DESKTOP_TEMPLATE = """\
[Desktop Entry]
Type=Application
Name={name}
Icon={appid}
Exec=/app/bin/launch-game
Categories=Game
"""

LAUNCHER_TEMPLATE = """\
#!{python}
from {mod} import {func}
{func}()
"""

python_paths = {
    '3.6': '/app/bin/python3',
    '3.4': '/usr/bin/python3',
    '2.7': '/usr/bin/python',
}

def main():
    with open('build/flatpak/config.json') as f:
        config = json.load(f)
    print("Making install dir")
    install_dir = Path('/app/share/mygame')
    install_dir.mkdir(parents=True)
    for file in config['files']:
        if os.path.isdir(file):
            copytree(file, str(install_dir / file),
                    ignore=ignore_patterns('__pycache__', '*.pyc'))
        else:
            copy2(file, str(install_dir))
    
    # Icons
    print("Installing icons")
    for size, path in config['icons'].items():
        target_path = '/app/share/icons/hicolor/{size}x{size}/apps/{appid}.png'.format(
                        size=size, appid=config['appid'])
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        copy2(path, target_path)
    
    # Desktop file
    print("Writing desktop file")
    desktop_target = '/app/share/applications/{}.desktop'.format(config['appid'])
    os.makedirs(os.path.dirname(desktop_target), exist_ok=True)
    with open(desktop_target, 'w') as f:
        f.write(DESKTOP_TEMPLATE.format_map(config))
    
    # Launcher
    print("Creating launch script")
    module, func = config['entry-point'].split(':')
    launcher_file = install_dir / 'launch-game.py'
    with launcher_file.open('w') as f:
        f.write(LAUNCHER_TEMPLATE.format(
            python=python_paths[config['python']],
            mod = module, func=func
        ))
    launcher_file.chmod(0o755)
    Path('/app/bin/launch-game').symlink_to(launcher_file)

if __name__ == '__main__':
    main()
