# Assignements

This directory is where you should speicify per-assignemnt test scripts.

## Defining an assignment

The assignments should be comprised of several test scripts that match test-*.sh.
They will be run in lexicographical order at runtime.

An example `Dockerfile`:

```Dockerfile
# Import from the build image
FROM os3224-build

# copy over your tests
COPY test-0.sh test-0.sh
COPY test-1.sh test-1.sh
COPY test-2.sh test-2.sh
COPY test-3.sh test-3.sh
```
