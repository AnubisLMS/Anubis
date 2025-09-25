# Theia Proxy  
Proxies requests to the corresponding ide server based on the session_id for the given request.  
Fetches the `cluster_ip` from the token, then proxies http and ws requests.  


### Running Locally
Requires you to run `mkdebug` to be able to test proxying to an ide.
