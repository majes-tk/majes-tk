#!/bin/bash

#print color
green=`tput setaf 2`
reset=`tput sgr0`

###############################
# Install Packages            #
###############################
echo ${green}Install Packages${reset}

sudo apt update

sudo apt install apache2 git nano -y
sudo apt install python3 python3-pip -y
sudo apt install libapache2-mod-wsgi-py3 -y

###############################
# Clone GitHub Repository     #
###############################
echo ${green}Clone GitHub Repository${reset}

# Clone the GitHub Repo to /opt/app.majes.tk
sudo git clone https://github.com/majes-tk/majes-tk /opt/app.majes.tk

# make app.majes.tk directory accessible
sudo chmod 777 /opt/app.majes.tk -R

#####################################
# Create folder for upgrade backups #
#####################################
echo ${green}Create backup folder${reset}

# make the folder
mkdir /opt/app.majes.tk_backups

# make app.majes.tk_backups directory accessible
sudo chmod 777 /opt/app.majes.tk_backups -R

##################################
# Create User configuration File #
##################################
echo ${green}Create user configuration file${reset}

# copy stock config file to userconfig.py. this is in te gitignore, so git should never touch it.
cp /opt/app.majes.tk/config.py /opt/app.majes.tk/userconfig.py

#######################
# Python dependencies #
#######################
echo ${green}Python dependencies setup${reset}

# move to app.majes.tk directory o make the following steps easier
cd /opt/app.majes.tk

# install current requirements using pip3
pip3 install -r requirements.txt

###############################
# Begin apache2 configuration #
###############################
echo ${green}Begin apache2 cofniguration${reset}

# Disable the default apache2 site
sudo a2dissite 000-default.conf

# Copy the app.majes.tk configuration file to the apache2 config directory
sudo cp /opt/app.majes.tk/majestkapp.conf /etc/apache2/sites-available

# Enable the site by linking to sites-enabled
sudo a2ensite majestkapp.conf

# Reload apache2 web server to make site available
sudo service apache2 stop

####################
# Begin Flask init #
####################
echo ${green}Begin Flask init${reset}

# Start database migrations
flask db upgrade
flask db migrate -m "Initial installation"
flask db upgrade

####################
# Begin SMTP Setup #
####################

read -p "Do you want to set up SMTP for password reset and Email Notifications now? (n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
 read -p "Please put in the SMTP Server that the EMail Address is stored on. > " SMTPSERVER
 echo
 read -p "Please put in the Port number that the SMTP Server is running on. > " SMTPPORTNUMBER
 echo
 read -p "Please put in the Email Address that you want app.majes.tk to send EMail from. > " SMTPUSER
 echo
 echo "Please put in the Password of the User Account that you want to send EMail from. > "
 read -s SMTPKEY
 SMTPSERVER=
 sed -i "s,SMTP_SERVER = None,SMTP_SERVER = \"$SMTPSERVER\"," smtpconfig.py
 sed -i "s,SMTP_PORT = None,SMTP_PORT = $SMTPPORTNUMBER," smtpconfig.py
 sed -i "s,SMTP_USER = None,SMTP_USER = \"$SMTPUSER\"," smtpconfig.py
 sed -i "s,SMTP_PASSWORD = None,SMTP_PASSWORD = \"$SMTPKEY\"," smtpconfig.py
fi

echo "You can repeat SMTP-Setup by editing the variables in smtpconfig.py manually."


#################
# Start website #
#################
echo ${green}Start website${reset}

# Start apache2
sudo service apache2 start

echo ${green}You can set up majestkapp with the file /opt/app.majes.tk/config.py${reset}
