#!/usr/bin/env bash

set -e

case "$1" in
  dm)
    shift;
    # Run Device manager Server
    exec python3 devices/api.py $@
    ;;

  usecases)
    shift;
    # Run Device manager Server
    exec python3 usecases/manager/api.py $@
    ;;

  *)
    echo "Usage: $0 {dm, usecases}" >&2
    exit 1
    ;;
esac
