BUILDDIR = _build

.PHONY: clean-pyc clean-build docs clean

# Setup up the man page directories.
PREFIX ?= /usr/local
MANDIR := $(abspath $(PREFIX)/man)
# NOTE: `make` appends MAKEFILE_LIST with paths as it reads makefiles.
#   https://ftp.gnu.org/old-gnu/Manuals/make/html_node/make_17.html
# So this is the path to this Makefile from the user's working directory.
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
# This is the path to the directory wherein this Makefile is located,
#   in case the user is running make from another directory.
mkfile_base := $(dir $(mkfile_path))
# USAGE: To wire man pages under the user's local directory, try:
#   PREFIX=~/.local make man-link
#   man dob

# DEV: Set BROWSER environ to pick your browser, otherwise webbrowser ignores
# the system default and goes through its list, which starts with 'mozilla'.
# E.g.,
#
#   BROWSER=chromium-browser make view-coverage
#
# Alternatively, one could be less distro-friendly and leverage sensible-utils, e.g.,
#
#   PYBROWSER := sensible-browser
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
# NOTE: Cannot name BROWSER, else overrides environ of same name.
PYBROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "Please choose a target for make:"
	@echo
	@echo " Installing and Packaging"
	@echo " ------------------------"
	@echo "   install         install the package to the active Python's site-packages"
	@echo "   develop         install (or update) all packages required for development"
	@echo "   dist            package"
	@echo "   release         package and upload a release"
	@echo
	@echo " Developing and Testing"
	@echo " ----------------------"
	@echo "   clean           remove all build, test, coverage and Python artifacts"
	@echo "   clean-build     remove build artifacts"
	@echo "   clean-docs      remove docs from the build"
	@echo "   clean-pyc       remove Python file artifacts"
	@echo "   clean-test      remove test and coverage artifacts"
	@echo "   cloc            \"count lines of code\""
	@echo "   coverage        check code coverage quickly with the default Python"
	@echo "   coverage-html   generate HTML coverage reference for every source file"
	@echo "   view-coverage   open coverage docs in new tab (set BROWSER to specify app)"
	@echo "   docs            generate Sphinx HTML documentation, including API docs"
	@echo "   isort           run isort; sorts and groups imports in every module"
	@echo "   lint            check style with flake8"
	@echo "   man-compile     compile manual page"
	@echo "   man-install     install manual page"
	@echo "   man-uninstall   uninstall manual page"
	@echo "   man-link        create man page symlink under ~/.local/man/man1"
	@echo "   man-unlink      remove man page symlink"
	@echo "   test            run tests quickly with the default Python"
	@echo "   test-all        run tests on every Python version with tox"
	@echo "   test-one        run tests until the first one fails"

clean: clean-build clean-pyc clean-test

clean-build:
	/bin/rm -fr build/
	/bin/rm -fr dist/
	/bin/rm -fr .eggs/
	find . -name '*.egg-info' -exec /bin/rm -fr {} +
	find . -name '*.egg' -exec /bin/rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec /bin/rm -f {} +
	find . -name '*.pyo' -exec /bin/rm -f {} +
	find . -name '*~' -exec /bin/rm -f {} +
	find . -name '__pycache__' -exec /bin/rm -fr {} +

clean-docs:
	$(MAKE) -C docs clean BUILDDIR=$(BUILDDIR)

clean-test:
	/bin/rm -fr .tox/
	/bin/rm -f .coverage
	/bin/rm -fr htmlcov/

develop:
	pip install -U pip setuptools wheel
	pip install -U -r requirements/dev.pip
	pip install -U -e .

lint:
	flake8 setup.py dob/ tests/

test:
	@echo "Use the PYTEST_ADDOPTS environment variable to add extra command line options."
	py.test $(TEST_ARGS) tests/

test-debug: test-local quickfix

