#!/bin/bash
set -e

# path of script
SCRIPT=$(readlink -f $0)
# script directory
DIR=`dirname $SCRIPT`

cd $DIR
rm -rf env
virtualenv env
env/bin/pip install -r requirements.txt
