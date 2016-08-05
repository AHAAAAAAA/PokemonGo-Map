# Amazon ECS

Amazon ECS is essentially managed docker allowed you to run multi-container environments easily with minimal configuration. In this guide we'll create an ECS Task that will run a single pokemongo-map container with a MariaDB container

## Requirements

* AWS Account
* AWS ECS Cluster with at least one instance assigned
    * t2.micro type is sufficient for this setup

## Process


In the AWS ECS console create a Task Definition with the JSON below. You will need to set the following values:

* `POKEMON_USERNAME` - username for pokemongo
* `POKEMON_PASSWORD` - password for pokemongo
* `POKEMON_AUTH_SERVICE` - Define if you are using google or ptc auth
* `POKEMON_LOCATION` - Location to search
* `POKEMON_DB_USER` - Database user for MariaDB
* `POKEMON_DB_PASS` - Database password for MariaDB

```json
{
    "taskRoleArn": null,
    "containerDefinitions": [
        {
            "volumesFrom": [],
            "memory": 128,
            "extraHosts": null,
            "dnsServers": null,
            "disableNetworking": null,
            "dnsSearchDomains": null,
            "portMappings": [
                {
                    "hostPort": 80,
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "hostname": null,
            "essential": true,
            "entryPoint": null,
            "mountPoints": [],
            "name": "pokemongomap",
            "ulimits": null,
            "dockerSecurityOptions": null,
            "environment": [
                {
                    "name": "POKEMON_DB_TYPE",
                    "value": "mysql"
                },
                {
                    "name": "POKEMON_LOCATION",
                    "value": "Seattle, WA"
                },
                {
                    "name": "POKEMON_DB_HOST",
                    "value": "database"
                },
                {
                    "name": "POKEMON_NUM_THREADS",
                    "value": "1"
                },
                {
                    "name": "POKEMON_DB_NAME",
                    "value": "pogom"
                },
                {
                    "name": "POKEMON_PASSWORD",
                    "value": "MyPassword"
                },
                {
                    "name": "POKEMON_GMAPS_KEY",
                    "value": "SUPERSECRET"
                },
                {
                    "name": "POKEMON_AUTH_SERVICE",
                    "value": "ptc"
                },
                {
                    "name": "POKEMON_DB_PASS",
                    "value": "somedbpassword"
                },
                {
                    "name": "POKEMON_DB_USER",
                    "value": "pogom"
                },
                {
                    "name": "POKEMON_STEP_LIMIT",
                    "value": "10"
                },
                {
                    "name": "POKEMON_USERNAME",
                    "value": "MyUser"
                }
            ],
            "links": [
                "database"
            ],
            "workingDirectory": null,
            "readonlyRootFilesystem": null,
            "image": "ashex/pokemongo-map",
            "command": null,
            "user": null,
            "dockerLabels": null,
            "logConfiguration": null,
            "cpu": 1,
            "privileged": null
        },
        {
            "volumesFrom": [],
            "memory": 128,
            "extraHosts": null,
            "dnsServers": null,
            "disableNetworking": null,
            "dnsSearchDomains": null,
            "portMappings": [],
            "hostname": "database",
            "essential": true,
            "entryPoint": null,
            "mountPoints": [],
            "name": "database",
            "ulimits": null,
            "dockerSecurityOptions": null,
            "environment": [
                {
                    "name": "MYSQL_DATABASE",
                    "value": "pogom"
                },
                {
                    "name": "MYSQL_RANDOM_ROOT_PASSWORD",
                    "value": "yes"
                },
                {
                    "name": "MYSQL_PASSWORD",
                    "value": "somedbpassword"
                },
                {
                    "name": "MYSQL_USER",
                    "value": "pogom"
                }
            ],
            "links": null,
            "workingDirectory": null,
            "readonlyRootFilesystem": null,
            "image": "mariadb:10.1.16",
            "command": null,
            "user": null,
            "dockerLabels": null,
            "logConfiguration": null,
            "cpu": 1,
            "privileged": null
        }
    ],
    "volumes": [],
    "family": "pokemongo-map"
}
```


If you would like to add workers you can easily do so by adding another container with the additional variable `POKEMON_NO_SERVER` set to `true`. You have to let one of the pokemongo-map containers start first to create the database, an easy way to control this is to create a link from the worker to the primary one as it will delay the start.

Once the Task is running you'll be able to access the app via the Instances IP on port 80.