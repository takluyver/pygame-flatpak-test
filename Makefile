build_dir = aliens

pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl:
	wget https://pypi.python.org/packages/a7/e6/1dd3d0d8d2c3fd3600edaa1f91d0fcbc2ad4b363985f89cb19098f7cb99e/pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl

pygame/__init__.py: pygame-1.9.3-cp34-cp34m-manylinux1_x86_64.whl
	unzip $<
	touch pygame/__init__.py  # Update the timestamp for make

# Download and unpack the pygame wheel for Python 3.4
# (3.4 is the Python 3 version available in the freedesktop 1.4 runtime)
get-pkg: pygame/__init__.py 

install-runtime:
	# Install the freedesktop 1.4 platform and SDK (runtime for building the app)
	flatpak remote-add --if-not-exists gnome http://sdk.gnome.org/repo/
	flatpak install gnome org.freedesktop.Sdk//1.4 || true
	flatpak install gnome org.freedesktop.Platform//1.4 || true

build-dir: get-pkg
	# Main build steps - set up $(build_dir) and build the app in it.
	rm -rf $(build_dir)
	flatpak build-init $(build_dir) org.pygame.aliens org.freedesktop.Sdk org.freedesktop.Platform 1.4
	flatpak build $(build_dir) make build-install
	flatpak build-finish $(build_dir) --socket=x11 --socket=pulseaudio --command=aliens

export:
	# Export the build directory into a repo (the source for installation)
	flatpak build-export repo $(build_dir)

uninstall:
	flatpak --user uninstall org.pygame.aliens || true

reinstall: uninstall
	# Ensure our repo is a remote, uninstall the application and install it again
	flatpak --user remote-add --no-gpg-verify --if-not-exists pg-test-repo repo
	flatpak --user install pg-test-repo org.pygame.aliens

build-baseapp:
	rm -rf baseapp
	flatpak-builder baseapp org.pygame.baseapp.json

build-install:
	# This is run inside the build environment
	# It installs the files for the application into /app
	mkdir /app/pypkgs
	cp -r pygame /app/pypkgs
	cp -r pygame-1.9.3.dist-info /app/pypkgs
	mkdir /app/bin
	cp launch.py /app/bin/aliens
	mkdir -p /app/share/applications
	cp org.pygame.aliens.desktop /app/share/applications

	for size in 32 48 64 96 128 ; do \
		install -TD icons/pygame_snake_$$size.png \
			/app/share/icons/hicolor/$${size}x$${size}/apps/org.pygame.aliens.png ; \
	done
