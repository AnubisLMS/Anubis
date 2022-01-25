<preview>

#### Anubis Proxy Vulnerability

At a time during peak load last semester (Fall 2021) a security vulnerability was found in the
service that proxies user requests to the Anubis Cloud IDEs. In this post we are going to explain
how it came about, and what we did to fix it.

</preview>

#### An overview of how connecting to your IDE works

Before we can explain how the vulnerability works, we'll need to cover how connecting
to an IDE works. The first thing that you must understand is that the IDE that you connect
to is nothing more than a nodejs server running a build of [theia](https://theia-ide.org/).
The server has an in cluster ip address.

At any given time we may have many IDE servers all running. We need some way of routing
incoming requests from users to the correct IDE server. We do this with the `theia-proxy` service.
This service is remarkably simple in its implementation. It is only a little over 200 lines of nodejs.
You can see the full implementation under 
[theia/proxy/index.js](https://github.com/AnubisLMS/Anubis/blob/master/theia/proxy/index.js). Pretty much the
entire purpose of the service can be summarised as this:

![](https://github.com/AnubisLMS/Anubis/raw/9bceb5a28a7eced88832c742113eee392e158c88/docs/design-tex/figures/theia-proxy-caching2.png)

The below diagram shows the full flow of logic for routing the requests through the service. Students
first connect to our edge router traefik, then to the proxy where their request is then routed to the
correct IDE.

![](https://github.com/AnubisLMS/Anubis/raw/fbcf815d831a16da127f9bbad5a6152262a2ee0f/docs/design-tex/figures/theia-proxy-caching-mmd.png)

> In this diagram there is only one proxy visible. In reality, due to the many limitations of running
> node servers there would actually be upwards of 15-20 instances of the proxy running.

The proxy sets a cookie when you first launch a session that it then uses when routing
further requests. This cooke only includes the id of the session. No other information.
This means that in order for the proxy to determine where the request should be routed 
(the in cluster ip address), it must pull that information from the database.

![](https://github.com/AnubisLMS/Anubis/raw/9bceb5a28a7eced88832c742113eee392e158c88/docs/design-tex/figures/theia-proxy-caching3.png)

#### The Vulnerability

The majority of time in any request to an Anubis API is nothing but IO. The server must request some 
data from the database and wait for the results - sometimes multiple times in a single request. 
Obviously when we design these systems we try to optimize the amount of requests to the database.
*This is where our the vulnerability comes from.*

At the time, the proxy service held an in-memory LRU cache per instance. This cache mapped the session id to the
in cluster ip address. The hope with this was that we could cache an in-cluster ip address once, then 
any subsequent request to that IDE that came through that proxy instance could skip the database round trip.
Something to note here is that when an IDE is started it gets an IP address from a limited pool of addresses.
This means that if an IDE is removed and a new one is created, the new one *could* get the same in-cluster 
address as the first one. The exact chance of this happening depends greatly on the settings of the k8s cluster.
The code below shows how we would skip requesting fresh information from the database if there was an entry in 
the in-memory cache.

![](https://github.com/AnubisLMS/Anubis/raw/9bceb5a28a7eced88832c742113eee392e158c88/docs/design-tex/figures/theia-proxy-caching1.png)

This situation where two IDEs that exist at different times is where the 
[race condition](https://en.wikipedia.org/wiki/Race_condition) can happen. Essentially if one person creates
then deletes and IDE, then a second person creates an IDE the first person would be able to connect to the
second IDE if their request is routed through a proxy instance that has their session id cached. This is
exactly what happened to two students last semester causing a great deal of confusion between the two people.

These two students reported their situation to their professor who reported it to us. We were able to find and
fix this bug within 30 or so minutes. As soon as I heard that this had happened I knew that the only place where such
a bug could occur would be the proxy service.

The moral of this story is that you should add a max-age to your cache entries, and think about these types of
abstract race conditions when designing scalable systems.
