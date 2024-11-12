all: lint test

#
# Setup
#

# # Install development dependencies and pre-commit hook (env must be already activated)
develop: install-deps activate-pre-commit configure-git

install-deps:
    @echo "--> Installing dependencies"
    uv sync

activate-pre-commit:
    @echo "--> Activating pre-commit hook"
    pre-commit install

configure-git:
    @echo "--> Configuring git"
    git config branch.autosetuprebase always

#
# testing & checking
#

# # Run python tests
test:
    @echo "--> Running Python tests"
    pytest -x -p no:randomly
    @echo ""

test-randomly:
    @echo "--> Running Python tests in random order"
    pytest

# Lint / check typing
lint:
    ruff check src tests

#
# Formatting
#

# Format / beautify code
format:
    ruff format src tests


# Cleanup repository
clean:
    adt clean
    rm -f **/*.pyc
    find . -type d -empty -delete
    rm -rf *.egg-info *.egg .coverage .eggs .cache .mypy_cache .pyre \
    	.pytest_cache .pytest .DS_Store  docs/_build docs/cache docs/tmp \
    	dist build pip-wheel-metadata junit-*.xml htmlcov coverage.xml

# Cleanup harder
tidy: clean
    rm -rf .nox
    rm -rf node_modules
    rm -rf instance
