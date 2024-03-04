#!/bin/bash
if [ -f resources/data.db ]; then
    exit
else
    sqlite3 resources/data.db < resources/sqlite3.sql
fi

echo "[*] sucessfully installed!"
