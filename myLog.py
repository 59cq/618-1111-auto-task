import json
import os
import time
import signal
import atexit
import sys
import traceback
import inspect

def singleton(cls):
    _instance = {}

    def inner(*argv):
        if cls not in _instance:
            _instance[cls] = cls(*argv)
        return _instance[cls]

    return inner


@singleton
class myLog(object):
    __TAG = "myLog"
    __classId = 0
    __currentId = '-1'
    
    # Per:单次运行结果
    __logFilePer = ""
    __logDumpPer = {}  # __loadLogFilePer

    # Glo:自定义数据，一般是脚本运行整体进度
    __logFileGlo = ""
    __logDumpGlo = {}

    def __init__(self, logFilePer, logFileGlo):
        self.__classId = id(self)
        self.__print("======== myLog start init... ========")
        self.__logFilePer = logFilePer
        self.__logFileGlo = logFileGlo
        self.__loadLogFilePer()
        self.__loadLogFileGlo()
        self.__initErrorHanlde()
        self.__print("======== myLog start init done ========")

    def logPrint(self, *msgs):
        # 仅供外部使用
        stacks = inspect.stack()
        filename = stacks[1].filename
        function = stacks[1].function
        line = stacks[1].lineno
        print(self.__TAG, self.__classId, '\"{}\", line {}'.format(filename, line), function, ':', *msgs)

    def e(self, *msgs):
        pass

    def w(self, *msgs):
        pass

    def d(self, *msgs):
        pass

# ===============================对log per的操作====================================

    def isComplete(self):
        # 判断脚本任务是否全部完成
        return self.__logDumpPer["complete"]

    def setAllComplete(self):
        # 设置脚本任务已经全部完成
        self.__print('set all complete')
        self.__logDumpPer['complete'] = True

    def isItemComplete(self, id):
        # 判断脚本任务其中一个item是否完成
        if id in self.__logDumpPer['completeIds']:
            return True
        else:
            return False

    def addItemComplete(self, id):
        # 添加一个已经完成的item
        self.__print('add complete id = {}'.format(id))
        self.__logDumpPer['completeIds'].append(id)

    def setValue(self, key, vel):
        # 通用设置值方法
        self.__logDumpPer[key] = vel

    def increaseCnt(self, val=1, isSuccess=True):
        # item完成计数增加（1），不代表处理成功

        if isSuccess:
            self.__logDumpPer["thisSuccessCnt"] += val
            self.__logDumpPer["totalSuccessCnt"] += val
        else:
            self.__logDumpPer["thisFailCnt"] += val
            self.__logDumpPer["totalFailCnt"] += val

        self.__logDumpPer["thisCnt"] += val
        self.__logDumpPer["totalCnt"] += val
        self.__print('increase count + {} , success/fail/all: this = {}/{}/{}, total = {}/{}/{}'.format(val, self.__logDumpPer["thisSuccessCnt"], self.__logDumpPer["thisFailCnt"], self.__logDumpPer["thisCnt"], self.__logDumpPer["totalSuccessCnt"], self.__logDumpPer["totalFailCnt"], self.__logDumpPer["totalCnt"]))

    def isInSkips(self, id):
        # 判断是否是之前跳过的item
        if id in self.__logDumpPer['skipIds']:
            return True
        else:
            return False

    def getSkips(self):
        # 获取所有之前跳过的item
        return self.__logDumpPer['skipIds']

    def addSkip(self, id='-1'):
        # 添加一个跳过（失败）的item, 需要外部限制skips的长度，防止无脑skip（例：断网）
        if id == '-1': # 如果为-1，则添加当前id
            _id = self.__currentId
        else:
            _id = id
        if not self.isInSkips(_id):
            self.__logDumpPer['skipIds'].append(_id)
            self.__print('add skip id :', _id)
        else:
            self.__print('add exists skip id :', _id)

    def removeSkip(self, id):
        # 移除一个跳过的item（本次成功）
        self.__print('remove skip id: {}'.format(id))
        self.__logDumpPer['skipIds'].remove(id)

    def updateCurItem(self, id='-1'):
        # 更新当前正在处理的item
        self.__print('-------------------------------------------------------------------------')
        oldId = self.__currentId
        if id == '-1': # 如果为-1，则从头开始
            self.__currentId = self.__logDumpPer['startId']
        else:
            if self.__logDumpPer['startId'] == '-1': # 第一次执行时为-1
                self.__logDumpPer['startId'] = id
            self.__currentId = id
        self.__print('current id from {} update to {}'.format(oldId, self.__currentId))

    def addMessage(self, msg):
        # 添加一条message（一般是warning，error）
        curTime = time.asctime(time.localtime(time.time()))
        stacks = inspect.stack()
        filename = stacks[1].filename
        function = stacks[1].function
        line = stacks[1].lineno
        _msg = '{} {} line {} {} : {}'.format(curTime, filename, line, function, msg)
        self.__logDumpPer['message'].append(_msg)

