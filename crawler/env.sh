#!/bin/bash

## //!!\\ launch with source ./env.sh

## Create a safe environment
virtualenv __crawler__
source __crawler__/bin/activate
rm bdd.db -f

##install dependencies
pip install -r requirements.txt

clear 
## Commande to use crawler
echo -e "\n--- endpoint ---\n"
echo "curl -i http://127.0.0.1:8080"
echo "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"hashtag\": \"trump\", \"lang\": \"en\", \"nb\": 200}' http://127.0.0.1:8080/v1.0/hashtag"
echo "curl -i http://127.0.0.1:8080/v1.0/trump"
echo -e "\n--- endpoint (quit with ^C)---\n"

## run crawler
python main.py

## quit the env
deactivate
rm -fr __crawler__
