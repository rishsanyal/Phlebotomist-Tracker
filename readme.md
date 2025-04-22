Lifecycle Status of Clinicians:

1. Initailized
2. Within Bounds
3. Outside Bounds
4. Error

Deployment:

1. source ./venv/bin/activate
2. python3 app.py

Trade-Offs:

1. Redis vs Postgres
2. Different threads

Deepdive

1. notification service
2. Redis as db, but any SQL works. Redis would be worse persistence. better for cacheing
   Could set an expiry dates. Traditional DB's store GEO info well. POSTGIS is very mature and SQL is more persistent. Could use Redis as a cache of sorts
3. Look into Ray-Casting Algo vs Ray-tracing

Enhancements:

1. Paralleize each clinician info
2. Could fan out API requests with a random delay

TODO:

1. Convert shapely_test to pytest
