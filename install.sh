#!/bin/bash

#sudo apt-get update
#sudo apt-get upgrade
#sudo apt-get install python3 sqlite3 python3-pip
#python3 -m ven venv
#source venv/bin/activate
#pip3 install -r requirements.txt
#python3 -B initialize.py

if [ -f resources/data.db ]; then
    echo "[*] deleting old DB" 
    rm resources/data.db
fi

echo "[*] create new DB"
sqlite3 resources/data.db < resources/sqlite3.sql

echo "[*] sucessfully installed!"
