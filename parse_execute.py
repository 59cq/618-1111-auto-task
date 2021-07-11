# keyword 京东 jingdong
# keyword 淘宝 taobao.taobao


import os
import re
import time
import sys
import cv2
import ocrUtils
import adbUtils
import json
import myLog
from fnmatch import fnmatch

jsonSubtaskKey_to_adbKeycode = {
    'back':adbUtils.KEYCODE_BACK,
    'enter':adbUtils.KEYCODE_ENTER,
    'home':adbUtils.KEYCODE_HOME,
    'menu':adbUtils.KEYCODE_MENU,
    'esc':adbUtils.KEYCODE_ESCAPE
}

def getJsonObj(json_path):
    data = json.load(open(json_path, encoding='UTF-8'))
    # todo 格式检验
    return data


def processSubTask(task):
    log.logPrint('子操作：{} {}'.format(task['name'], task['value']))
    if task['name'] == 'touch':
        res = adbUtils.touch(task['value'])
        return res
    if task['name'] == 'key':
        res = adbUtils.key(jsonSubtaskKey_to_adbKeycode[task['value']])
        return res
    if task['name'] == 'delay':
        time.sleep(task['value'])
        return (0, '')
    log.logPrint('未知子操作')
    return(1, 'unknow sub task: {}'.format(task))


def processTask(tasksTypes, task):
    log.logPrint('开始执行任务：{}'.format(task))
    log.logPrint('本任务进度：{} / {}'.format(task[2], task[3]))
    global appActivity
    taskType = None
    isFindFitType = False
    # 找到json中定义的任务类型
    for type in tasksTypes:
        for condition in type['keywrod_Description']: # 满足任意一条即可
            if fnmatch(task[4], condition):
                taskType = type
                isFindFitType = True
                break
        if isFindFitType == True:
            break
    log.logPrint('任务类型：{}'.format(taskType))

    # 未找到则不执行此任务
    if isFindFitType is False:
        log.logPrint('不支持的任务：未在json中找到匹配样式，跳过')
        return(1, 'can not fit any type in json')

    # 找到但是button名不匹配也不执行
    if taskType['button_Name'] != task[1]:
        log.logPrint('不支持的任务：任务按钮名与json中样式不匹配，跳过')
        return(1, 'button Name not fit in page: {}, in json: {}'.format(task[1], taskType['button_Name']))

    # 如果任务已经做完，根据json判断是否需要刷新任务列表（任务完成后消失，打乱排列）
    if task[2] == task[3]:
        log.logPrint('本组任务已经完成')
        if taskType['needRefresh'] is True:
            log.logPrint('需要刷新任务列表')
            return (2, 'need refresh tasks list')
        else:
            return (0, 'this tasks has done')

    # 点击任务按钮, 如果json中没有定义按钮位置，使用ocr检测到的位置
    button_position = taskType['button_Position']
    if button_position[0] == 0 and button_position[1] == 0:
        button_position = task[0]
    res = adbUtils.touch(button_position)
    if res[0] != 0:
        return res

    # 等待延时结束
    delay = taskType['delay_after_touch']
    time.sleep(delay)
    log.logPrint('等待任务延时：{}s'.format(delay))

    # 进行子操作，如json中 subTasks 为空，则不做操作
    for subTask in taskType['subTasks']:
        res = processSubTask(subTask)
        if res[0] < 0:
            return res

    # 延时结束，返回
    adbUtils.key(adbUtils.KEYCODE_BACK)
    log.logPrint('延时结束，返回任务列表')
    time.sleep(switchPageDelay)

    # 检查是否跳转到了其他app
    res = adbUtils.checkoutCurrentActivity(appActivity)
    if res[0] != 0:
        return res
    if False == res[1]:
        log.logPrint('未处于正确的应用，再次尝试返回')
        adbUtils.key(adbUtils.KEYCODE_BACK)
        time.sleep(switchPageDelay)
        res = adbUtils.checkoutCurrentActivity(appActivity)
        if res[0] != 0:
            return res
        if False == res[1]:
            log.logPrint('无法回到正确的应用')
            return(-1, 'can not back to correct activity')

    # 检查Fragment是否正确，即是否在任务列表页面
    res = adbUtils.getFragmentStack(appPackage)
    if res[0] != 0:
        return res
    if res[1][0] != activityFragment:
        log.logPrint('未能回到活动页面，再次尝试返回')
        adbUtils.key(adbUtils.KEYCODE_BACK)
        time.sleep(switchPageDelay)
        res = adbUtils.getFragmentStack(appPackage)
        if res[0] != 0:
            return res
        if res[1][0] != activityFragment:
            log.logPrint('无法回到正确的页面')
            return(-1, 'can not back to correct fragment')

    return (0, '')



def DEAL_ERROR(result):
    msg = {'code: {} , detail: {}'.format(result[0], result[1])}
    log.logPrint(msg)
    log.addMessage(msg)
    exit(0)


# result = adbUtils.getCurrentActivity()

# log.logPrint(result[1])


RULL_FILE = './jingdong_21_618.json'  #  sys.argv[1]

# 初始化log
log = myLog.myLog('./logPer.json', './logGlo.json')

