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

Now, you can run the following:

`docker-compose build`

After the build completes, run:

`docker-compose up`

You can run migrations now using the following command: 

`docker-compose run django python manage.py migrate`

You'll also want to create your super user. There's currently no shortcut for this:

`docker-compose run django python manage.py createsuperuser`



You probably want to install [PyCharm Educational Edition](https://www.jetbrains.com/pycharm-educational/) if you don't have it (it's free for academic accounts!).

Migrate
    migrate


That should be it! At this point, your server should be up and running.

Your openbadge server should be running on the machine you provisioned with docker-machine now. To check the IP:
`docker-machine ip <machine-name>`

You can access the server with this IP. If it is a virtual host running on your machine, you will need to set up port forwarding to your virtual machine in order to access it outside of your computer.



## Deployment
----------------

In order to deploy the server to production, you need four files that are not checked in. Get `github_rsa`, `github_rsa.pub`, `sshkey`, and `sshkey.pub` from someone via email, and put them in the directory `deploy/fabric/keys`.

At that point all you need to deploy the code to production is to run the command:

    fab -f deploy/fabric/deploy.py -H {HOSTNAME} deploy


## Production Server Setup
----------------

If the repository is public, you will not need to create a Github access token. Otherwise, if it is private, follow [the instructions here](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) to get a Personal Access Key.

If the project has already been set up with SSH keys, be sure to get them from someone. Just put the keys in the deploy/fabric/keys/ directory. If you don't have any keys there, they will be created automatically when you create a deploy user.

Ensure you have a `passwords.py` file located on the root of this project's directory, and that it has the proper usernames and passwords in it. It should have the exact variables and format of `src/project/passwords.py.template`, only the passwords and usernames should be filled in.


Now that we have the correct files, create a deploy user on your server:

    fab -f deploy/fabric/create_deploy_user.py -H {{ YOUR USERNAME HERE }}@{{ YOUR HOSTNAME HERE }} create
    
Or, if you are using an SSHConfig HostName alias, just use this:

    fab -f deploy/fabric/create_deploy_user.py -H {{ HOSTNAME }} create

To make sure it worked, run this command to test that the user was created:

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} test

Then just run the command:

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} setup_server

This command is safe to run on a server that's already been set up, though you should avoid it if possible.

After that, you just need to configure Django.

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} create_superuser
    
Now you're all set and you should be able to log in to your admin console on your server!


# Custom Commands
---------------
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

