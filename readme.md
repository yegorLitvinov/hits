[![Build Status](https://travis-ci.org/yegorLitvinov/metric.svg?branch=master)](https://travis-ci.org/yegorLitvinov/metric)

## Simple asyncio hits and visits counter

### Usage
Place the following markup at your page
```html
<img
    src="http://metr.ddns.net/visit/{your_api_key}/"
    alt="Hits counter"
    style="display: none;"
>
```

### Deploy
```bash
fab metric_pg  # checkout dockerfile
fab metric_app
```
