class IpCamera:
    nickname = "camera"
    ip = ""
    port = ""
    login = ""
    password = ""
    suffixLowRes = ""
    suffixHighRes = ""
    #see captureStill() for details
    overlay_label = ""

    #Constants a la Python, the default label for overlay
    def defaultLabel():
        return "Captured at {0:%Y/%m/%d %H:%M:%S}"


    def __init__(self, nickname, ip, port, login, password, suffixLowRes, suffixHighRes=suffixLowRes, lbl=defaultLabel()) -> None:
        self.ip = ip
        self.suffixLowRes = suffixLowRes
        self.suffixHighRes = suffixHighRes
        self.port = port
        self.login = login
        self.password = password
        self.nickname = nickname
        self.overlay_label = lbl

    #get the connection URL
    def url(self, highRes=False):
        suffix = self.suffixHighRes if highRes else self.suffixLowRes

        if self.login and not self.login.isspace():
            #there's a login non null non empty
            return f"rtsp://{self.login}:{self.password}@{self.ip}:{self.port}{suffix}"
        #anonymous string
        return f"rtsp://{self.ip}:{self.port}{suffix}"
    
