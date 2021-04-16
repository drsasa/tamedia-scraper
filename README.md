# Tamedia Test

API server and scraper application

## Getting started

The stack consists of the following elements:

- Python 3.9.x
- Postgres 13
- Redis 5.x

To replicate the development environment (somewhat) faithfully on your
development machine, we use Docker Compose. It is highly recommended to use
Docker for development. If you know what you are doing, you can set up the
individual parts of the stack yourself.

### Installing Docker

If you are on Windows or Mac, use the [Docker Desktop](https://dockr.ly/2KoEowU)
for your operating system. On Linux, you will need to install `docker` and
`docker-compose` tools via your distro's preferred installation method.

### Migrating the database

This is done both before the first time you want to run the Docker cluster.

```bash
docker-compose build
```

### Starting Docker cluster

To start the Docker cluster up, run the following command:

```bash
docker-compose up
```

Or if we want to scale some parts we can start with next command:

```bash
docker-compose up -d --scale worker-scraping=3 --scale worker-mapping=2 --scale api-service=1
```


Once it's up, the development server is available on port 80.

## How to remove all containers

To remove all containers defined in docker-compose.yml, stop the cluster and
run:

```bash
docker-compose down --remove-orphans
```

or

```bash
docker-compose down -v --rmi all --remove-orphans
```

After that, set everything up as if it's the first time.

## Short description of all services

### postgres
  It is a DB service with a PostgreSQL database instance.Can be accessed on address `127.0.0.1:5432`

### flower
  Celery monitoring utility.
  Can be accessed on address `127.0.0.1:6660`
  It is used for monitoring and checking tasks (scraping, mapping/transforming), 
  with all time consumed and eventual errors.

### api-service
  It is Flask mini web api with one endpoint.

### nginx
  It is a reverse proxy for our mini Flask API.
  Can be accessed on `127.0.0.1`. And accepts date for our single endpoint.
  `127.0.0.1/2021/04/16` -> return result for date `2021-04-16`

### beat
  Beat service is a cron job. It triggers a scraping task every 60sec.

### worker-srcraping and worker-mapping
  These two services do scraping and mapping/transformations jobs.
  They are independent, so can scale on it's own.
