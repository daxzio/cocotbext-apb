SIM?=icarus

default:
	cd tests/test001 ; make clean sim ; ../../rtlflo/combine_results.py
	cd tests/test002 ; make clean sim ; ../../rtlflo/combine_results.py
	cd tests/test003 ; make clean sim ; ../../rtlflo/combine_results.py
	cd tests/hazard3 ; make clean sim ; ../../rtlflo/combine_results.py

lint:
	pyflakes cocotbext

mypy:
	mypy cocotbext

format:
	black cocotbext

dist:
	rm -rf MANIFEST 
	rm -rf CHANGELOG.txt
	python setup.py sdist

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

