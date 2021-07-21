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
import imageProcess

parser = argparse.ArgumentParser()

parser.add_argument("dir1", nargs='?', default="-")
parser.add_argument("output", nargs='?', type=argparse.FileType(
    'w', encoding="utf-8"), default="-")
parser.add_argument("-d", "--dir2", nargs='?', default="-")
parser.add_argument("-s", "--histgram", nargs='?', default='100', type=int, choices=range(0, 100),
                    help="-i integrity, Integrity is 0-100")


def diffImage(list):
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


def diffFiles(list):
    resultList = []
    popedDeque = copy.copy(list)
    for content in list:
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


def printSameFiles(results, args):
    for i in results:
        for j in i.result():
            print("The following files are same:")
            for k in j:
                fileSize = str(os.path.getsize(k)) + "byte"
                timeStamp = str(
                    datetime.datetime.fromtimestamp(os.path.getatime(k)))
                k = k + " (" + fileSize + ", " + timeStamp + " )"
                k = k.replace(args.dir1, "")
                print("- " + k)


def writeSameFiles(results, args):
    with open(args.output.name, args.output.mode) as wFile:
        for i in results:
            for j in i.result():
                wFile.write("The following files are same:" + '\n')
                for k in j:
                    fileSize = str(os.path.getsize(k)) + "byte"
                    timeStamp = str(
                        datetime.datetime.fromtimestamp(os.path.getatime(k)))
                    k = k + " (" + fileSize + ", " + timeStamp + " )"
                    k = k.replace(args.dir1, "")
                    wFile.write("- " + k + '\n')


def main():
    try:
        args = parser.parse_args()
    except Exception as e:
        error_type = type(e).__name__
        sys.stderr.write("{0}: {1}\n".format(error_type, e.message))
        sys.exit(1)

    if args.dir1 is None:
        return

    # ファイルの絶対パスのみを取得
    fileList = [p for p in glob.glob(args.dir1 + '/**', recursive=True)
                if os.path.isfile(p)]

    textList = []
    imageList = []
    vdeoList = []
    applicationList = []

    if args.dir1 is None:
        return

    # ファイルの絶対パスのみを取得
    fileList = [p for p in glob.glob(args.dir1 + '/**', recursive=True)
                if os.path.isfile(p)]

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

    results = []
    with ThreadPoolExecutor(max_workers=4) as execuor:
        if len(textList) > 1:
            result = execuor.submit(diffFiles, textList)
            results.append(result)
        if len(imageList) > 1:
            if args.histgram:
                result2 = execuor.submit(
                    imageProcess.diffImages, imageList, args)
            else:
                result2 = execuor.submit(diffFiles, imageList)
            results.append(result2)
        if len(imageList) > 1:
            result3 = execuor.submit(diffFiles, vdeoList)
            results.append(result3)
        if len(imageList) > 1:
            result4 = execuor.submit(diffFiles, applicationList)
            results.append(result4)
    execuor.shutdown()

    if args.output.name == '<stdout>':
        printSameFiles(results, args)
    else:
        writeSameFiles(results, args)


if __name__ == "__main__":
    main()
