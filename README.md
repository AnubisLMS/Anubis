# Anubis

## Debugging
This project requires envrionment variables to be deployed. You can store those in
a `.env` file to keep things simple. Here is an example `.env` file for debugging.

*DO NOT USE THIS ENV IN PROD*

```
ACME_EMAIL=john.doe@email.com
MYSQL_ROOT_PASSWORD=password
GF_SECURITY_ADMIN_PASSWORD=password
AUTH='root:$2y$05$2VCT7LSzWh7ULSHtQHHxBeTu89WoE5W995MDXc5XVygYCqI3Rn8am'
DOMAIN=localhost
```

This debug environment will let you connect to the api on https://localhost/.
The creds for all http basic auth is `root` `password`.
