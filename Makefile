.PHONY: pypi-test-publish

pypi-test-publish:
	rm -rf dist/*
	sed -i "s/version = \"[^\"]*\"/version = \"$(shell date +%Y.%m.%d.%H%M%S)\"/" pyproject.toml
	uv build
	uv publish --token "$$TEST_PYPI_TOKEN" --publish-url https://test.pypi.org/legacy/
