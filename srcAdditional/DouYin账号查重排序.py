import json
from pathlib import Path

from pypinyin import pinyin, Style
import sys

"""
查重
去空行
拼音排序
["Candy", "https://www.douyin.com/user/MS4wLjABAAAAyg_4ABlCrTIlP2c0hYRuJ-azrLHhzZd1OekyWZV05Ik", "post", "2023/07/24", ""],
"""


def duplicatesFinder(data):
    userURLStrList = []
    userMarkStrList = []
    for key, value in enumerate(data):
        mark = value.split(", ")[0].replace("[", "")
        # urlStr = value.split(",")[1].split("?")[0][29:84]
        urlStr = value.split(", ")[1]
        userMarkStrList.append(mark)
        userURLStrList.append(urlStr)

    dupURLList = list(set([x for x in userURLStrList if userURLStrList.count(x) > 1]))
    dupMarkList = list(set([x for x in userMarkStrList if userMarkStrList.count(x) > 1]))
    return dupURLList, dupMarkList


def main():
    file_path = Path(__file__).resolve()
    dir_path = file_path.parent.parent
    settingTxtPath = Path.joinpath(dir_path, "settings.txt")
    settingJsonPath = Path.joinpath(dir_path, "settings.json")
    print(f"配置文件路径 {settingTxtPath}")

    print("--------------------------------------------------------------------------")
    with open(settingTxtPath, mode='r', encoding='utf-8') as file:
        lineList = file.readlines()
    # 格式化空格,去除注释
    for key, value in enumerate(lineList):
        lineList[key] = value.replace(" ", "").replace(",", ", ").strip()
        if value.startswith("#"):
            lineList[key] = ""
    # 去除空行
    lineList = [line for line in lineList if line.strip()]
    # 去除URL中?以后的部分
    newLines = []
    for line in lineList:
        lines = line.split(", ")
        lines[1] = lines[1].split("?")[0]
        if not lines[1].endswith("\""):
            lines[1] = lines[1] + "\""
        newLines.append(", ".join(lines))

    # 查重
    dup1, dup2 = duplicatesFinder(newLines)

    if len(dup1) > 0:
        print("网址重复如下\n")
        for x in dup1:
            print(x)
        print("--------------------------------------------------------------------------")

    if len(dup2) > 0:
        print("mark重复如下\n")
    for x in dup2:
        print(x)

    if len(dup1) > 0 or len(dup2) > 0:
        sys.exit()
    else:
        print("没发现重复的博主~~")
    print("--------------------------------------------------------------------------")
    # 拼音排序
    newLines.sort(key=lambda keys: [pinyin(i, style=Style.TONE3, strict=False) for i in keys])
    print("拼音排序完成啦~~")
    # 行末加上换行符
    for key, value in enumerate(newLines):
        if not value.endswith("\n"):
            newLines[key] = value + "\n"
    print("--------------------------------------------------------------------------")
    # 覆写文件
    with open(settingTxtPath, mode='w', encoding='utf-8') as file:
        file.write("".join(newLines))
    print("--------------------------------------------------------------------------")
    """
    # 写入json
    # 解决不了反转义字符
    print(f"配置文件路径 {settingJsonPath}")
    with open(settingJsonPath, mode='r', encoding='utf-8') as f:
        settingList = json.load(f)
    settingList["accounts"] = newLines
    with open(settingJsonPath, mode='w', encoding='utf-8') as file:
        json.dump(settingList, file, indent=4, ensure_ascii=False)
    """
    print("done")


if __name__ == '__main__':
    main()
