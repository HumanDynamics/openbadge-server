# OpenBadge Django Server

The OpenBadge server now uses Docker for development and deployment. This document explains how to configure your server, and how to use Docker-compose and Docker-machine for deployment.
You can find further examples in the Docker website.

## Configuration
Configuration is done using a .env file. Create a new one by copying config/env_template to the root project dir and renaming it to .env. Then, edit the following fields:
* POSTGRES_DBNAME - name of database schema (can leave as is)
* POSTGRES_USER - name of postgres user to use (can leave as is)
* POSTGRES_PASSWORD - unique password to use for the postgres user
* DJANGO_SECRET_KEY - A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value
* ALLOWED_HOSTS - A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent HTTP Host header attacks.
* APP_KEY - a unique key used by the OpenBadge server to authenticate hubs

Important! do not commit the .env to a github repository, but keep a copy somewhere safe.

## Setting up your working environment
First, you will need to install Docker CE to run the openbadge server. Follow the instructions here:
https://docs.docker.com/engine/installation/ . This also includes docker-compose.

## Development
For development purposes, you will probably want to run a local copy of the server. You can either run docker-compose
directly (if you are using Linux), use Docker for mac (https://docs.docker.com/docker-for-mac/) or Docker for Windows
(https://docs.docker.com/docker-for-windows/).

Now, you can run the following (all from the base directory of the project):

`docker-compose -f dev.yml build`

You can run migrations now using the following command:

`docker-compose -f dev.yml run django python manage.py migrate`

You'll also want to create your super user (Django admin account):

`docker-compose -f dev.yml run django python manage.py createsuperuser`

Finally, run the following command to start the server:

`docker-compose -f dev.yml up`

In order to check whether the server is working, login to the admin console: http://localhost:8000/admin

### Using a virtual machine for development
You can also create a local Virtual Machine and provision it - https://docs.docker.com/machine/get-started/

If you decide to use a VM, make sure you make it active by running:
    `eval $(docker-machine env <machine-name>)`

You can check to see if this was successful by running `docker-machine ls`.
There should be an asterisk under the 'active' column in the output for the machine you activated.

To check the IP of the VM:
`docker-machine ip <machine-name>`

You can access the server with this IP. If it is a virtual host running on your machine, you will need to set up port forwarding to your virtual machine in order to access it outside of your computer.

## Deployment
----------------

We recommend deploying the code to a server is using docker-machine. You can either deploy to an existing host (physical or virtual) or a could-based server, such as DigitalOcean or AWS.

If you are deploying to a remote cloud-based server, you can follow the instructions furnished by the service provider to set up the host with docker-machine. Examples can also be found in the Docker-machine page - https://docs.docker.com/machine/examples/

If you intend to deploy to an existing linux host, you will need three things: A user, an ssh key for said user, and the IP of the machine. To setup docker and provision the server using docker-machine, run the following:

`docker-machine create --driver generic --generic-ssh-user <username> --generic-ssh-key <ssh-key-location> --generic-ip-address <ip-address> <machine-name>`

Docker-machine will automatically install docker and all related prereqs on the host.
 
Make sure you make the new machine the active machine by running:
    `eval $(docker-machine env <machine-name>)`

You can check to see if this was successful by running `docker-machine ls`.
There should be an asterisk under the 'active' column in the output for the machine you activated.

Now, you can run the following (all from the base directory of the project):

`docker-compose build`

You can run migrations now using the following command:

`docker-compose run django python manage.py migrate`

You'll also want to create your super user (Django admin account):

`docker-compose run django python manage.py createsuperuser`

Finally, run the following command to start the server (the "-d" option will keep the service up as a daemon):

`docker-compose up -d`

In order to check whether the server is working, login to the admin console: http://your-server-address/admin

## Misc commands
* docker-compose down : disables the server
* docker-compose down -v : disables the server and deletes the volume data (use with caution...)
* docker-compose build --force-rm --no-cache --pull : rebuilds without using cached images. Useful when you change the
configuration files
* docker volume ls : list of existing volumes
* docker-compose run django bash  : open interactive shell into the Django container
