# Gobannus

> Work in progress!

Gobannus, also known as Goibniu or Gofannon in different Celtic traditions, is a deity associated with blacksmithing in
Celtic mythology.

## Summary

Gobannus is a project build recorder designed to streamline and enhance the documentation of build project activities.
It offers a comprehensive solution for recording, managing, and sharing the progress of your projects.

## Use Cases
* __Experimental Aircraft Construction:__ Video recording during the construction of experimental aircraft is pivotal in
ensuring airworthiness, serving multiple critical functions. Firstly, it offers a detailed and dynamic record of the
entire building process. This aspect is particularly vital in experimental aviation, where unique and innovative
construction methods are often employed. Videos capture intricate details and specific techniques that might be
overlooked in traditional documentation, ensuring every step of the process is thoroughly documented. This level of
detail is crucial for maintaining high standards of quality control and for verifying that all procedures align with
safety requirements and design specifications.

![Aircraft construction YouTube video](./docs/static/youtube.png)

## Features

* __Multi-Camera Feed Recording:__ Gobannus enables the recording of build activities from multiple camera feeds
simultaneously. This feature ensures comprehensive coverage and detailed documentation of the entire building process
from different angles.
* __Automatic YouTube Uploads:__ After recording, Gobannus takes care of uploading the build activity videos to YouTube.
This automation saves time and effort, making the sharing of progress effortless.
* __Notion Integration:__ Gobannus goes a step further by synchronizing the activity progress to Notion. This
integration includes links to the YouTube videos, providing an organized and accessible way to track and review project
developments.

## TODO
* __C4 Model Diagram:__ Plans are underway to include a C4 model diagram. This diagram will provide a visual 
representation of the software architecture, offering insights into the system's components and their interactions.

## Requirements
* Python >= 3.8
* Docker and Docker Compose

## Run
Execute the following to start a local cluster:

```shell
docker compose up --build -d && docker compose logs -f
```

(Note: Linux requires running docker as `sudo`.) 
