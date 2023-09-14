import sys
from time import time

from src.Customizer import TEXT_REPLACEMENT
from src.Customizer import failed
from src.DataAcquirer import Acquirer
from src.DataDownloader import Downloader
from src.FileManager import Cache
from src.Recorder import BaseLogger
from src.Recorder import LoggerManager
from src.Recorder import RecordManager


def prompt(
        tip: str,
        choose: tuple | list,
        colorize,
        start=1,
        separate=None) -> str:
    screen = colorize(f"{tip}:\n", 96, bold=1)
    row = 0
    for i, j in enumerate(choose):
        screen += colorize(f"{i + start}. {j}\n", 92, bold=1)
        if separate and row in separate:
            screen += colorize(f"{'=' * 25}\n", 92, bold=1)
        row += 1
    return input(screen)


def check_save(function):
    def inner(self, *args, **kwargs):
        if self.save:
            return function(self, *args, **kwargs)
        print(self.colour.colorize("未设置 save 参数，无法正常使用该模式！", 93))

    return inner


class TikTok:
    SEARCH = {
        "type": {
            "综合": 0,
            "视频": 1,
            "用户": 2,
            # "直播": 3,
            "0": 0,
            "1": 1,
            "2": 2,
            # "3": 3,
        },
        "type_text": {
            0: "综合搜索",
            1: "视频搜索",
            2: "用户搜索",
            # 3: "直播搜索",
        },
        "sort": {
            "综合排序": 0,
            "最新发布": 1,
            "最多点赞": 2,
            "0": 0,
            "1": 1,
            "2": 2,
        },
        "sort_text": {
            0: "综合排序",
            1: "最新发布",
            2: "最多点赞",
        },
        "publish_text": {
            "0": "不限",
            "1": "一天内",
            "7": "一周内",
            "182": "半年内",
        },
    }
    DATA_TYPE = {
        0: "",
        1: "",
        2: "search_user",
    }

    def __init__(self, colour, blacklist, xb, user_agent, code, settings):
        self.colour = colour
        self.logger = None
        self.request = None
        self.download = None
        self.manager = None
        self.save = False
        self.xb = xb
        self.record = RecordManager()
        self.settings = settings
        self.accounts = []  # 账号数据
        self.quit = False
        self._number = 0  # 账号数量
        self._data = {}  # 其他配置数据
        self.mark = None
        self.nickname = None
        self.blacklist = blacklist
        self.user_agent = user_agent
        self.code = code

    def configuration(self, **kwargs):
        if not self.check_config():
            self.quit = True
            return
        self.initialize(**kwargs)
        self.set_parameters()

    def check_config(self):
        # print("正在读取配置文件！")
        settings = self.settings.read()
        if not isinstance(settings, dict):
            return False
        try:
            return self.read_data(settings)
        except KeyError as e:
            print(f"读取配置文件发生错误: {e}")
            select = input(
                "配置文件存在错误！是否需要重新生成默认配置文件？（Y/N）")
            if select == "Y":
                self.settings.create()
            print("程序即将关闭，请检查配置文件后再重新运行程序！")
            return False

    def read_data(self, settings):
        def get_data(key, value, items, index=False):
            for i in items:
                key[i] = value[i][0] if index else value[i]

        self.accounts = settings["accounts"]
        self._number = len(self.accounts)
        get_data(
            self._data,
            settings,
            ("mix",
             "root",
             "folder",
             "name",
             "time",
             "split",
             "save",
             "log",
             "retry",
             "chunk",
             "max_size",
             "music",
             "cookie",
             "dynamic",
             "original",
             "proxies",
             "download",
             "thread",
             "pages",
             ))
        self.save = bool(self._data["save"])
        # print("读取配置文件成功！")
        return True

    def batch_acquisition(self):
        self.manager = Cache(
            self.logger,
            self._data["root"],
            type_="UID",
            mark=self.mark,
            name=self.nickname)
        save, root, params = self.record.run(
            self._data["root"], format_=self._data["save"])
        self.user_works_batch(save, root, params)
        self.logger.info("已退出批量下载账号作品模式")

    def user_works_batch(self, save, root, params):
        self.logger.info(f"共有 {self._number} 个账号的作品等待下载")
        for index in range(self._number):
            self.get_account_works(
                index + 1,
                *self.accounts[index],
                save,
                root,
                params)

    def user_works_solo(self, save, root, params):
        while True:
            url = input("请输入账号链接: ")
            if not url:
                break
            elif url in ("Q", "q",):
                self.quit = True
                break
            links = self.request.run_alone(url, user=True)
            for i in links:
                if not self.get_account_works(
                        0,
                        "",
                        i,
                        "post",
                        "",
                        "",
                        save,
                        root,
                        params):
                    if failed():
                        continue
                    break

    def get_account_works(
            self,
            num: int,
            mark: str,
            url: str,
            mode: str,
            earliest: str,
            latest: str, save, root: str, params: dict, api=False):
        self.request.mark = mark
        self.request.url = url
        self.request.api = mode
        self.request.earliest = earliest
        self.request.latest = latest
        if not self.request.run(f"第 {num} 个" if num else ""):
            return False
        old_mark = m["mark"] if (
            m := self.manager.cache.get(
                self.request.uid.lstrip("UID"))) else None
        self.manager.update_cache(
            self.request.uid.lstrip("UID"),
            self.request.mark,
            self.request.name)
        self.download_account_works(num, save, root, params, old_mark, api)
        return True

    def download_account_works(
            self,
            num,
            save,
            root: str,
            params: dict,
            old_mark, api=False):
        self.download.nickname = self.request.name
        self.download.uid = self.request.uid
        self.download.mark = self.request.mark
        self.download.favorite = self.request.favorite
        with save(root, name=f"{self.download.uid}_{self.download.mark}", old=old_mark, **params) as data:
            self.download.data = data
            self.download.run(f"第 {num} 个" if num else "",
                              self.request.video_data,
                              self.request.image_data, api)

    def single_acquisition(self, url):
        save, root, params = self.record.run(
            self._data["root"], format_=self._data["save"])
        with save(root, **params) as data:
            self.download.data = data

            ids = self.request.run_alone(url)
            if not ids:
                self.logger.error(f"{url} 获取作品ID失败")
                sys.exit()
            self.download.tiktok = self.request.tiktok
            for i in ids:
                self.download.run_alone(i)
        # self.logger.info("已退出单独下载链接作品模式")

    def initialize(
            self,
            root="./",
            folder="Log",
            name="%Y-%m-%d %H.%M.%S",
            filename=None,
    ):
        self.logger = LoggerManager(
            self.colour) if self._data["log"] else BaseLogger(
            self.colour)
        self.logger.root = root  # 日志根目录
        self.logger.folder = folder  # 日志文件夹名称
        self.logger.name = name  # 日志文件名称格式
        self.logger.run(filename=filename)
        self.request = Acquirer(self.logger, self.xb, self.colour)
        self.download = Downloader(
            self.logger,
            None,
            self.xb,
            self.colour,
            self.blacklist,
            self._data["thread"])
        self.request.clean.set_rule(TEXT_REPLACEMENT, True)  # 设置文本过滤规则
        self.download.clean.set_rule(TEXT_REPLACEMENT, True)  # 设置文本过滤规则
        self.mark = "mark" in self._data["name"]
        self.nickname = "nickname" in self._data["name"]
        self.request.initialization(self.user_agent, self.code)
        self.download.initialization(self.user_agent, self.code)

    def set_parameters(self):
        self.download.root = self._data["root"]
        self.download.folder = self._data["folder"]
        self.download.name = self._data["name"]
        self.download.music = self._data["music"]
        self.request.time = self._data["time"]
        self.download.time = self.request.time
        self.download.split = self._data["split"]
        self.request.cookie = self._data["cookie"]
        self.download.cookie = self.request.cookie
        self.download.dynamic = self._data["dynamic"]
        self.download.original = self._data["original"]
        self.request.proxies = self._data["proxies"]
        self.download.proxies = self.request.proxies
        self.download.download = self._data["download"]
        self.request.retry = self._data["retry"]
        self.download.retry = self._data["retry"]
        self.download.chunk = self._data["chunk"]
        self.download.max_size = self._data["max_size"]
        self.request.pages = self._data["pages"]

    @check_save
    def comment_acquisition(self):
        save, root, params = self.record.run(
            self._data["root"], type_="comment", format_=self._data["save"])
        while True:
            url = input("请输入作品链接: ")
            if not url:
                break
            elif url.upper() == "Q":
                self.quit = True
                break
            ids = self.request.run_alone(url)
            if not ids:
                self.logger.error(f"{url} 获取作品ID失败")
                continue
            for i in ids:
                name = f"作品{i}_评论数据"
                with save(root, name=name, **params) as data:
                    self.request.run_comment(i, data)
                self.logger.info(f"作品评论数据已储存至 {name}")
        self.logger.info("已退出采集作品评论数据模式")

    def mix_acquisition(self):
        self.manager = Cache(
            self.logger,
            self._data["root"],
            type_="MIX",
            mark=self.mark,
            name=self.nickname)
        save, root, params = self.record.run(
            self._data["root"], type_="mix", format_=self._data["save"])
        select = prompt("请选择合集链接来源", ("使用 mix 参数内的合集链接(推荐)",
                                               "手动输入待采集的合集链接"), self.colour.colorize)
        if select == "1":
            self.mix_batch(save, root, params)
        elif select == "2":
            self.mix_solo(save, root, params)
        elif select.upper() == "Q":
            self.quit = True
        self.logger.info("已退出批量下载合集作品模式")

    def get_mix_info(self, id_: str, collection=False):
        data = id_ if collection else self.download.get_data(id_)
        if not data:
            self.logger.info(f"{id_} 获取合集信息失败")
            return False
        mix_info = self.request.run_mix(data)
        if not isinstance(mix_info, list):
            self.logger.info(f"{id_} 获取合集信息失败")
            return False
        return mix_info

    def download_mix(self, mix_info, save, root, params, mark=None, api=False):
        if isinstance(mark, str):
            mix_info[1] = mark or mix_info[1]
        else:
            mix_info[1] = input(
                "请输入合集标识(直接回车使用合集标题作为合集标识): ") or mix_info[1]
        self.download.nickname = mix_info[2]
        self.download.mark = mix_info[1]
        old_mark = m["mark"] if (
            m := self.manager.cache.get(
                mix_info[0])) else None
        self.manager.update_cache(*mix_info)
        with save(root, name=f"MIX{mix_info[0]}_{mix_info[1]}", old=old_mark, **params) as data:
            self.download.data = data
            self.download.run_mix(
                f"MIX{mix_info[0]}_{mix_info[1]}",
                self.request.mix_total, api)

    def mix_solo(self, save, root, params):
        while True:
            url = input("请输入合集作品链接: ")
            if not url:
                break
            elif url in ("Q", "q",):
                self.quit = True
                break
            ids = self.request.run_alone(url, "合集ID", mix=True)
            if not ids:
                self.logger.error(f"{url} 获取作品ID或合集ID失败")
                continue
            if isinstance(ids, tuple):
                mix_id = True
                ids = ids[0]
            else:
                mix_id = False
            for i in ids:
                if not (info := self.get_mix_info(i, mix_id)):
                    continue
                self.download_mix(info, save, root, params)

    def mix_batch(self, save, root, params):
        for mark, url in self._data["mix"]:
            id_ = self.request.run_alone(url, "合集ID", solo=True, mix=True)
            if not id_:
                self.logger.error(f"{url} 获取作品ID或合集ID失败")
                continue
            if isinstance(id_, tuple):
                mix_id = True
                id_ = id_[0]
            else:
                mix_id = False
            if not (info := self.get_mix_info(id_[0], mix_id)):
                continue
            self.download_mix(info, save, root, params, mark)

    def accounts_user(self):
        save, root, params = self.record.run(
            self._data["root"], type_="user", format_=self._data["save"])
        for i in self.accounts:
            self.request.url = i[1]
            self.logger.info(f"{i[1]} 开始获取账号数据")
            data = self.request.run_user()
            if not data:
                self.logger.warning(f"{i[1]} 获取账号数据失败")
                continue
            with save(root, name="UserData", **params) as file:
                self.request.save_user(file, data)

    def alone_user(self):
        save, root, params = self.record.run(
            self._data["root"], type_="user", format_=self._data["save"])
        while True:
            url = input("请输入账号链接: ")
            if not url:
                break
            elif url in ("Q", "q",):
                self.quit = True
                break
            ids = self.request.run_alone(url, user=True)
            if not ids:
                continue
            for i in ids:
                self.request.url = i
                self.logger.info(f"{i} 开始获取账号数据")
                data = self.request.run_user()
                if not data:
                    self.logger.warning(f"{i} 获取账号数据失败")
                    continue
                with save(root, name="UserData", **params) as file:
                    self.request.save_user(file, data)

    @check_save
    def user_acquisition(self):
        def choose_mode() -> str:
            return prompt(
                "请选择账号链接来源",
                ("使用 accounts 参数内的账号链接",
                 "手动输入待采集的账号链接"), self.colour.colorize)

        if (m := choose_mode()) == "1":
            self.accounts_user()
        elif m == "2":
            self.alone_user()
        elif m.upper() == "Q":
            self.quit = True
        self.logger.info("已退出批量采集账号数据模式")

    def run(self, url=""):
        self.configuration()
        if url:
            self.single_acquisition(url)
        else:
            self.batch_acquisition()
        # self.logger.info("程序运行结束")
