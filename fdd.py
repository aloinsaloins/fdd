import sys
import os
import argparse
import time
import glob
import mimetypes
import filecmp
from concurrent.futures import ThreadPoolExecutor
import copy
import datetime

parser = argparse.ArgumentParser()

parser.add_argument("dir1", nargs='?', default="-")
parser.add_argument("dir2", nargs='?', default="-")


def diffFile(list):
    resultList = []
    popedDeque = copy.copy(list)
    for index, content in enumerate(list):

        list.remove(content)
        if popedDeque:
            popedDeque.remove(content)

        if not popedDeque:
            return resultList

        sameList = [content]
        for content2 in (reversed(popedDeque)):
            if filecmp.cmp(content, content2):
                sameList.append(content2)
                # 同じものを比較しないにように削除
                popedDeque.remove(content2)
                list.remove(content2)
        if len(sameList) > 1:
            resultList.append(sameList)

    return resultList


def printSameFiles(result, args):
    for i in result.result():
        print("The following files are same:")
        for j in i:
            fileSize = str(os.path.getsize(j)) + "byte"
            timeStamp = str(
                datetime.datetime.fromtimestamp(os.path.getatime(j)))
            j = j + " (" + fileSize + ", " + timeStamp + " )"
            j = j.replace(args.dir1, "")
            print("- " + j)


def main():
    try:
        args = parser.parse_args()
    except Exception as e:
        error_type = type(e).__name__
        sys.stderr.write("{0}: {1}\n".format(error_type, e.message))
        sys.exit(1)

    if args.dir1 is None:
        return

    fileList = glob.glob(args.dir1 + '/*')

    textList = []
    imageList = []
    vdeoList = []
    applicationList = []

    target = r'/'
    for file in fileList:
        mime = mimetypes.guess_type(file)
        idx = mime[0].find(target)
        type = mime[0][:idx]
        if type == "text":
            textList.append(file)
        elif type == "image":
            imageList.append(file)
        elif type == "video":
            vdeoList.append(file)
        elif type == "application":
            applicationList.append(file)

    with ThreadPoolExecutor(max_workers=4) as execuor:
        if len(textList) > 1:
            result = execuor.submit(diffFile, textList)
            printSameFiles(result, args)
        if len(imageList) > 1:
            result = execuor.submit(diffFile, imageList)
            printSameFiles(result, args)
        if len(imageList) > 1:
            result = execuor.submit(diffFile, vdeoList)
            printSameFiles(result, args)
        if len(imageList) > 1:
            result = execuor.submit(diffFile, applicationList)
            printSameFiles(result, args)


if __name__ == "__main__":
    main()
