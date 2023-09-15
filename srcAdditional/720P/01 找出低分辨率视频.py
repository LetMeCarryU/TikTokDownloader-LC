import json
import os
import pprint
from pathlib import Path

import cv2
from dateutil.parser import parse as dateParse


def getFileIdList(path, checkDate):
    # 徐大仙儿er - 2019-06-10 20.04.32 - 6700550805663026439 - 小女子不才，扰公子良久，公子莫怪.mp4
    # 徐大仙儿er - 2019-06-10 20.04.32 - 小女子不才，扰公子良久，公子莫怪.mp4
    # 徐大仙儿er - 小女子不才，扰公子良久，公子莫怪.mp4
    returnList = []
    for root, dirs, files in os.walk(path):
        print(root)
        if "DownloadAlone" in root or "images" in root:
            continue
        if len(files) == 0:
            continue
        for file in files:
            if not file.endswith(".mp4"):
                continue
            fileNameList = file.split(" - ")
            publishTime = fileNameList[1]
            if not publishTime.startswith("20") and len(publishTime) == 19:
                continue
            else:
                if dateParse(publishTime[0:10]) <= dateParse(checkDate):
                    continue

            tempList = []
            fileFullName = os.path.join(root, file)
            if len(fileNameList) > 3:
                vid = fileNameList[2]
                if vid.isdigit() and len(vid) == 19:
                    tempList.append(vid)
                    tempList.append(file)
                    tempList.append(fileFullName)
                    # tempList = [vid,file,绝对文件名]
                    returnList.append(tempList)

    return returnList


def getResolution(path):
    cap = cv2.VideoCapture(path)
    # 获取视频分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 关闭视频流
    cap.release()
    print(width, height)
    return width, height


def main():
    """
    下载目录中拿到指定日期之后的文件存到idA
    """
    # 文件路径
    checkFilePath = "F:\\DouYin\\DownloadA"
    file_path = Path(__file__).resolve()
    dir_path = file_path.parent
    aPath = Path.joinpath(dir_path, "idA.json")

    fileList = getFileIdList(checkFilePath, "2018-09-13")
    print("----------------------------------------------")
    print(f"fileList: {len(fileList)}")

    # 获取idB文本中已经处理过的文件ID
    idBPath = Path.joinpath(dir_path, "idB.txt")
    with open(idBPath, mode='r', encoding='utf-8') as file:
        idBList = file.readlines()
    for key, line in enumerate(idBList):
        idBList[key] = idBList[key].strip()
    print("----------------------------------------------")
    print(f"len(idBList): {len(idBList)}")

    # 减去idBList得到没处理过,再检查分辨率不够的放到cList
    cList = []
    for key, file in enumerate(fileList):
        # file = [vid,file,绝对文件名]
        if not file[0] in idBList:
            print(file[1])
            width, height = getResolution(file[2])
            if width < 1080 or height < 1080:
                cList.append(file)
    print("----------------------------------------------")
    print(f"len(idCList): {len(cList)}")

    # 把cList存到aPath
    with open(aPath, mode='w', encoding='utf-8') as file:
        json.dump(cList, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
