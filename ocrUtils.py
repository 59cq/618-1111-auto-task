import easyocr
import numpy as np
from fnmatch import fnmatch
import re
from numpy.core.fromnumeric import take
import adbUtils

TASK_BUTTON_TEXT = ('去完成', '去浏览', '去挑选', '去开卡', '去兑换')


def getActivityEntrance(image_path):
    pass


def getTask(image_path, scale=1):
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext(image_path, batch_size=100)
    tasks = []
    for text in result:
        if text[1] in TASK_BUTTON_TEXT:
            x = int(np.mean(list(zip(*text[0][:]))[0]))
            y = int(np.mean(list(zip(*text[0][:]))[1]))
            task = [[x, y], text[1], -1, -1, 'description']
            # 找到任务描述和任务进度
            distence_progress = 10000
            distence_description = 10000
            for text_ in result:
                if fnmatch(text_[1], '*(*/*)*'):
                    y_ = int(np.mean(list(zip(*text_[0][:]))[1]))
                    distence = np.abs(y - y_)
                    if distence < distence_progress:
                        doneCnt = int(re.findall(r'\d+', re.findall(r'\(\d+\/', text_[1])[0])[0])
                        totalCnt = int(re.findall(r'\d+', re.findall(r'\/\d+\)', text_[1])[0])[0])
                        task[2] = doneCnt
                        task[3] = totalCnt
                        distence_progress = distence
                else:
                    y_ = int(np.mean(list(zip(*text_[0][:]))[1]))
                    distence = np.abs(y - y_)
                    if distence < distence_description and y < y_:  # 描述在进度下面
                        task[4] = text_[1]
                        distence_description = distence
            task[0][0] = int(task[0][0] * (1 / scale))
            task[0][1] = int(task[0][1] * (1 / scale))
            tasks.append(task)

    res = (0, tasks)

    return res