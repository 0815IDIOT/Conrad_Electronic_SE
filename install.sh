#!/bin/bash

#sudo apt-get update
#sudo apt-get upgrade
#sudo apt-get install python3 sqlite3

if [ -f resources/data.db ]; then
    echo "[*] deleting old DB" 
    rm resources/data.db
fi

echo "[*] create new DB"
sqlite3 resources/data.db < resources/sqlite3.sql

echo "[*] sucessfully installed!"
