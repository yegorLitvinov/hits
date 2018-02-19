[![Build Status](https://travis-ci.org/yegorLitvinov/metric.svg?branch=master)](https://travis-ci.org/yegorLitvinov/metric)

## Simple asyncio hits and visits counter

### Usage
Place the following markup at your page
```html
<img
    src="http://metr.ddns.net/visit/{your_api_key}/"
    alt="metriccounter"
    style="display: none;"
>
```

### Docker
```bash
docker build --tag metric:latest .
docker run -d -p8181:8181 --volume=`pwd`:/app --name metric --rm metric:latest
```
