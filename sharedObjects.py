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


    def url(self):
        return f"rtsp://{self.ip}:{self.port}{self.suffix}"