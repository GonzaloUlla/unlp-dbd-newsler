#!/bin/bash

/usr/src/app/wait-for-it.sh elasticsearch:9200 || exit 2
tail -f /dev/null
