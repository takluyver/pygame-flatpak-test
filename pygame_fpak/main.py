import json
from pathlib import Path
import pytoml
import shutil
from subprocess import run
import sys

def flatpak(*args):
    run(('flatpak',) + args, check=True)

def get_baseapp(baseapp):
    flatpak('--user', 'remote-add', '--if-not-exists', '--from',
    'pygame-bases', 'https://takluyver.github.io/pygame-flatpak-test/pgbase.flatpakrepo')
    flatpak('--user', 'install', 'pygame-bases', baseapp)

inner_py = Path(__file__).parent / 'inner.py'

def call_build_script(project_dir, packing_dir, build_dir, config):
    """Copy the build script and call it inside the flatpak build.
    """
    print('Running build script...')
    build_script = packing_dir / 'inner_build.py'
    shutil.copy(str(inner_py), str(build_script))
    # pytoml isn't in the build environment, so store the config as JSON
    with (packing_dir / 'config.json').open('w') as f:
        json.dump(config, f, indent=2)
        
    run(['flatpak', 'build', str(build_dir), '/usr/bin/python3',
            str(build_script)], cwd=str(project_dir), check=True)

def build_repo(config_path):
    with config_path.open() as f:
        config = pytoml.load(f)
    check_config(config)
    project_dir = config_path.parent
    packing_dir = project_dir / 'build' / 'flatpak'
    build_dir = packing_dir / 'build'
    try:
        shutil.rmtree(str(packing_dir))
    except FileNotFoundError:
        pass

    baseapp = 'org.pygame.BaseApp-py{}{}'.format(*config['python'].split('.'))
    flatpak('build-init', '--base', baseapp, str(build_dir), config['appid'],
            'org.freedesktop.Sdk', 'org.freedesktop.Platform', '1.4')
    call_build_script(project_dir, packing_dir, build_dir, config)
    flatpak('build-finish', str(build_dir), '--socket=x11', '--socket=pulseaudio', '--command=launch-game')

    repo_dir = project_dir / 'build' / 'flatpak-repo'
    flatpak('build-export', str(repo_dir), str(build_dir))
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
    
    config_path = Path(argv[1]).resolve()
    build_repo(config_path)

if __name__ == '__main__':
    main()
