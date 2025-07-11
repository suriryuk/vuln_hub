#!/bin/bash

if [ $1 == 'start' ]; then
	docker-compose up -d
elif [ $1 == 'stop' ]; then
	docker-compose down && docker rmi vuln_hub_web vuln_hub_db
elif [ $1 == 'restart' ]; then
	docker-compose down && docker rmi vuln_hub_web vuln_hub_db && docker-compose up -d
fi
