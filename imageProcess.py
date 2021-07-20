from PIL import Image
import cv2
import copy


def diffImages(list, args):
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
            if imagecmp(content, content2) > args.image/100:
                sameList.append(content2)
                # 同じものを比較しないにように削除
                popedDeque.remove(content2)
                list.remove(content2)
        if len(sameList) > 1:
            resultList.append(sameList)
    return resultList


def imagecmp(content, content2):
    img_1 = cv2.imread(content)
    target_hist = cv2.calcHist([img_1], [0], None, [256], [0, 256])

    img_2 = cv2.imread(content2)

    resizedImg_2 = cv2.resize(img_2, dsize=(
        img_1.shape[0], img_1.shape[1]))
    compare_hist = cv2.calcHist([resizedImg_2], [0], None, [256], [0, 256])

    return cv2.compareHist(target_hist, compare_hist, 0)
