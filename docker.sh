#!/bin/bash

if [ $1 == 'start' ]; then
	docker-compose up -d
elif [ $1 == 'stop' ]; then
	docker-compose down && docker rmi vuln_hub_web
elif [ $1 == 'restart' ]; then
	docker-compose down && docker rmi vuln_hub_web && docker-compose up -d
fi
