# Anubis Development Guide

<p align="center">
  <a href="https://anubis.osiris.services/">
    <img
      alt="Anubis"
      src="https://raw.githubusercontent.com/GusSand/Anubis/ADD-contribution-guidelines/docs/img/anubis-icon-1.png"
      width="400"
    />
  </a>
</p>

# Table of contents
* [Project layout](#project-layout)
* [Foreword](#foreword)
* [startup links](#startup-links)
* [mindebug environment](#mindebug-environment)
* [debug environment](#debug-environment)
* [mkdebug environment](#mkdebug-environment)
* [Further](#further)

## Project layout

- [api](../api) is where the flask api lives
- [web](../web) is where the reactjs website lives
- [theia](../theia) is where the different components that make up the Anubis Cloud IDEs live
- [k8s](../k8s) is where the kubernetes definitions for things live. This includes the 
  Anubis helm chart, and prod provisioning scripts.

## Foreword

Anubis is a very big system. For this reason there are three separate debug environments. Each one
is a little closer to fully simulating prod. There are certain things that can only be done in 
one development environment. The three environments are called:

1. mindebug - natively run api and website
2. debug - launch services through docker-compose in containers  
3. mkdebug - launch services in minikube cluster

Each of these environments are meant to be launched from the top level Makefile. At the end of
starting each environment, a list of what we call [startup links](#startup-links) will be printed.

## startup links

The startup links are meant to make seeding the database, and getting logged in while debugging fast 
and easy. The links do not change between debug environments (except with mindebug being on 
port 3000).

The startup links for the `debug` and `mkdebug` are:

```
seed: http://localhost/api/admin/seed/
auth: http://localhost/api/admin/auth/token/superuser
auth: http://localhost/api/admin/auth/token/professor
auth: http://localhost/api/admin/auth/token/ta
auth: http://localhost/api/admin/auth/token/student
site: http://localhost/
```

The startup links for `mindebug` are:

```
seed: http://localhost:3000/api/admin/seed/
auth: http://localhost:3000/api/admin/auth/token/superuser
auth: http://localhost:3000/api/admin/auth/token/professor
auth: http://localhost:3000/api/admin/auth/token/ta
auth: http://localhost:3000/api/admin/auth/token/student
site: http://localhost:3000/
```

When you click on the seed link, the api will run a [seed function](https://github.com/GusSand/Anubis/blob/master/api/anubis/rpc/seed.py#L33)
that will initialize the database with some generated assignments, submissions and users of different permission levels.

There are 4 main permission levels (which are course specific). The seed endpoint will create a user for
the generated course at each permission level. Clicking on any of the auth links that are printed will set
a token cookie logging you in as that user. If you are having issues logging in with the auth links,
you should clear your cookies and try again. The seed also may take a couple of seconds to run. If you
click the seed link, then an auth link before the seed has had a chance to create that user it may say 
that the user does not exist.

The last site link is just for convenience, so you can open a new tab with the website after clicking your other
startup links.

So to recap, after the debug services have started you can use the startup links to quickly seed (or re-seed) data and
log in as a user of a specific permission level. The order of links that the maintainers use is first the seed, then
the superuser link, then the site link. That will initialize the database with generated data, log us in as a superuser,
then open the website.

## mindebug environment

This is what will work for most people. If you are on OSX, Windows or have a potato computer you should start with this.
The other debug environments use lots of docker containers, which just do not work well on OSX or
Windows. This debug environment uses the least amount of resources by far. There are several places 
that this environment differs from prod (we will get into that later).

You will need these things installed:

- make
- python 3.7 or above
- virtualenv 
- nodejs 
- yarn


To start off `mindebug` first run this at the top of the repo:

```shell
make mindebug
```

This command will initialize the python virtual environment for the api and the node_modules for the web. It
will then print out the mindebug startup links. Then you need to run the api and website yourself separately. 
We launch these separately so that the api can be run in your debugger of choice.

To start the api, run this from the top of the repo:

```shell
# Same as running `make run` or `env MINDEBUG=1 DEBUG=1 ./venv/bin/python3 dev.py` from the api directory
# This will start the flask server in MINDEBUG mode
make -C api run
```

> _Alternatively you can run api/dev.py from your IDE if it has a fancy debugger (like pycharm!)_

Then to start the web, run this from the web directory:

```shell
# This will start the create-react-app dev server with api proxy
yarn run start
```

Things that will not work with `mindebug` are:

- Anything that interacts with the kubernetes API
- Cloud IDEs
- Submission pipelines
- Most everything that involves RPC
- API tests will not work
- Database migrations (we skirt mariadb migrations to use sqlite instead)
- Things that use libmagic (file upload specifically use this)

One last thing to note with the mindebug environment is that rpc job will be called synchronously where normally they
would be called asynchronously. This is because the library we use for rpc [python-rq](https://python-rq.org/) requires
a redis backend. Since there is no such service in the mindebug environment, rpc calls are called when they would 
normally be enqueued.

Now you can hack Anubis

## debug environment

If you are on linux and have at least 2-6 GiB of memory to spare, this option is probably best for you. This is much closer
to simulating prod than the mindebug configuration. This is the debug configuration that most of Anubis has been written
with.

You will need these things installed:

- docker
- docker-compose 3.7 or above

All you need to do to start all the debug services is run this at the top of the repo:

```shell
# This will start the flask api, web server, rpc workers, traefik, mariadb and redis
make debug
```

In this setup we run the api and web in DEBUG mode. The containers that are launched will also have the proper
places in the repo mounted. So changes to code will be picked up and services will restart.

Things that will not work with `debug` are:

- Anything that interacts with the kubernetes API
- Cloud IDEs
- Submission pipelines

## mkdebug environment

If you have 4-8 GiB of memory to spare, and want to specifically develop the Cloud IDEs or Submission pipelines then
this is the environment for you. This environment is as close to prod as you can get. mkdebug is really only meant for
developing things that directly interact with the kubernetes api. Unlike the more simple docker-compose setup in the 
debug environment, there is no live edit updating here. You will need to rebuild and restart services when you have 
a change.

You will need these things installed:

- docker
- minikube
- helm 3
- kubectl

All you need to do to start all the debug services is run this at the top of the repo:

```shell
# This will provision a new minikube cluster with Anubis
# !Warning! this will delete any existing minikube cluster
make mkdebug
```

There is also a special script that is called when provisioning the minikube cluster. The purpose of it
is to place any kubernetes secret create commands that you may need. Place that script at `k8s/debug/init-secrets.sh`.
The file will be gitignored, but be extra sure you do not commit it on accident.

The startup links for the minikube debug environment work exactly the same as with the debug and mindebug environments.
When you have a change that you want to push to the minikube cluster you can run the `./k8s/debug/restart.sh` script. It
will rebuild and restart common services (like api, web, rpc workers). You can also get a kubernetes dashboard with
`minikube dashboard`.

The script that provisions minikube will also set the cluster resources to half your machines cpu and memory resources.

## Further

- Checkout the [project board](https://github.com/GusSand/Anubis/projects/1) to see what you can 
contribute
- Checkout the [design doc](./README.md) to see a detailed explanation of the internals of Anubis