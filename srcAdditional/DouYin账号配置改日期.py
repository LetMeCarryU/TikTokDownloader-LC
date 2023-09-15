"""
["Candy", "https://www.douyin.com/user/MS4wLjABAAAAyg_4ABlCrTIlP2c0hYRuJ-azrLHhzZd1OekyWZV05Ik", "post", "2023/07/24", ""], 
"""
from pathlib import Path

"""
遍历settings.txt文件，检查每一项的第四个是不是dateStr
"""


def main():
    print("--------------------------------------------------------------------------")
    file_path = Path(__file__).resolve()
    dir_path = file_path.parent.parent
    settingTxtPath = Path.joinpath(dir_path, "settings.txt")
    print(f"配置文件路径 {settingTxtPath}")
    dateStr = '"2023/09/01"'

    with open(settingTxtPath, mode='r', encoding='utf-8') as file:
        lineList = file.readlines()
    newLines = []
    for key, line in enumerate(lineList):
        lines = line.split(", ")
        lines[3] = dateStr
        newLines.append(", ".join(lines))

    # 覆写文件
    with open(settingTxtPath, mode='w', encoding='utf-8') as file:
        file.write("".join(newLines))
    print("done")


if __name__ == '__main__':
    main()
