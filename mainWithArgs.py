import argparse
import os
import pathlib

from main import TikTokDownloader


def argParser():
    parser = argparse.ArgumentParser(description='Demo of argparse')
    parser.add_argument('url', metavar='u', type=str, help='链接或者视频ID')
    # parser.add_argument('url', metavar='u', type=str, nargs='+', help='链接或者视频ID')
    parser.add_argument('-a', type=pathlib.Path, default=None, help="链接文本")
    parser.add_argument('-sm', type=str, default=None, help="扫码登陆以获取cookie")
    parser.add_argument('-s', type=str, default=None, help="simulate")
    parser.add_argument('-o', type=str, default=None, help="output")
    args = parser.parse_args()
    # print(args.url)
    tt = TikTokDownloader()
    tt.run(args.url)


def init():
    """
    file_path = Path(__file__).resolve()
    dir_path = file_path.parent
    """
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    os.chdir(dir_path)
    # print("切换工作目录到" + dir_path)


if __name__ == '__main__':
    init()
    argParser()
