#!/bin/sh
set -e

if [[ ! -z "$BASE_DEVICES_URL_OVERRIDE" ]]; then
    echo "running with BASE_URL=${BASE_DEVICES_URL_OVERRIDE}"
    sed -i "s^127.0.0.1:5000^$BASE_DEVICES_URL_OVERRIDE^g" /var/www/assets/*.js
fi

if [[ ! -z "$BASE_USECASES_URL_OVERRIDE" ]]; then
    echo "running with BASE_URL=${BASE_USECASES_URL_OVERRIDE}"
    sed -i "s^127.0.0.1:5001^$BASE_USECASES_URL_OVERRIDE^g" /var/www/assets/*.js
fi

# Run the parent (nginx) container's entrypoint script
exec /docker-entrypoint.sh "$@"
