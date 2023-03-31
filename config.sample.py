class IpCamera:
    nickname = "camera"
    ip = ""
    port = ""
    login = ""
    password = ""
    suffix = ""

    def __init__(self, nickname, ip, port, login, password, suffix) -> None:
        self.ip = ip
        self.suffix = suffix
        self.port = port
        self.login = login
        self.password = password
        self.nickname = nickname



myconfig = {
    "cameras" : {
        "Doorway"   : IpCamera ("Doorway", "192.168.0.1", "554", "admin", "xxxxxxxxxxxxx", "/2"),
        "Front-Lawn": IpCamera ("Front-Lawn", "192.168.0.2", "554", "admin", "zzzzzzzzzzz", "/2")        
    },

    "app_login" : "test",
    "app_password" : "test",
    "app_port" : "56789",

    "isProd" : False,

    "detailedLogs" : True
}
