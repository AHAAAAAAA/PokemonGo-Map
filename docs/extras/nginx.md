# Nginx

If you do not want to expose pokemongo-map to the web directly or you want to place it under a prefix, follow this guide:

Assuming the following:

* You are running pokemongo-map on the default port 5000
* You've already made your machine available externally (for example, [port forwarding](external.md))

1. Install nginx (I'm not walking you through that, google will assist) - http://nginx.org/en/linux_packages.html
2. In /etc/nginx/nginx.conf add the following before the last `}`

   ```
   include conf.d/pokemongo-map.conf;
   ```

3. Create a file /etc/nginx/conf.d/pokemongo-map.conf and place the following in it:

   ```
   server {
       location /go/ {
          proxy_pass http://127.0.0.1:5000/;
       }
   }
   ```

You can now access it by http://yourip/go

## Add a free SSL Certificate to your site:

1. https://certbot.eff.org/#debianjessie-nginx
2. For webroot configuration, simplest for this use, do the following:
   - Edit your `/etc/nginx/conf.d/pokemongo-map.conf`
   - Add the following location block:
   ```
   location /.well-known/acme-challenge {
     default_type "text/plain";
     root /var/www/certbot;
   }
   ```
3. Create the root folder above `mkdir /var/www/certbot`
4. Set your permissions for the folder
5. Run `certbot certonly -w /var/www/certbot -d yourdomain.something.com`
6. Certificates last for 3 Months and can be renewed by running `certbot renew`

## Example Config

```
server {
    listen       80;
    server_name  PokeMaps.yourdomain.com;

    location /.well-known/acme-challenge {
        default_type "text/plain";
        root /var/www/certbot;
    }

    # Forces all other requests to HTTPS
    location / {
        return      301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name PokeMaps.yourdomain.com;

    location /go/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
    }
}
```
