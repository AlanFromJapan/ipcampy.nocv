from sharedObjects import IpCamera

myconfig = {
    "cameras" : [
        IpCamera ("Doorway", "192.168.0.1", "554", "admin", "xxxxxxxxxxxxx", suffixLowRes="/2", suffixHighRes="/1"),
        IpCamera ("Front-Lawn", "192.168.0.2", "554", None, None, suffixLowRes="/2", suffixHighRes="/1")        
    ],


    "app_port" : "56789",
    "secret_key" : "whatever you want!!",

    "isProd" : False,

    "detailedLogs" : True,

    "path 2 fonts": "static/fonts",
    "font label" : '8bitOperatorPlusSC-Regular.ttf',
    "default refresh sec" : 6,

    #Use access control or not?
    "Access control" : True,
    "Login" : "admin",
    "Password" : "admin",
}
