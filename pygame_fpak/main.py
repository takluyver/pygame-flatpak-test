import json
from pathlib import Path
import pytoml
import shutil
from subprocess import run, PIPE
import sys

def flatpak(*args):
    run(('flatpak',) + args, check=True)

class PkgRef:
    def __init__(self, name, arch, branch):
        self.name = name
        self.arch = arch
        self.branch = branch

def list_installed():
    res = run(['flatpak', 'list'], check=True, stdout=PIPE)
    lines = res.stdout.decode('utf-8', 'replace').splitlines()
    for line in lines:
        yield PkgRef(*line.split()[0].split('/'))

def get_baseapp(baseapp):
    installed_names = [p.name for p in list_installed()]
    if baseapp in installed_names:
        return
    flatpak('--user', 'remote-add', '--if-not-exists', '--from',
    'pygame-bases', 'https://takluyver.github.io/pygame-flatpak-test/pgbase.flatpakrepo')
    flatpak('--user', 'install', 'pygame-bases', baseapp)

inner_py = Path(__file__).parent / 'inner.py'


class Flatpacker:
    def __init__(self, config_path):
        self.config_path = config_path
        with config_path.open() as f:
            self.config = pytoml.load(f)
        check_config(self.config)
        self.project_dir = config_path.parent
        self.packing_dir = self.project_dir / 'build' / 'flatpak'
        self.build_dir = self.packing_dir / 'build'
        self.repo_dir = self.project_dir / 'build' / 'flatpak-repo'

    def call_build_script(self):
        """Copy the build script and call it inside the flatpak build.
        """
        print('Running build script...')
        build_script = self.packing_dir / 'inner_build.py'
        shutil.copy(str(inner_py), str(build_script))
        # pytoml isn't in the build environment, so store the config as JSON
        with (self.packing_dir / 'config.json').open('w') as f:
            json.dump(self.config, f, indent=2)
            
        run(['flatpak', 'build', str(self.build_dir), '/usr/bin/python3',
                str(build_script)], cwd=str(self.project_dir), check=True)

    def build(self):
        try:
            shutil.rmtree(str(self.packing_dir))
        except FileNotFoundError:
            pass

        baseapp = 'org.pygame.BaseApp-py{}{}'.format(*self.config['python'].split('.'))
        get_baseapp(baseapp)
        flatpak('build-init', '--base', baseapp, str(self.build_dir), self.config['appid'],
                'org.freedesktop.Sdk', 'org.freedesktop.Platform', '1.4')
        self.call_build_script()
        flatpak('build-finish', str(self.build_dir), '--socket=x11',
                '--socket=pulseaudio', '--command=launch-game')

        flatpak('build-export', str(self.repo_dir), str(self.build_dir))

    def info(self):
        repo_rel = self.repo_dir.relative_to(Path.cwd())
        print()
        print("Built to repo in {}".format(repo_rel))
        print("To distribute, see http://docs.flatpak.org/en/latest/distributing-applications.html")
        print("Make a single file bundle:")
        print("  flatpak build-bundle {repo} {appid}.bundle {appid}"
                .format(repo=repo_rel, appid=self.config['appid']))
        print("Install and test:")
        print("  flatpak --user remote-add --no-gpg-verify --if-not-exists {}-origin {}"
                .format(self.config['appid'], repo_rel))
        print("  flatpak --user install {appid}-origin {appid}"
                .format(appid=self.config['appid']))

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
    packer = Flatpacker(config_path)
    packer.build()
    packer.info()

if __name__ == '__main__':
    main()
