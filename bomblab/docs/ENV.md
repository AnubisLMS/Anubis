# Environment Variables

There are a few environment variables that are read when the deploy script runs. 
The deploy.sh script will check to see that they are all defined. If any one is not
defined, it will print an error message and exit. Each of those variables are:

My recomendation is to store these environment variables in the `bomblab/.env` file.

### ACME_EMAIL
This should be the email used to get a [letsencrypt](https://letsencrypt.org/) ssl cert.
This can be any old email. They won't send you any spam. They will only send alerts when the 
cert is close to expiring.

### BOMB_AUTH
This variable needs to be a [htpasswd](https://en.wikipedia.org/wiki/.htpasswd). That is 
pretty much just a format for saving credentials. Its just username:passwordhash. This 
format supports multiple different hashing algorithms. The best way to generate this htpasswd
is to use this command:

```bash
docker run -it httpd htpasswd -Bbn '<username>' '<password>' | python3 -c 'print(input().strip())'
```

### DOMAIN
This should be the domain that you are using. It is used to determine routing rules for traefik.
