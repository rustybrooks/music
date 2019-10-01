#!/usr/bin/env bash

cd /srv/src/ui/app

npm install
while true; do
    npm start
    sleep 10
done

