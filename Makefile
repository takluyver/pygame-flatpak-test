build_dir = aliens

pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl:
	wget https://pypi.python.org/packages/a7/e6/1dd3d0d8d2c3fd3600edaa1f91d0fcbc2ad4b363985f89cb19098f7cb99e/pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl

pygame/__init__.py: pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl
	unzip $<
	touch pygame/__init__.py  # Update the timestamp for make

# Download and unpack the pygame wheel for Python 3.4
# (3.4 is the Python 3 version available in the freedesktop 1.4 runtime)
get-pkg: pygame/__init__.py 

build-dir: get-pkg
	# Main build steps - set up $(build_dir) and build the app in it.
	rm -rf $(build_dir)
	flatpak build-init $(build_dir) org.pygame.aliens org.freedesktop.Sdk org.freedesktop.Platform 1.4
	flatpak build $(build_dir) make build-install
	flatpak build-finish $(build_dir) --socket=x11 --socket=pulseaudio --command=aliens

export:
	# Export the build directory into a repo (the source for installation)
	flatpak build-export repo $(build_dir)

reinstall:
	# Ensure our repo is a remote, uninstall the application and install it again
	flatpak --user remote-add --no-gpg-verify --if-not-exists pg-test-repo repo
	flatpak --user uninstall org.pygame.aliens
	flatpak --user install pg-test-repo org.pygame.aliens

build-install:
	# This is run inside the build environment
	# It installs the files for the application into /app
	mkdir /app/pypkgs
	cp -r pygame /app/pypkgs
	cp -r pygame-1.9.3.dist-info /app/pypkgs
	mkdir /app/bin
	cp launch.py /app/bin/aliens
