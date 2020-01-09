# Build image

This Dockerfile should be built, so that the workers can run build jobs. 
The container should take a repo url, clone it then build and test.
The results of the test, along with any errors or failures should be reported
back to the api.
