#!/bin/bash

here=`dirname $0`

sudo -u webuser -s nohup $here/run_ssl.sh > /tmp/ipcampy.log 2>&1 &
