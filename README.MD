# Aenaeas timelapse

Hoe ik van een set webcam images een timelapse video maakte. 

## Python programma

## Splits naar voorbereiding docker versie
via http en flask

## Docker versie

Docker is mij nog redelijk onbeked. Principe is redelijk duidelijk. Python programma via een _Dockerfile_ omzetten naar een container, deze opslaan in een registry. Hierdoor is deze te downloaden in het (uiteindelijke) kubernetes cluster.

Docker op mijn rpi3 geinstalleerd, volgens de info van [docker](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script) zelf. Daarna nog verder aangepast, zodat ik deze ook als [non-root](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) user kan gebruiken. En hoera! `docker run hello-world` werkt!

Daarna op rpi3 een docker registry aangemaakt, op dit moment wil ik liever niet op docker hub iets gaan uploaden... `sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2`

Eerste test, volgens [Deploy a registry server](https://docs.docker.com/registry/deploying/) met `docker pull python:3.9.5-slim-buster`. 