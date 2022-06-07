#!/bin/bash

here=`dirname $0`

#flask run --cert=ssl/cert.pem --key=ssl/key.pem
python3 $here/ipcampy.py $here/ssl/cert.pem $here/ssl/key.pem
