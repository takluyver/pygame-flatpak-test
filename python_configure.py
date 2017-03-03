#!/usr/bin/python3
import sys

MAKEFILE_TEMPLATE = '''
all:
	echo "Doing nothing at this step"

install:
	{environment} {python} -m pip install --ignore-installed . --prefix={prefix}
'''

prefix = '/app'
python = '/app/bin/python3'
c_flags = ''

for arg in sys.argv[1:]:
	if arg.startswith('--prefix='):
		prefix = arg[len('--prefix='):]
	elif arg.startswith('CFLAGS='):
		c_flags = arg[len('CFLAGS='):]
	elif arg.startswith(('--libdir=', 'CXXFLAGS=')):
		pass
	else:
		sys.exit("Unknown arg: %r" % arg)

with open('Makefile', 'w') as f:
	if c_flags:
		environment = 'CFLAGS="%s"' % c_flags
	else:
		environment = ''
	f.write(MAKEFILE_TEMPLATE.format(
		environment=environment,
		prefix=prefix,
		python=python,
	))
