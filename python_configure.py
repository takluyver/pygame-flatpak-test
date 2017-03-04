#!/usr/bin/python3
import os
import re
import subprocess
import sys

MAKEFILE_TEMPLATE = '''
all:
	echo "Doing nothing at this step"

install:
	{environment} {pip} install --ignore-installed . {prefix_arg}
'''

prefix = '/app'
pip = os.environ['PIP_PATH']
c_flags = ''

def get_pip_version():
	out = subprocess.check_output([pip, '--version']).decode('ascii', 'replace')
	print('pip version:', out)
	m = re.match('pip (\d+(.\d+)*)', out)
	if not m:
		raise ValueError('Failed to get version number from %r' % out)
	return tuple(map(int, m.group(1).split('.')))

for arg in sys.argv[1:]:
	if arg.startswith('--prefix='):
		prefix = arg[len('--prefix='):]
	elif arg.startswith('CFLAGS='):
		c_flags = arg[len('CFLAGS='):]
	elif arg.startswith(('--libdir=', 'CXXFLAGS=')):
		pass
	else:
		sys.exit("Unknown arg: %r" % arg)

if get_pip_version() >= (8,):
	prefix_arg = '--prefix="%s"' % prefix
else:
	# This works with sdists, but won't affect installing wheels
	prefix_arg = '--install-option="--prefix=%s"' % prefix

with open('Makefile', 'w') as f:
	if c_flags:
		environment = 'CFLAGS="%s"' % c_flags
	else:
		environment = ''
	f.write(MAKEFILE_TEMPLATE.format(
		environment=environment,
		prefix_arg=prefix_arg,
		pip=pip,
	))
