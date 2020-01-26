# Anubis

## Deploy
You should just need to configure a few environment vars to get this up and running.
The easiest way to store these would be a `.env` file.

- ACME_EMAIL - email for let encrypt cert
- MYSQL_ROOT_PASSWORD - root password for database
- AUTH - http basic auth for traefik and private api
- DOMAIN - dns domain that the server resides on

#### Generating AUTH
To generate the AUTH environment variable you can just use: 

```bash
docker run -it httpd htpasswd -Bbn '<username>' '<password>' 
```

## Debugging
This project requires envrionment variables to be deployed. You can store those in
a `.env` file to keep things simple. Here is an example `.env` file for debugging.

*DO NOT USE THIS ENV IN PROD*

```
ACME_EMAIL=john.doe@email.com
MYSQL_ROOT_PASSWORD=password
AUTH='root:$2y$05$2VCT7LSzWh7ULSHtQHHxBeTu89WoE5W995MDXc5XVygYCqI3Rn8am'
DOMAIN=localhost
```

This debug environment will let you connect to the api on https://localhost/.
The creds for all http basic auth is `root` `password`.



# TODO 
- Students could potentially forge reports by dropping their own json's at the build phase.
- Add container timeouts to test cycle containers to prevent stale workers
- Write assignment tests
- Restructure assignments to fit cluster workflow
