# Services

Everything is now dockerized. By having everything run in docker containers
we can have a significantly more eligant deploy, with more control over 
load balancing. There are 6 main micro services that we are running.


## Traefik

![alt](https://docs.traefik.io/assets/img/traefik-architecture.png)

[Traefik](https://containo.us/traefik/) is an edge router on steriods. 
It does the same thing nginx does, but much much better. If you have not 
used it before, it is a tool you will want to learn because it is seriously OP.

The main purpose of traefik is having multiple domains be pointed at a single ip address,
so we can have everything on one server, load balancing, and easy ssl.

#### Routing
Traefik is what listens on the http and https ports. When a request comes in,
it is forwarded to a container based on routing rules we define. This may
sound scary, but it really isn't. The only type of routing rule we used for 
this deploy was the Host rule. This means what domain the request is intended
for. The rules are defined using docker labels that are defined in `bomblab/docker-compose.yml`.

For example, if a request comes in for bombs.nyu.cool, traefik will see that
we have a bombs service with rules that match that request and forward it along.

#### Load Balancing
Traefik also handles load balancing for us. If we use docker-compose to scale a service up
to multiple containers, traefik will automatically do round robin load balancing between those 
containers.

#### SSL
Traefik will also handle getting letencrypt certificates for us, and automatically apply
ssl to traffic if we simply specify we want tls.


## MariaDB database

I wanted to have events be handled in a database rather than on the filesystem, so I've
added a MariaDB service. This instance only has one database, with one table. That table
is called Submission, and it holds all the reported explosions and defusions that are reported
from the [Reportd](#Reportd) service.

## Reportd

This service does two things. Every 30 seconds, it will pull all the events out of the Submission table
of the [MariaDB](#mariadb-database) database into the `bomblab/log.txt` file. After that it will run the 
`bomblab/bomblab-update.pl` script that will process all the events, verifying solutions, calculating scores
and regenerate the `bomblab/bomblab-scoreboard.html` file.

## Requestd

This micro service handles serving the `bomblab/bomblab-scoreboard.html` file and generating the bomblabs for students.
I decided to completly rewrite this entire service to be able to handle way more clients. Before the rewrite, this 
service was single threaded. This needed to change, so I basically just reimplemented all the perl logic in flask
to allow for gunicorn to be used so we could scale workers. The only main difference is that when a bomblab needs to
be generated, it will copy the `bomblab/src` directory to `/tmp/src<bombid>`, build the bomblab there, then copy the
results to `bomblab/bombs/bomb<bombid>`. This is so that we dont have a race condition when compiling the lab. If
we didn't have a seperate build directory for each worker building a bomblab, different threads could easily overwrite
while compiling. This change is what allows us to be able to compile more than one lab at a time.

## Resultd

This service was another single threaded http server that was very much in need of a rewrite. I rewrote this simple
api in flask, and am using gunicorn to scale the workers. It is a very simple api that the bomblabs report to when 
an event occurs. The bomblabs will report when there is a defusion or explosion. When that occurs, it will send a 
get request to this service with parameters descripting the event. All this service does is take those parameters and 
insert them into the [MariaDB](#mariadb-database) database.

## Bombs

The TAs need a way to access the scores, event log, and bomblab solutions and source in order to help student with 
debugging and whatnot. This service is a super simple http file server that has a couple of files and directories
mounted in it. This http file server is locked behind [http basic auth](https://en.wikipedia.org/wiki/Basic_access_authentication).
You can read more about configuting that authentication in [ENV.md](ENV.md#bomb_auth).
