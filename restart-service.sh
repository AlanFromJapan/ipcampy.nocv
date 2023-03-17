#!/bin/bash

here=`dirname $0`

$here/stop-service.sh
$here/start-service.sh
