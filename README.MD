# Aenaeas timelapse

Hoe ik van een set webcam images een timelapse video maakte. 

## Python programma
Check hoeveel images beschikbaar zijn, bereken hoeveel er nodig zijn. Maak sprongen. 
Daarna, neem een aantal images om te middelen. Middel per frame een aantal images, plak ze allemaal achter elkaar tot een filmpje. 
Fancy muziekje erbij en hop, klaar.

## Splits naar voorbereiding docker versie
Eerste versie werkte alles in een single thread. Daarna omgebouwd met tqdm naar multiprocessing. 
Tweede versie het werk gesplitst, via http en flask, om er eerst een docker en uiteindelijk een kubernetes versie van te maken.

## Docker versie

Docker is mij nog redelijk onbeked. Principe is redelijk duidelijk. Python programma via een _Dockerfile_ omzetten naar een container, deze opslaan in een registry. Hierdoor is deze te downloaden in het (uiteindelijke) kubernetes cluster.

Docker op mijn rpi3 geinstalleerd, volgens de info van [docker](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script) zelf. Daarna nog verder aangepast, zodat ik deze ook als [non-root](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) user kan gebruiken. En hoera! `docker run hello-world` werkt!

Daarna op rpi3 een docker registry aangemaakt, op dit moment wil ik liever niet op docker hub iets gaan uploaden... `sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2`

Eerste test, volgens [Deploy a registry server](https://docs.docker.com/registry/deploying/) met `docker pull python:3`. Lijkt goed te werken

**Dockerfile** Is lastiger dan wat ik dacht. Het installeren van numpy, PIL en Flask levert problemen op. Ik probeer een andere route: deze via apt-get installeren. `docker build --tag img_proc .`

Dat ziet er goed uit. Nu proberen te starten: `docker run -it testje`. Flask wordt niet gevonden...
Ik neem een kijkje in de container: `docker run -it testje /bin/bash`. Nieuwe poging door venv te gebruiken. Pip install werkt nu wel, helaas niet via piwheels. Na een hele lange tijd is de container klaar. Nu start _image_procesor_server_ wel op. Proberen te optimaliseren door een multistage build Dockerfile te maken. Werkte toch niet helemaal goed. Later nog eens opnieuw bekijken. Huidge Dockerfile werkt nu toch met pip.

Docker image naar private registry duwen:
- docker tag img_proc 192.168.178.15:5000/img_proc
- docker push 192.168.178.15:5000/img_proc

Docker image testrun op rpi3: `docker run -p 8000:8000 img_proc`. In make_timelapse.py IMG_PROC aangepast naar de rpi3: werkt! Nu naar de volgende stap...

## Kubernetes

Via mijn andere project, ansible-pis, is kubernetes geinstalleerd op een drietal raspberry pi's. Het zouden er meer kunnen/mogen zijn, maar dat mag de pret niet drukken...

Op rpi3 is een docker registry geinstalleerd. Via de Dockerfile een image gemaakt. Image naar eigen registry toegeduwd.
Dit is een niet beveiligde registry. Bij [Rancher](https://rancher.com/docs/k3s/latest/en/installation/private-registry/) staat een hint hoe een registry geconfigureerd moet worden. Helaas krijg ik dit niet aan de gang, dus... 

### Docker registry TLS versie

Terug naar de tekentafel... Ik pak de [uitleg](https://docs.docker.com/registry/deploying/#run-an-externally-accessible-registry) van Docker zelf op. 
Daarvoor heb ik een certificaat nodig. Ik heb geen eigen hostname, dus via openssl zelf een [certificaat](https://docs.docker.com/registry/insecure/#use-self-signed-certificates) maken:
`openssl ...`. Docker registry opnieuw aangemaakt, deze keer met certificaten. Eerst img_proc verwijderd, daarna opnieuw getagged en gepushed.

Kubernetes krijg ik nog niet aan de gang, kubectl describe pod ... geeft aan dat het certificaat getekend is door een onbekende. Nu certificaat naar master node gekopieerd, daarna update-ca-certificates gedraaid. Nu ff afwachten of ie het nu wel pakt... Niet dus... 

Oplossing gevonden: eerst containerd proberen te voorzien van de certificaten, in /etc/rancher/registries.yaml. Bleek niet te werken, de configuratie veranderen naar:
```
mirrors:
  docker.io:
    endpoint:
      - "https://192.168.178.15:5000"

configs:
  "192.168.178.15:5000":
    tls:
      insecure_skip_verify: true
```

Gaf een beter resultaat. In de deployment.yaml `image: 192.168.178.15:5000/img_proc:latest` veranderd: de `:latest` was nodig. Hiermee kon de boel gestart worden.

