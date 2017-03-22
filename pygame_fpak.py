from pathlib import Path
import pytoml
import shutil
from subprocess import run
import sys

def flatpak(*args):
    run(args, check=True)

def get_baseapp(baseapp):
    flatpak('--user', 'remote-add', '--if-not-exists', '--from',
    'pygame-bases', 'https://takluyver.github.io/pygame-flatpak-test/pgbase.flatpakrepo')
    flatpak('--user', 'install', 'pygame-bases', baseapp)
    

def build_repo(config, project_dir):
    build_dir = project_dir / 'build' / 'flatpak-build'
    try:
        shutil.rmtree(build_dir)
    except FileNotFoundError:
        pass

    baseapp = 'org.pygame.BaseApp-py{}{}'.format(*config['python'].split('.'))
    flatpak('build-init', '--base', baseapp, build_dir, config['appid'],
            'org.freedesktop.Sdk', 'org.freedesktop.Platform', '1.4')
    flatpak('build', build_dir, sys.executable, '-m', 'pygame_fpak.inner')
    flatpak('build-finish', build_dir, '--socket=x11', '--socket=pulseaudio', '--command=launch-game')

    repo_dir = project_dir / 'build' / 'flatpak-repo'
    flatpak('build-export', repo_dir, build_dir)
    return repo_dir

class InputError(ValueError):
    pass

def check_config(config):
    if config['python'] not in {'3.6', '3.4', '2.7'}:
        raise InputError("Python version should be 3.6, 3.4 or 2.7, not {}"
                         .format(config['python']))

def main(argv=None):
    if argv is None:
        argv = sys.argv
    config = pytoml.load(argv[1])
    check_config(config)
    project_dir = Path(argv[1]).resolve().parent
    build_repo(config, project_dir)

if __name__ == '__main__':
    main()
