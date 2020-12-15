FROM alpine:latest

# Create out directory
VOLUME /out

# Only dependency is git
RUN apk --update --no-cache add git

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh

# Set entrypoint
CMD /entrypoint.sh