test-local:
	# (lb) The pipe to tee, `| tee`, masks the return code from py.test. I.e., on its own,
	# `py.test | tee` will always return true (0), regardless of py.test's exit code. As
	# such, don't run this task from Travis CI. Or, if you do, change shells and set pipefail.
	# E.g., at the top of the file, include:
	#     SHELL = /bin/bash -o pipefail
	# And then if any command along the pipeline fails, the whole command fails.
	# Note: Using `set -o` or testing PIPESTATUS did not succeed for me, e.g.,
	#     SHELL = /bin/bash
	#     test-local:
	#       # Tried this; didn't work:
	#       set -o pipefail
	#       py.test | tee
	#       # Tried this; didn't work:
	#       py.test | tee; test ${PIPESTATUS[0]} = 0
	#       # nor $${PIPESTATUS[0]}, $(...), or $$(...).
	py.test $(TEST_ARGS) tests/ | tee .make.out

test-all:
	tox

test-one:
	# You can also obviously: TEST_ARGS=-x make test
	# See also, e.g.,:
	#   py.test --pdb -vv -k test_function tests/
	py.test $(TEST_ARGS) -x tests/

coverage:
	coverage run -m pytest $(TEST_ARGS) tests
	coverage report

coverage-html: coverage view-coverage
	coverage html

view-coverage:
	$(PYBROWSER) htmlcov/index.html

quickfix:
	# Convert partial paths to full paths, for Vim quickfix.
	sed -r "s#^([^ ]+:[0-9]+:)#$(shell pwd)/\1#" -i .make.out
	# Convert double-colons in messages (not file:line:s) -- at least
	# those we can identify -- to avoid quickfix errorformat hits.
	sed -r "s#^(.* .*):([0-9]+):#\1∷\2:#" -i .make.out

docs:
	/bin/rm -f docs/dob.rst
	/bin/rm -f docs/modules.rst
	sphinx-apidoc -o docs/ dob
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(PYBROWSER) docs/_build/html/index.html

isort:
	isort --recursive setup.py dob/ tests/
	# DX: End files with blank line.
	git ls-files | while read file; do \
		if [ -n "$$(tail -n1 $$file)" ]; then \
			echo "Blanking: $$file"; \
			echo >> $$file; \
		else \
			echo "DecentOk: $$file"; \
		fi \
	done
	@echo "ça va"

servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean
	python setup.py sdist bdist_wheel
	twine upload -r pypi -s dist/*

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install

man-compile:
	@mandb > /dev/null 2>&1

man-install:
	@find man/ \
		-iname "*.[0-9]" \
		-exec /bin/bash -c \
			"echo {} \
				| /bin/sed -r 's~(.*)([0-9])$$~install \1\2 $(MANDIR)/man\2/~' \
				| source /dev/stdin" \;

man-uninstall:
	@cd $(mkfile_base)/man \
		&& find . \
			-iname "*.[0-9]" \
			-exec /bin/bash -c \
				"echo {} \
					| /bin/sed -r 's~(.*)([0-9])$$~[[ -f $(MANDIR)/man\2/\1\2 \&\& ! -h $(MANDIR)/man\2/\1\2 ]] \&\& /bin/rm $(MANDIR)/man\2/\1\2 || true~' \
					| source /dev/stdin" \;

man-link:
	@find man/ \
		-iname "*.[0-9]" \
		-exec /bin/bash -c \
			"echo {} \
				| /bin/sed -r 's~(.*)([0-9])$$~/bin/ln -sf \$$(realpath $(mkfile_base)/\1\2) $(MANDIR)/man\2/~' \
				| source /dev/stdin" \;

man-unlink:
	@cd $(mkfile_base)/man \
		&& find . \
			-iname "*.[0-9]" \
			-exec /bin/bash -c \
				"echo {} \
					| /bin/sed -r 's~(.*)([0-9])$$~[[ -h $(MANDIR)/man\2/\1\2 ]] \&\& /bin/rm $(MANDIR)/man\2/\1\2 || true~' \
					| source /dev/stdin" \;

CLOC := $(shell command -v cloc 2> /dev/null)

cloc:
ifndef CLOC
	$(error "Please install cloc from: https://github.com/AlDanial/cloc")
endif
	@cloc --exclude-dir=.git,_build,dob.egg-info,.pytest_cache .

# vim:tw=0:ts=2:sw=2:noet:ft=make:

