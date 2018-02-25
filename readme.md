[![Build Status](https://travis-ci.org/yegorLitvinov/metric.svg?branch=master)](https://travis-ci.org/yegorLitvinov/metric)

## Simple asyncio hits and visits counter

### Usage
1. Get your api key from administrator
2. Place the following markup at your page
```html
<img
    src="http://metr.ddns.net/api/visit/{your_api_key}/"
    alt="Hits counter"
    style="display: none;"
>
```
3. Watch visit statistics at [http://metr.ddns.net](http://metr.ddns.net)

### Prepare server
```bash
fab install_docker
fab create_docker_network
fab user_add
fab install_certificates
```

### Deploy
```bash
fab copy_nginx
fab metric_pg
fab metric_redis
fab metric_app
fab metric_front
```
or just
```bash
fab prod
```
