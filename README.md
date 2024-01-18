# Gobannus

Gobannus is a project build recorder.

Features:
* Record multiple camera feeds during build activities
* Automatically uploads build activity videos to YouTube
* Synchronizes activity progress to Notion, including links to YouTube videos 

TODO:
* Gobannus detailed description, intent, and reasoning
* C4 model diagram

## Requirements
* Python >= 3.8
* Docker and Docker Compose

## Run
Execute the following to start a local cluster:

```shell
docker compose up --build -d && docker compose logs -f
```

(Note: Linux requires running docker as `sudo`.) 
