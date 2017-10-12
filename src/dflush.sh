#!/bin/bash
echo "WARNING! This will reset DeCore node and remove all configuration files as well as all media."
read -r -p "Do you want to proceed? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        sudo rm -r /usr/decore/
        echo "DeCore node has been reset."
        ;;
    *)
        exit 0
        ;;
esac