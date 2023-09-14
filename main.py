from atexit import register
from pathlib import Path
from shutil import rmtree

from src.Configuration import Settings
from src.CookieTool import Cookie
from src.CookieTool import Register
from src.FileManager import DownloadRecorder
from src.FileManager import deal_config
from src.Parameter import NewXBogus
from src.Parameter import generate_user_agent
from src.StringCleaner import Colour
from src.main_api_server import APIServer
from src.main_complete import TikTok
from src.main_server import Server
from src.main_web_UI import WebUI


class TikTokDownloader:
    VERSION = 4.2
    STABLE = True

    REPOSITORY = "https://github.com/JoeanAmier/TikTokDownloader"
    LICENCE = "GNU General Public License v3.0"
    DOCUMENTATION = "https://github.com/JoeanAmier/TikTokDownloader/wiki/Documentation"
    RELEASES = "https://github.com/JoeanAmier/TikTokDownloader/releases/latest"
    NAME = f"TikTokDownloader v{VERSION}{'' if STABLE else ' Beta'}"
    WIDTH = 50
    LINE = ">" * WIDTH

    UPDATE = {"path": Path("./src/config/Disable_Update")}
    COLOUR = {"path": Path("./src/config/Disable_Colour")}
    RECORD = {"path": Path("./src/config/Disable_Record")}
    DISCLAIMER = {"path": Path("./src/config/Consent_Disclaimer")}

    def __init__(self):
        self.colour = None
        self.cookie = None
        self.register = None
        self.blacklist = None
        self.user_agent, self.code = generate_user_agent()
        self.x_bogus = NewXBogus()
        self.settings = Settings()
        self.register = Register(
            self.settings,
            self.x_bogus,
            self.user_agent,
            self.code)

    def check_config(self):
        folder = ("./src/config", "./cache", "./cache/temp")
        for i in folder:
            if not (c := Path(i)).is_dir():
                try:
                    c.mkdir()
                except FileNotFoundError:
                    print(f"发生预期之外的错误，请联系作者寻求解决方案，工作路径: {Path.cwd()}")
                    exit()
        self.UPDATE["tip"] = "启用" if self.UPDATE["path"].exists() else "禁用"
        self.COLOUR["tip"] = "启用" if (
            c := self.COLOUR["path"].exists()) else "禁用"
        self.RECORD["tip"] = "启用" if (
            b := self.RECORD["path"].exists()) else "禁用"
        self.colour = Colour(not c)
        self.blacklist = DownloadRecorder(not b, "./cache")
        self.cookie = Cookie(self.settings, self.colour)

    def main(self, url=""):
        self.complete(url)

    def complete(self, url=""):
        """终端命令行模式"""
        example = TikTok(
            self.colour,
            self.blacklist,
            self.x_bogus,
            self.user_agent,
            self.code,
            self.settings)
        register(self.blacklist.close)
        example.run(url)

    def change_config(self, file: Path, tip="修改设置成功！"):
        deal_config(file)
        print(tip)
        self.check_config()

    def write_cookie(self):
        self.cookie.run()

    def auto_cookie(self):
        if cookie := self.register.run():
            self.cookie.extract(cookie)
        else:
            print("扫码登录失败，未写入 Cookie！")

    def check_settings(self):
        if not Path("./settings.json").exists():
            self.settings.create()

    def run(self, url=""):
        self.check_config()
        self.check_settings()
        self.complete(url)
        self.delete_temp()

    @staticmethod
    def delete_temp():
        rmtree(Path("./cache/temp").resolve())


if __name__ == '__main__':
    TikTokDownloader().run()