# ==============================对log glo的操作==================================

    def isItemInGlo(self, key):
        ret = key in self.__logDumpGlo
        self.__print('item {} {} in log Glo'.format(key, ret))
        return ret

    def setItemValToGlo(self, key, val):
        # 增加或修改一个 log glo 中的 item
        self.__print('set item value: key: {}; value:{}'.format(key, val))
        if self.isItemInGlo(key):
            self.__print('key: {} in log global, modify it form {}'.format(key, self.__logDumpGlo[key]))
        else:
            self.__print('key: {} not in log global, add it'.format(key))
        self.__logDumpGlo[key] = val

# ==============================================================================

    def __print(self, *msgs):
        # print文件外部对本log类方法的调用情况
        stacks = inspect.stack()
        filenameOut = stacks[2].filename
        functionOut = stacks[2].function
        lineOut = stacks[2].lineno
        # filenameIn = stacks[1].filename
        functionIn = stacks[1].function
        # lineIn = stacks[1].lineno
        print(self.__TAG, self.__classId, '\"{}\", line {}'.format(filenameOut, lineOut) , functionOut, '->', functionIn, ':', *msgs)


    def __loadLogFilePer(self):
        self.__print("load logFilePer:", self.__logFilePer, "...")
        self.__logDumpPer["complete"] = False
        self.__logDumpPer["startTime"] = time.asctime(time.localtime(time.time()))
        self.__logDumpPer["stopTime"] = ""
        self.__logDumpPer["startId"] = "-1"
        self.__logDumpPer["stopId"] = "-1"
        self.__logDumpPer["completeIds"] = []
        self.__logDumpPer["skipIds"] = []
        self.__logDumpPer["totalCnt"] = 0
        self.__logDumpPer["totalSuccessCnt"] = 0
        self.__logDumpPer["totalFailCnt"] = 0
        self.__logDumpPer["thisCnt"] = 0
        self.__logDumpPer["thisSuccessCnt"] = 0
        self.__logDumpPer["thisFailCnt"] = 0
        self.__logDumpPer["message"] = []
        self.__logDumpPer["exitCode"] = 0
        if os.path.exists(self.__logFilePer):
            preLog = []
            with open(self.__logFilePer, encoding="UTF-8") as f:
                lines = f.readlines()
                for line in lines:
                    decoded_line = json.loads(line)
                    preLog.append(decoded_line)
            if len(preLog) != 0:
                lastLog = preLog.pop()
                self.__logDumpPer["complete"] = lastLog["complete"]
                self.__logDumpPer["startId"] = lastLog["stopId"]  # in lastLog, stopId didnent finish
                self.__logDumpPer["stopId"] = lastLog["stopId"]
                self.__logDumpPer["completeIds"] = lastLog["completeIds"]
                self.__logDumpPer["skipIds"] = lastLog["skipIds"]
                self.__logDumpPer["totalCnt"] = lastLog["totalCnt"]
                self.__logDumpPer["totalSuccessCnt"] = lastLog["totalSuccessCnt"]
                self.__logDumpPer["totalFailCnt"] = lastLog["totalFailCnt"]
            else:
                self.__print("log file is empty")
        else:
            self.__print("log file not found")
        self.__print(self.__logDumpPer)
        self.__print("load logFilePer done")

    def __loadLogFileGlo(self):
        self.__print("load logFileGlo:", self.__logFileGlo, "...")
        if os.path.exists(self.__logFileGlo):
            preLog = []
            with open(self.__logFileGlo, encoding="UTF-8") as f:
                lines = f.readlines()
                for line in lines:
                    decoded_line = json.loads(line)
                    preLog.append(decoded_line)
            if len(preLog) != 0:
                self.__logDumpGlo = preLog.pop()
            else:
                self.__print("log file Global is empty")
        else:
            self.__print("log file Global not found, create new")

        self.__print(self.__logDumpGlo)
        self.__print("load logFileGlo done")


    def __initErrorHanlde(self):
        self.__print("init error handle...")
        atexit.register(self.__onExit)
        signal.signal(signal.SIGTERM, self.__onSignal)
        signal.signal(signal.SIGINT, self.__onSignal)
        # signal.signal(signal.SIGHUP, self.__onSignal)
        signal.signal(signal.SIGFPE, self.__onSignal)
        signal.signal(signal.SIGSEGV, self.__onSignal)
        # signal.signal(signal.SIGBUS, self.__onSignal)
        signal.signal(signal.SIGABRT, self.__onSignal)
        signal.signal(signal.SIGILL, self.__onSignal)
        # signal.signal(signal.SIGQUIT, self.__onSignal)
        self.__print("init error handle done")

    def __onExit(self):
        self.logPrint("saving log file...") #  使用__print会越界
        self.__logDumpPer["stopId"] = self.__currentId
        self.__logDumpPer["stopTime"] = time.asctime(time.localtime(time.time()))
        with open((self.__logFilePer), "a", encoding="UTF-8") as f:
            f.write(json.dumps(self.__logDumpPer, ensure_ascii=False) + "\r")
        with open((self.__logFileGlo), "w", encoding="UTF-8") as f:
            f.write(json.dumps(self.__logDumpGlo, ensure_ascii=False) + "\r")
        self.logPrint("saving log file done")

    def __onSignal(self, signalnum, __onSignal):
        msg = 'receive signal: {}'.format(signalnum)
        self.logPrint(msg)
        self.addMessage(msg)
        self.__logDumpPer["exitCode"] = signalnum
        exit(0)


