build_dir = build/aliens

install-runtime:
	# Install the freedesktop 1.4 platform and SDK (runtime for building the app)
	flatpak remote-add --if-not-exists gnome http://sdk.gnome.org/repo/
	flatpak install gnome org.freedesktop.Sdk//1.4 || true
	flatpak install gnome org.freedesktop.Platform//1.4 || true

build-aliens.done: Makefile install-baseapp-py36.done
	# Main build steps - set up $(build_dir) and build the app in it.
	rm -rf $(build_dir)
	flatpak build-init --base=org.pygame.BaseApp-py36 $(build_dir) org.pygame.aliens \
				org.freedesktop.Sdk org.freedesktop.Platform 1.4
	flatpak build $(build_dir) make build-install
	flatpak build-finish $(build_dir) --socket=x11 --socket=pulseaudio --command=aliens
	touch $@

export-aliens.done: build-aliens.done
	# Export the build directory into a repo (the source for installation)
	flatpak build-export repo $(build_dir)
	touch $@

uninstall-aliens:
	flatpak --user uninstall org.pygame.aliens || true

install-aliens: uninstall-aliens repo-added.done
	flatpak --user install pg-test-repo org.pygame.aliens

build-baseapp.done:
	rm -rf baseapp
	flatpak-builder baseapp org.pygame.baseapp.json
	touch $@

export-baseapp.done:
	flatpak build-export repo baseapp
	touch $@

uninstall-baseapp:
	flatpak --user uninstall org.pygame.BaseApp || true

repo-added.done:
	flatpak --user remote-add --no-gpg-verify --if-not-exists pg-test-repo repo
	touch $@

# Ensure our repo is a remote, uninstall the application and install it again
install-baseapp.done: uninstall-baseapp export-baseapp.done repo-added.done
	flatpak --user install pg-test-repo org.pygame.BaseApp
	touch $@

build-baseapp-%.done: install-baseapp.done org.pygame.baseapp-%.json
	mkdir -p build
	rm -rf build/baseapp-$*
	flatpak-builder build/baseapp-$* org.pygame.baseapp-$*.json
	touch $@

export-baseapp-%.done: build-baseapp-%.done
	flatpak build-export repo build/baseapp-$*
	touch $@

uninstall-baseapp-%:
	flatpak --user uninstall org.pygame.BaseApp-$* || true

install-baseapp-%.done: uninstall-baseapp-% export-baseapp-%.done repo-added.done
	flatpak --user install pg-test-repo org.pygame.BaseApp-$*

all: install-baseapp-py34.done install-baseapp-py36.done

org.pygame.BaseApp%.bundle: export-baseapp%.done
	flatpak build-bundle repo $@ org.pygame.BaseApp$*

build-install:
	# This is run inside the build environment
	# It installs the files for the application into /app
	# mkdir /app/pypkgs
	# cp -r pygame /app/pypkgs
	# cp -r pygame-1.9.3.dist-info /app/pypkgs
	# mkdir /app/bin
	cp launch.py /app/bin/aliens
	mkdir -p /app/share/applications
	cp org.pygame.aliens.desktop /app/share/applications

	for size in 32 48 64 96 128 ; do \
		install -TD icons/pygame_snake_$$size.png \
			/app/share/icons/hicolor/$${size}x$${size}/apps/org.pygame.aliens.png ; \
	done
