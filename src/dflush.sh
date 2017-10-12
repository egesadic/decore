#!/bin/bash
echo "WARNING! This will reset your device and remove all configuration files as well as media."
read -r -p "Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        sudo rm -r /usr/decore/
        ;;
    *)
        exit 0
        ;;
esac