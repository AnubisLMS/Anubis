# Assignements

This directory is where you should speicify per-assignemnt test scripts.

## Defining an assignment

The assignments should be comprised of several test scripts that match test-*.sh.
They will be run in lexicographical order at runtime.

An example `Dockerfile`:

```Dockerfile
# Import from the build image
FROM os3224-assignment-base

# copy over your tests
COPY test-0.py test-0.py
COPY test-1.py test-1.py
COPY test-2.py test-2.py
COPY test-3.py test-3.py
```
