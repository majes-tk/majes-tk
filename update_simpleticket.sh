#!/bin/bash

green=`tput setaf 2`
reset=`tput sgr0`

# stop apache fto close the database file
echo ${green}Stopping apache...${reset}
sudo service apache2 stop

# make backup of the current system
echo ${green}Creating backup...${reset}
mkdir /opt/app.majes.tk_backups/$(date +"%d-%m-%Y")
cp /opt/app.majes.tk/* /opt/app.majes.tk_backups/$(date +"%d-%m-%Y") -R

# Pull changes
echo ${green}Pulling updates...${reset}
cd /opt/app.majes.tk
sudo git pull

# make app.majes.tk directory accessible
echo ${green}Changing directory perms...${reset}
sudo chmod 777 /opt/app.majes.tk -R

# Start database migrations
echo ${green}Running database migrations...${reset}
flask db upgrade
flask db migrate -m "app.majes.tk Update"

# Start apache2
echo ${green}Starting apache...${reset}
sudo service apache2 start
