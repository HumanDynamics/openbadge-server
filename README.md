# OpenBadge Django Server
================


## Installation
----------------

For a dev server, you need first to install [Virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) using Pip, [Autoenv](https://github.com/kennethreitz/autoenv) using Pip, and [MySQL](https://dev.mysql.com/doc/refman/5.6/en/osx-installation-pkg.html) using the preinstalled package or Homebrew. You also probably want to install [PyCharm Educational Edition](https://www.jetbrains.com/pycharm-educational/) if you don't have it (it's free for academic accounts!).

Once you have those, be sure to check out the code from this repository. CD into the base directory, and Autoenv should show a message about executing the .env file. Choose `yes`, since it has some very useful shortcuts we'll use.

Now, create a virtual environment:

    virtualenv env

With that created, you'll want to CD to a different directory and then back to the root project directory. This is to restart the Autoenv script with the environment you just created. Now, every time you CD into the base directory, it loads your virtual environment automatically.

First thing is to install the required libraries:

    In Ubuntu, first run: sudo apt-get install build-essential libssl-dev libffi-dev python-dev; pip install pycrypto
    pip install -r requirements.txt

You then will need to install MySQL Python, which isn't included in the requirements because the production server needs to not have it:

    In Ubuntu, first run: sudo apt-get install python-mysqldb libmysqlclient-dev
    pip install MySQL-python

From here on out you'll need to set up your MySQL database:

    fab -f deploy/fabric/deploy.py configure_local_db
    or, if you have a root passwod set for mySQL, fab -f deploy/fabric/deploy.py configure_local_db:root_password=YOU_PASSWORD

With that in place, you can now set up the database tables. You can use the shortcut provided in .env:

    sudo mkdir /var/log/django
    sudo chmod 777 -R  /var/log/django
    migrate

You'll also want to create your super user. There's currently no shortcut for this:

    python src/manage.py createsuperuser --settings=project.localsettings

That should be it! At this point, all you need to do is run the server, then log into your admin to put data into it.

    runserver


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


## Custom Commands
---------------

# Sending Weekly Summary Emails

First `cd` into the project directory.

To send an email containing the weekly summary to all groups, run this command:

    python src/manage.py send_weekly_email --week_num {positive_integer}

To send it to one or more specific groups, run this instead:

    python src/manage.py send_weekly_email --week_num {positive_integer} --group_keys {group_key_1} {group_key_2} ...

# Generate Weekly Summary Charts

To generate charts for the weekly summary for all meetings for a specified group within a specified week (starting from Mon June 13, 2016, e.g. Week 2: Mon 2016-06-20 to Sun 2016-06-26), `cd` into the project directory, then run this command:

    python src/manage.py generatecharts --week_num {positive_integer} --group_keys {group_key_1} {group_key_2} ...

To generate charts for all meetings for all groups, run this command:

    python src/manage.py generatecharts --week_num {positive_integer}

Reports for each group can be viewed through `{hostname}/weekly_group_report/{group_key}/{week_num}`
    
# Importing users from a CSV file

The file must have a header row, and the columns must be:

    email, group, name, badge
    {email1}, {group1}, {name1}, {badge1}
    {email2}, {group2}, {name2}, {badge2}
    {email3}, {group3}, {name3}, {badge3}
    ...

Optionally, you can also set the visualization ranges for the groups bu providing an additional CSV file. The file
must include a header row, and follow the structure below:
    start,end
    {start1},{end1}

where the dates are in UTC timezone, and in the following structure: 2016-06-07 16:37:12

To run it, `cd` into the project directory, then run this command:

    python src/manage.py importcsv --filename={FILENAME OF CSV} --ranges_filename={FILENAME of visualization rages}

# Setting visualization ranges

Similarly to the previous command, you can override the visualization ranges for a given group.

To run it, `cd` into the project directory, then run this command:

    python src/manage.py set_visualization_ranges --group_key={group key} --filename={FILENAME of visualization rages}


# Re-sending post-meeting email

Occasionally, users complain that they have not received the end-of-meeting email. You can resend this email using the following command.

To run it, `cd` into the project directory, then run this command:

    python src/manage.py resend_meeting_email --meeting_uuid {meeting_uuid} --member_key {member_key}


## Backing up a Server's Database
---------------

There is a backup and restoration script that can be used to back up the database and media to S3, and then restore it in the same or a different location.

If the crontab file is deployed to a server it will automatically backup every night. If not, you'll have to run backups manually.

To manually run a backup on a server, SSH into the server then run the command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_backup.py backup_db
    
Then it'll be backed up! To double check it all, you can run this command:

    sudo -u www-data fab -f /opt/OpenBadge-Server/deploy/fabric/db_restore.py list_backups


## Overwriting a Server's Database from a Backup
---------------

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


## Notes
---------------

If you use autoenv, there are many shortcut aliases included to make your life simpler. They change too often to put them in the README, but check out the .env file to see what they are.

TODO: add media_lab_logo.png to media/img directory in production server.
