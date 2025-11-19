SIM?=icarus

default: verilog vhdl

verilog:
	cd tests/test_basic ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_basic_64 ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slave ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slave_noenable ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slave_noprot ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slave_noslverr ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slave_nostrb ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_slverr ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_multi_device ; make clean sim WAVES=0 && ../rtlflo/combine_results.py
	cd tests/test_poll ; make clean sim WAVES=0 && ../rtlflo/combine_results.py

vhdl:
	# VHDL tests would go here if any are added

lint:
	pyflakes cocotbext
	ruff check cocotbext

mypy:
	mypy cocotbext

format:
	black cocotbext

checks: format lint mypy

dist:
	rm -rf MANIFEST
	rm -rf CHANGELOG.txt
	python setup.py sdist

pre-commit:
	pre-commit run --all-files

GIT_TAG?=0.0.1
VERSION_FILE?=`find . -name version.py`
release:
	echo "Release v${GIT_TAG}"
# 	@grep -Po '\d\.\d\.\d' cocotbext/jtag/version.py
	git tag v${GIT_TAG} || { echo "make release GIT_TAG=0.0.5"; git tag ; exit 1; }
	echo "__version__ = \"${GIT_TAG}\"" > ${VERSION_FILE}
	git add ${VERSION_FILE}
	git commit --allow-empty -m "Update to version ${GIT_TAG}"
	git tag -f v${GIT_TAG}
	git push && git push --tags

git_align:
	mkdir -p repos
	cd repos ; git clone git@github.com:daxzio/rtlflo.git 2> /dev/null || (cd rtlflo ; git pull)
	rsync -artu --exclude .git repos/rtlflo/ tests/rtlflo
	rsync -artu --exclude .git tests/rtlflo/ repos/rtlflo
