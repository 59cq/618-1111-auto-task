import subprocess
import re
import time
import cv2

KEYCODE_HOME = 3
KEYCODE_BACK = 4
KEYCODE_MENU = 82
KEYCODE_ENTER = 66
KEYCODE_ESCAPE = 111




def connectPhone(ip, port=5555):
    cmd = 'adb connect {}:{}'.format(ip, port)
    result = subprocess.getstatusoutput(cmd)
    return result

def getPackage(keyWord):
    cmd = 'adb shell pm list package -3'
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    lines = result[1].split('\n')
    packageName = ''
    for line in lines:
        if keyWord in line:
            packageName = line.split(':')[1]
            return (0, packageName)
    return (-1, 'can not find package name')    

def getStartActivity(keyWord):
    result = getPackage(keyWord)
    if result[0] != 0:
        return result
    package = result[1]
    cmd = 'adb shell dumpsys package {}'.format(package)
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    lines = result[1].split('\n')
    packageActivityName = ''
    for i in range(len(lines)):
        if 'LAUNCHER' in lines[i]:
            part = lines[i - 2].split(' ')
            for str in part:
                if keyWord in str:
                    packageActivityName = str
                    break
            break
    # print(packageActivityName)
    if packageActivityName == '':
        return (1, 'can not find activity name')
    return (0, packageActivityName)

def startApp(packageActivityName):
    cmd = 'adb shell am start -n {}'.format(packageActivityName)
    result = subprocess.getstatusoutput(cmd)
    return result

def getScreen(saveDir='/sdcard/screen.png', pullDir='./screen.png', downScale=1):
    cmd = 'adb shell screencap -p {}'.format(saveDir)
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    cmd = 'adb pull {} {}'.format(saveDir, pullDir)
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    image = cv2.imread(pullDir)
    for i in range(downScale):
        image = cv2.pyrDown(image)
    cv2.imwrite(pullDir, image)
    return (0, pullDir)

def getScreenSize():
    cmd = 'adb shell wm size'
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    sizes = re.findall(r'\d+', result[1])
    return (0, (int(sizes[0]), int(sizes[1])))

def slide(pointS, pointE):
    cmd = 'adb shell input swipe {} {} {} {}'.format(pointS[0], pointS[1], pointE[0], pointE[1])
    result = subprocess.getstatusoutput(cmd)
    return result

def touch(point):
    point_ = [point[0], point[1]]
    result = getScreenSize()
    if result[0] != 0:
        return result
    size = result[1]
    # 如果超出屏幕边界，增加滑动操作
    over_migrant = 50
    slide_len_x = 0
    slide_len_y = 0
    if point[0] > size[0]:
        slide_len_x = -(point[0] - size[0] + over_migrant)
        point_[0] = size[0] - over_migrant
    if point[0] < 0:
        slide_len_x = -(point[0] + over_migrant)
        point_[0] = over_migrant
    if point[1] > size[1]:
        slide_len_y = -(point[1] - size[1] + over_migrant)
        point_[1] = size[1] - over_migrant
    if point[1] < 0:
        slide_len_y = -(point[1] + over_migrant)
        point_[1] = over_migrant
    
    if slide_len_x + slide_len_y != 0:
        result = slide((size[0] // 2, size[1] // 2), (size[0] // 2 + slide_len_x, size[1] // 2 + slide_len_y))
        if result[0] != 0:
            return result
        time.sleep(0.5)
    
    cmd = 'adb shell input tap {} {}'.format(point_[0], point_[1])
    result = subprocess.getstatusoutput(cmd)
    return result

def key(keyCode):
    cmd = 'adb shell input keyevent {}'.format(keyCode)
    result = subprocess.getstatusoutput(cmd)
    return result

def keyInput(str):
    cmd = 'adb shell input keyboard text \'str\''
    result = subprocess.getstatusoutput(cmd)
    return result

def getCurrentActivity():
    cmd = "adb shell dumpsys activity activities | findstr \"cmp=com.\""
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    currentActivity = result[1].split('\n')[0].split('cmp=')[-1].split('=')[0].split(' ')[0]
    return (0, currentActivity)

def checkoutCurrentActivity(targetActivityName):
    res = getCurrentActivity()
    if res[0] != 0:
        return res
    if res[1] == targetActivityName:
        return(0, True)
    return(0, False)

def getFragmentStack(package):
    cmd = "adb shell dumpsys activity {} | findstr \"Fragment\"".format(package)
    result = subprocess.getstatusoutput(cmd)
    if result[0] != 0:
        return result
    str = result[1]
    stack = []

    while str.find('Active Fragments in') != -1:
        index = str.find('Active Fragments in')
        stack.append(str[index + 19: index + 29].split(':')[0])
        str = str[index + 19:]
    
    return (0, stack)

