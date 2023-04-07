class IpCamera:
    nickname = "camera"
    ip = ""
    port = ""
    login = ""
    password = ""
    suffix = ""
    #see captureStill() for details
    overlay_label = ""

    def __init__(self, nickname, ip, port, login, password, suffix, lbl="Captured at {0:%Y/%m/%d %H:%M:%S}") -> None:
        self.ip = ip
        self.suffix = suffix
        self.port = port
        self.login = login
        self.password = password
        self.nickname = nickname
        self.overlay_label = lbl


    def url(self):
        return f"rtsp://{self.ip}:{self.port}{self.suffix}"