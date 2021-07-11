# Continuous Image Puller

This is the service that pulls the large images on anubis to nodes every few seconds. This assures that images like those for the cloud ides will be available as soon as possible.

Without this service every time the cluster adds a new node, the large images would only get pulled when pods are scheduled. By continuously pulling images, we may be able to speed up the "provisioning" of new nodes.

*why is this in go?*

Yeah, great question. If this didn't need to be in golang, believe me it would not. The docker image for the image puller needs to be as small as possible. The one thing go is actually good at is small binaries, and final images. The docker image for the current puller is `8.27MB` compared to `443MB` for the regular python api. By keeping this image small we can insure that this service can get started quickly.
