# Deploy

I would recomend that before attempting to deploy, familiarise yourself with the different 
[services](services.md) that make up Anubis.

## Server Resource Recomendations

The scale at which you deploy Anubis is configurable, but it still is a hefty cluster of services that
wont work on a raspberry pi. I would recommend these as the *minimum* specs the server Anubis runs on 
should have.

```
CPU:       4 Cores 8 Threads
RAM:       8 GB
Storage:  32 GB (free after OS and other services)
```

## Dependencies

The only thing you will need to have installed on the server is the latest version of [docker](https://docs.docker.com/), [docker-compose](https://docs.docker.com/compose/) and [jq](https://stedolan.github.io/jq/).

- A trick for installing docker very easily on any system is to run this: `curl https://get.docker.com/ | sh`.
- If you are deploying on ubuntu (or any debian distro for that matter), you will want to `sudo pip3 install docker-compose` instead of apt installing it. The debian package for docker-compose is way too out of date to work.

Assuming you are on a debian distro (ubuntu-server or some such), you can run these commands to get up and running.
You will need to restart for some of the docker stuff to take effect.

```shell script
# Install docker and docker-compose
curl https://get.docker.com/ | sh
sudo pip3 install docker-compose

# Enable docker on reboot, and start docker engine
sudo systemctl enable docker
sudo systemctl start docker

# Add current user to the docker group
sudo usermod -aG docker ${USER}

# Get jq installed
sudo apt update && sudo apt upgrade && sudo apt install -y jq 
```

## Configuration

Most of the configuration for deploying Anubis is made to be done through the environment variables. My 
recomendation is that you use a `.env` file for holding your configuration on the server. You can put a file 
called `.env` at the root of the project directory with `key=value` on each line. A sample `.env` file would 
look like this:

```
ACME_EMAIL=john.doe@email.com
MYSQL_ROOT_PASSWORD=password
AUTH=root:$2y$05$2VCT7LSzWh7ULSHtQHHxBeTu89WoE5W995MDXc5XVygYCqI3Rn8am
DOMAIN=localhost
BOMBLAB_DOMAIN=bombs.localhost
```

Please take care to not commit any of these values to the repo. They should be kept private.

### Variables:
- ACME_EMAIL - email for let encrypt cert
- MYSQL_ROOT_PASSWORD - root password for database
- AUTH - http basic auth for traefik and private api
- DOMAIN - dns domain that the server resides on
- BOMBLAB_DOMAIN - dns domain for bomblab

The AUTH environment variable is used to set the username password for all the services that are locked 
behind http basic auth. Those services include the private section of the api, the cli, and kibana. To generate
the AUTH environment variable, we can use a simple docker command:

```
docker run -it httpd htpasswd -Bbn '<username>' '<password>' 
```

This will print out a username password hash that you can use for the AUTH environment variable.