def main():
    jsonObj = getJsonObj(RULL_FILE)
    
    global homeFragment
    global activityFragment

    global platform 
    global appActivity
    global appPackage
    global phoneIP
    global phonePort
    global switchPageDelay
    global activityInterface
    global tasksInterface
    global tasksTypes
    platform = jsonObj['keyword']
    appActivity = jsonObj['appActivity']
    appPackage = jsonObj['appPackage']
    phoneIP = jsonObj['phoneIP']
    phonePort = jsonObj['phonePort']
    switchPageDelay = jsonObj['switchPageDelay']
    activityInterface = jsonObj['activityPageInterface']
    tasksInterface = jsonObj['tasksPageInterface']
    tasksTypes = jsonObj['tasksTypes']

    startState = jsonObj['startState']

    # 连接手机
    res = adbUtils.connectPhone(phoneIP, phonePort)
    if res[0] != 0:
        DEAL_ERROR(res)
    log.logPrint('连接手机成功：{}:{}'.format(phoneIP, phonePort))
    
    # 如果json未指定package，自动获得app package
    if appPackage == "":
        res = adbUtils.getPackage(platform)
        if res[0] != 0:
            DEAL_ERROR(res)
        appPackage = res[1]
    log.logPrint('获得应用包名：{}'.format(appPackage))

    # 获得启动 app activity
    if appActivity == '':
        res = adbUtils.getStartActivity(platform)
        if res[0] != 0:
            DEAL_ERROR(res)
        appActivity = res[1]
    log.logPrint('获得启动activity：{}'.format(appActivity))

    if startState != "activityPage":
        # 启动app
        res = adbUtils.startApp(appActivity)
        if res[0] != 0:
            DEAL_ERROR(res)
        log.logPrint('成功启动应用')

        time.sleep(4)
        res = adbUtils.getFragmentStack(appPackage)
        if res[0] != 0:
            DEAL_ERROR(res)
        homeFragment = res[1][0]

        # 进入活动页面
        activityInterfacePosition = None
        if activityInterface['position'][0] == 0 and activityInterface['position'][1] == 0:
            # TODO 通过ocr识别文字找到入口
            DEAL_ERROR((1, 'TODO 通过ocr识别文字找到入口'))
            res = adbUtils.getScreen(downScale=1)
            if res[0] != 0:
                DEAL_ERROR(res)
            image_dir = res[1]
            ocrUtils.getActyvityEntrance(image_dir)
            pass
        else:
            activityInterfacePosition = activityInterface['position']
        res = adbUtils.touch(activityInterfacePosition)
        if res[0] != 0:
            DEAL_ERROR(res)
        log.logPrint('尝试进入活动页面')

        time.sleep(5)
        # 检测是否切换新的fragment（活动页面）
        res = adbUtils.getFragmentStack(appPackage)
        if res[0] != 0:
            DEAL_ERROR(res)
        homeFragment_ = res[1][0]
        if homeFragment == homeFragment_:
            log.logPrint('进入活动页面失败，再次尝试')
            res = adbUtils.touch(activityInterfacePosition)  # 再次尝试点击
            if res[0] != 0:
                DEAL_ERROR(res)
            time.sleep(5)
            res = adbUtils.getFragmentStack(appPackage)  # 再次验证
            if res[0] != 0:
                DEAL_ERROR(res)
            homeFragment_ = res[1][0]
            if homeFragment == homeFragment_:
                log.logPrint('未能成功进入活动页面')
                res = (-1, 'can not get into activity page after 2 attempt')
                DEAL_ERROR(res)
        log.logPrint('进入活动页面成功')
    
    # 打开任务页面
    if tasksInterface['position'][0] == 0 and tasksInterface['position'][1] == 0:
        # TODO 通过ocr识别文字找到入口
        DEAL_ERROR((1, 'TODO 通过ocr识别文字找到入口'))
        res = adbUtils.getScreen(downScale=1)
        if res[0] != 0:
            DEAL_ERROR(res)
        image_dir = res[1]
        ocrUtils.getActyvityEntrance(image_dir)
        pass
    else:
        res = adbUtils.touch(tasksInterface['position'])
        if res[0] != 0:
            DEAL_ERROR(res)
    res = adbUtils.getFragmentStack(appPackage)
    if res[0] != 0:
        DEAL_ERROR(res)
    activityFragment = res[1][0]
    log.logPrint('get tasks fragment id {}'.format(activityFragment))
    log.logPrint('打开任务列表页面成功')

    time.sleep(1.5)
    # 探测任务
    res = adbUtils.getScreen(downScale=1)
    if res[0] != 0:
        DEAL_ERROR(res)
    log.logPrint('获取截图成功，开始识别图片文字')

    image_dir = res[1]
    result = ocrUtils.getTask(image_dir, scale=0.5)
    log.logPrint(result)
    tasksList = result[1]
    log.logPrint('识别成功')

    # 开始执行任务
    needRefresh = False # 是否需要使用ocr矫正任务列表

    while not needRefresh:

        for task in result[1]:
            repeat = task[3]
            # TODO 根据json中的repeat设定重复次数
            while task[2] <= repeat:
                res = processTask(tasksTypes, task)
                if res[0] < 0:
                    DEAL_ERROR(res)
                if res[0] == 1: # 不支持的任务，跳过
                    break
                if res[0] == 2:
                    needRefresh = True
                    break
                if res[0] == 0:
                    task[2] += 1
            if needRefresh:
                break
        if needRefresh:
            res = adbUtils.getScreen(downScale=1)
            if res[0] != 0:
                DEAL_ERROR(res)
            image_dir = res[1]
            result = ocrUtils.getTask(image_dir, scale=0.5)
            log.logPrint(result)
            tasksList = result[1]
            needRefresh = False
        else:
            break

    log.logPrint('所有任务均已完成')

main()

