# OpenBadge Django Server
================


## Installation
----------------

You will need to install Docker CE to run the openbadge server. Follow the instructions here: https://docs.docker.com/engine/installation/


You will likely want to use docker-machine to provision either local or remote hosts. 

To provision a local host for development, follow the instructions here: https://docs.docker.com/machine/get-started/

You can also use docker-machine to provision remote hosts from the command line, e.g. on AWS or DigitalOcean 

Once your machine is provisioned, you must make it active by running: 
    `eval $(docker-machine env <machine-name>)`

You can check to see if this was sucessful by running `docker-machine ls`.
There should be an asterisk under the 'active' column in the output for the machine you activated.

For development, you will want to swap out 'docker-compose' in the following instructions for 'docker-compose -f dev.yml'

Now, you can run the following (all from the base directory of the project):

`docker-compose build`

After the build completes, run:

`docker-compose up`

You can run migrations now using the following command: 

`docker-compose run django python manage.py migrate`

You'll also want to create your super user. There's currently no shortcut for this:

`docker-compose run django python manage.py createsuperuser`

Your openbadge server should be running on the machine you provisioned with docker-machine now. To check the IP:
`docker-machine ip <machine-name>`

You can access the server with this IP. If it is a virtual host running on your machine, you will need to set up port forwarding to your virtual machine in order to access it outside of your computer.



## Deployment
----------------

In order to deploy the server to production, you will need to decide where you wish to deploy to. If you are deploying to a remote cloud-based server, for example DigitalOcean, all you will need to do is provision a host with docker-machine. You can follow the instructions furnished by the service provider to set up the host with docker-machine.

If you intend to deploy to an existing host, you will need three things: A user, an ssh key for said user, and the IP of the machine. To connect to the host via docker using docker-machine, run the following:

`docker-machine create --driver generic --generic-ssh-user <username> --generic-ssh-key <ssh-key-location> --generic-ip-address <ip-address> <machine-name>`

Docker-machine will automatically install docker and all related prereqs on the host.
 
After you have provisioned your host, all you need to do is follow the instructions seen above. 

## Production Server Setup
----------------
If the project has already been set up with SSH keys, be sure to get them from someone. 

Ensure you have a `passwords.py` file located in the config subdirectory of this project's directory, and that it has the proper usernames and passwords in it. It should have the exact variables and format of `config/passwords.py.template`, only the passwords and usernames should be filled in. Also, be sure to change the environment variables in docker-compose.yml to match your environment.

# Custom Commands
---------------
#NOTE: OUTDATED
# General note

The description below show how to execute commands in the local (dev) instance of the server. When executing on the
production server, you should run them as the www-data user, and add --pythonpath=/opt to the command. For example:

    sudo -u www-data /opt/OpenBadge-Server/src/manage.py importcsv --pythonpath=/opt --project_key=AAAA --filename=/home/deploy/temp_groups.csv

Note - "--pythonpath=/opt" MUST come after the management command you'll be running


# Importing users from a CSV file

The file must have a header row, and the columns must be (with no spaces!):

    email,group,name,badge
    {email1},{group1},{name1},{badge1}
    {email2},{group2},{name2},{badge2}
    {email3},{group3},{name3},{badge3}
    ...

Where "badge" is the MAC address, and "group" isn't currently used

To run it, `cd` into the project directory, then run this command:

    python src/manage.py importcsv --project_key={DB project key} --filename={FILENAME OF CSV}

Note - the timestamps for these members will be set to the time the script was executed

# Resetting the last timestamps

If you need to set the timestamp to the current date, you can use the set_timestamps command

`cd` into the project directory, then run this command:

    python src/manage.py set_timestamps --project_key={DB project key}

Note - if you want to set the timestamp to a specific value, you can use --timestamp={epoch time}


# Database related commands
---------------
#NOTE this is outdated

## Backing up a Server's Database

There is a backup and restoration script that can be used to back up the database and media to S3, and then restore it in the same or a different location.

If the crontab file is deployed to a server it will automatically backup every night. If not, you'll have to run backups manually.

To manually run a backup on a server, SSH into the server then run the command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_backup.py backup_db
    
Then it'll be backed up! To double check it all, you can run this command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_restore.py list_backups


## Overwriting a Server's Database from a Backup

## WARNING: DO NOT RUN THIS ON PRODUCTION!

Are you on production? Don't run this. Are you not on production? You probably don't want to run this!

When you do this, this will overwrite all your media and all your database, replacing them with those of a backup. Seriously. It will be gone forever.

If you really must continue, here's how:

First off, as a safety concern, the restoration script **will not work with settings.DEBUG = False**. So your first step is to set `DEBUG = True` in settings.py.

With that done, get the name of a backup with this command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_restore.py list_backups

It will give results like this:

    S3 Bucket Contents:
    -----------
    tmp/dump.2016-05-27.10-02.sql.enc
    tmp/dump.2016-06-01.22-27.sql.enc
    tmp/dump.2016-06-02.19-45.sql.enc
    tmp/media.2016-05-27.10-02.tar.gz.enc
    tmp/media.2016-06-01.22-27.tar.gz.enc
    tmp/media.2016-06-02.19-45.tar.gz.enc

Find a datestring from one of those backups. The datestring in this case could be `2016-06-02.19-45` or `2016-06-01.22-27`

With that datestring, run this command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_restore.py restore_db:datestring={{DATESTRING}}

It will ask for you to confirm a couple times, then do the restoration.

Finally, **Be sure you turn DEBUG = False** on again in settings.py.

