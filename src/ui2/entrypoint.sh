#!/usr/bin/env bash

cd /srv/src/ui2/app

npm install
while true; do
    npm start
    sleep 10
done

