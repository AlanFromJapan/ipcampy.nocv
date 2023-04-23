# ipcampy
Simplistic web interface to show capture of IP Camera. Should work with any RTSP compatible camera.
Uses FFmpeg (av) libs for the capture and **not** OpenCV (the trick being that getting it to work on small board computers is a pain).

Documentation details are here: http://electrogeek.tokyo/ipcampy.nocv.html

## Inspiration

- some guy doing brute force with av (FFMPEG) and **not** OpenCV https://gitlab.com/woolf/RTSPbrute/-/blob/master/rtspbrute/modules/attack.py
- the av lib https://pypi.org/project/av/

## Ideas and todos

- Use ffmpeg in the back to save image every x seconds and just show it with the site. No need to add a Python overlay if ffmpeg does it, and it does : `ffmpeg -i rtsp://my.camera.ip.address:554/2 -vf fps=1/5  camera%03d.jpg` will save 1 JPEG every 5 sec [as the doc says](https://trac.ffmpeg.org/wiki/Create%20a%20thumbnail%20image%20every%20X%20seconds%20of%20the%20video)

# Setup and maintenance 

## Installation

1. git clone https://github.com/AlanFromJapan/ipcampy.nocv.git
1. git branch master 
1. ./install-dependencies.sh
1. create a config.py
1. create the ssl keys in the ssl/ folder
1. From that point it should work if you run it with your user. Now from next line is how to make it a service-like
1. run the ./setup.sh or do the below 2 lines
1. sudo adduser webuser  #make the user
1. sudo passwd -l webuser #disable the login of the user but allows to su to
1. edit the /ssl/*.pem permissions so the files belong to group webuser and that group has readonly access (otherwise can't run as ssh)
1. now run the ./start-service.sh on startup, usually by putting it in /etc/rc.local
1. (optional) you might want to redirect your running port to port 443 so add this also in your /etc/rc.local : `iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port *[the port you use to run the app]*` 
1. reboot and test...

## Troubleshooting

So I got some errors, and I'm trying to get around it. Workarounds only here, if I found the solution I fixed it (duh).

### Service stops answering

After a few days it happened to randomly stop answering. Didn't get why, it was not a memory or CPU problem, logs were ok ... just Flask not answering anymore. Bug of Flask (it has been serving my other website for 700+ days an counting so I doubt), maybe some handling not freed or port? Something due to the av lib?

WORKAROUND: just cron a restart daily using the eponym script, that's it.

### The stop start restart start complaining about tty and askpass?

Dunno why after 3 days this error appeared ! You need to allow your user to sudo and run the stop/start/restart so edit the visudo file and add:

username ALL=NOPASSWD:/home/username/Git/ipcampy.nocv/restart-service.sh, /home/username/Git/ipcampy.nocv/start-service.sh, /home/username/Git/ipcampy.nocv/stop-service.sh
