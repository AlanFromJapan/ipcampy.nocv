#!/bin/bash

here=`dirname $0`

echo Restart initiated at `date` > /tmp/ipcampy_restart_latest.log
echo ***STOP*** >> /tmp/ipcampy_restart_latest.log
$here/stop-service.sh >> /tmp/ipcampy_restart_latest.log 2>&1
echo ***START*** >> /tmp/ipcampy_restart_latest.log
$here/start-service.sh >> /tmp/ipcampy_restart_latest.log 2>&1
echo Restart completed at `date` >> /tmp/ipcampy_restart_latest.log
