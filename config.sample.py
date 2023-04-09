from sharedObjects import IpCamera

myconfig = {
    "cameras" : [
        IpCamera ("Doorway", "192.168.0.1", "554", "admin", "xxxxxxxxxxxxx", "/2"),
        IpCamera ("Front-Lawn", "192.168.0.2", "554", None, None, "/2")        
    ],

    "app_login" : "test",
    "app_password" : "test",
    "app_port" : "56789",

    "isProd" : False,

    "detailedLogs" : True,

    "path 2 fonts": "static/fonts",
    "font label" : '8bitOperatorPlusSC-Regular.ttf'
}
