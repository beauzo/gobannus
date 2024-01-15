# Airplane Build Tracker

Experimental aircraft build tracker system.

Features:
* Records camera feeds during build activities
* Stores build activity video to YouTube
* Synchronizes activity progress to Notion; includes links to YouTube videos 

TODO:
* Detailed description, intent, and reasoning
* C4 model diagram

## Setup
* Requires Python >= 3.8
* Docker and Docker Compose

## Run
Execute the following to start a local cluster:

```shell
docker compose up --build -d && docker compose logs -f
```

(Note: Linux requires running docker as `sudo`.) 
