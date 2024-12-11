#!/bin/bash

echo "Container is running!!!"

chmod +x /app/set_env.sh
source /app/set_env.sh

args="$@"
echo $args

if [[ -z ${args} ]]; 
then
    pipenv shell
else
  pipenv run python $args
fi