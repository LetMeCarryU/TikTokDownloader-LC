import json
import os
import pathlib
import subprocess
import sys
from time import sleep

import send2trash

import cv2
import winsound


def getResolution(path):
    cap = cv2.VideoCapture(path)
    # 获取视频分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 关闭视频流
    cap.release()
    return width, height


def sleepT(msg, sleepSeconds):
    while sleepSeconds > 0:
        print(f"\r{msg} sleeping…… %2d 秒" % sleepSeconds, end='')
        sleep(1)
        sleepSeconds = sleepSeconds - 1
    print()


def download(videoUrl):
    cmd2 = 'cd /d D:\\mywork\\PycharmProjects\\TikTokDownloader-Alone  && python mainWithArgs.py ' + videoUrl + ' && exit'
    p = subprocess.Popen(cmd2, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    print("重新下载 " + videoUrl)
    return p


def delete2trash(fullPathFile):
    if pathlib.Path(fullPathFile).exists():
        send2trash.send2trash(fullPathFile)


def main():
    # 下载目录中拿到指定日期之后的文件存到idA
    file_path = pathlib.Path(__file__).resolve()
    dir_path = file_path.parent
    idAPath = pathlib.Path.joinpath(dir_path, "idA.json")
    idBPath = pathlib.Path.joinpath(dir_path, "idB.txt")

    with open(idAPath, mode='r', encoding='utf-8') as f:
        idAList = json.load(f)
    print(f"idAList: {len(idAList)}")
    # 获取idB文本中已经处理过的文件ID
    idBPath = pathlib.Path.joinpath(dir_path, "idB.txt")
    with open(idBPath, mode='r', encoding='utf-8') as file:
        idBList = file.readlines()
    for key, line in enumerate(idBList):
        idBList[key] = idBList[key].strip()
    # 分辨率<1080的文件
    for key, file in enumerate(idAList):
        # file = [vid,file,绝对文件名]
        print("-------------------------------------------------------")
        print(f"进度{key + 1}/{(len(idAList))}个 vid {file[0]} file {file[1]}")
        # 有时候也会执行失败，获取不到twwid，所以需要把已经执行的先存起来
        if file[0] in idBList:
            print("已经在idBList")
            continue
        # 发送过请求的都存起来,
        with open(idBPath, mode='a', encoding='utf-8') as f:
            f.write("".join(file[0] + "\n"))
        # 发送请求
        videoUrl = "https://www.douyin.com/video/" + file[0]
        p = download(videoUrl)
        p.wait()
        # 获取子进程中的full_path
        subOutPut, subErr = p.communicate()
        subOutPutStr = subOutPut.decode('utf-8')
        subErrStr = subErr.decode('utf-8')
        if subOutPutStr:
            print(f"subOutPut: {subOutPutStr}")
        if subErrStr:
            print(f"subErr: {subErrStr}")
            for i in range(5):
                winsound.Beep(frequency=4500, duration=600)
            sys.exit()
        if "full_path:4253|14151:" in subOutPutStr:
            newFileFullName = subOutPutStr.split(":4253|14151:")[1]

            # 比对重新下载的和checkPath之中的差异。如果文件体积增大或者分辨率增大了，替换过去。如果一样或者变小，删掉。
            oFileSize = os.path.getsize(file[2])
            newFileSize = os.path.getsize(newFileFullName)

            if newFileSize > oFileSize:  # 新下载的比较大
                delete2trash(file[2])
                os.rename(newFileFullName, file[2])
                print(f"{newFileSize}>{oFileSize}")
                print("替换 " + file[2])
            elif newFileSize <= oFileSize:
                delete2trash(newFileFullName)
                print("删除 " + newFileFullName)

    print("-------------------------------------------------------")
    print("done")


if __name__ == '__main__':
    main()
