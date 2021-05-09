# Aenaeas timelapse

Hoe ik van een set webcam images een timelapse video maakte. 

## Python programma

## Splits naar voorbereiding docker versie
via http en flask

## Docker versie

Docker is mij nog redelijk onbeked. Principe is redelijk duidelijk. Python programma via een _Dockerfile_ omzetten naar een container, deze opslaan in een registry. Hierdoor is deze te downloaden in het (uiteindelijke) kubernetes cluster.

Docker op mijn rpi3 geinstalleerd, volgens de info van [docker](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script) zelf. Daarna nog verder aangepast, zodat ik deze ook als [non-root](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) user kan gebruiken. En hoera! `docker run hello-world` werkt!

Daarna op rpi3 een docker registry aangemaakt, op dit moment wil ik liever niet op docker hub iets gaan uploaden... `sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2`

Eerste test, volgens [Deploy a registry server](https://docs.docker.com/registry/deploying/) met `docker pull python:3.9.5-slim-buster`. Lijkt goed te werken

**Dockerfile** Is lastiger dan wat ik dacht. Het installeren van numpy, PIL en Flask levert problemen op. Ik probeer een andere route: deze via apt-get installeren. `docker build --tag testje .`

Dat ziet er goed uit. Nu proberen te starten: `docker run -it testje`. Flask wordt niet gevonden...
Ik neem een kijkje in de container: `docker run -it testje /bin/bash`. Nieuwe poging door venv te gebruiken. Pip install werkt nu wel, helaas niet via piwheels. Na een hele lange tijd is de container klaar. Nu start _image_procesor_server_ wel op.


