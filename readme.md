# SimpleOrder Order Management System

SimpleOrder is a simple order system built using flask and wsgi.

Its designed to be easy to use and set up, providiing a fast, easy and portable solution for smaller teams.

It even runs on a [Raspberry Pi](https://raspberrypi.org)!

WARNING! THIS IS NOT YET READY FOR PRODUCTION ENVIRONMENTS AS VERY BASIC FEATURES OF TICKET SYSTEMS ARE STILL MISSING.

## TODOS

Better password resets

Better Order UI

Fix icon spacings in table

## Installation

You can easily install SimpleOrder on any debian System using the provided install script.

TODO: Fix DB errors right after installation and software updates.

QUICK FIX: Run ``flask db upgrade && flask db migrate && flask db upgrade`` in /opt/simpleorder

The default path for the installation is /opt/simpleorder and cannot be changed for now
(If you implement this, please create a pull request and let me know!).

The install script can be run using this command:

    curl -s https://raw.githubusercontent.com/9hax/simpleorder/main/install_simpleorder.sh | sudo bash

This will install apache2, git, python3 and some python3 libraries.
It will also disable the default apache2 welcome page which runs on port 80 to stop it from showing up when not called with the correct domain.

Please put your configuration into userconfig.py to make sure git doesnt mess with your configuration while updating.

## Usage

Just open the Web interface at Port 80! 
If your Hostname is order, the url would be http://order:80.

You can also implement Port 443 with HTTPS by editing the simpleorder.conf file in /etc/apache2/sites-available. 

TODO: Add sample SSL VirtualHost Configuration File and automatically copy it to Destination in Install and Upgrade Script

## Creating the first Admin User

To create an admin user, just visit /add-admin to open a signup form.

For security, this is disabled by default. To enable it temporarily, run ``touch /opt/simpleorder/_CREATE_ADMIN_ALLOWED`` . 
This path can be relatively changed in config.py.

Please make sure to delete the _CREATE_ADMIN_ALLOWED file after adding all the administrator accounts you need, as leaving the file will enable everyone on the same network to create their own admin users without any authentication.

## Creating normal users

To create a normal user, visit /add-user while logged in as an admin.

This will open the same user creation form as /add-admin, but the created user will have less privileges.
