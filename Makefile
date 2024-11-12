activate-pre-commit:
	just activate-pre-commit

all:
	just all

## Cleanup repository
clean:
	just clean

configure-git:
	just configure-git

## # Install development dependencies and pre-commit hook (env must be already activated)
develop:
	just develop

## Format / beautify code
format:
	just format

install-deps:
	just install-deps

## Lint / check typing
lint:
	just lint

## # Run python tests
test:
	just test

test-randomly:
	just test-randomly

## Cleanup harder
tidy:
	just tidy
