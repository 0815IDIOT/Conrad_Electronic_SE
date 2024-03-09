#!/bin/bash

apt-get update
apt-get upgrade
apt-get install python3 sqlite3 python3-pip -y
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

if [ -f resources/data.db ]; then
    echo "[*] deleting old DB" 
    rm resources/data.db
fi

echo "[*] create new DB"
sqlite3 resources/data.db < resources/sqlite3.sql

echo "[*] sucessfully installed!"
echo "[*] initialize database. this may take a while ..."

python3 -B initialize.py