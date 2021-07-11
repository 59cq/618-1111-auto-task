# 618、双十一刷任务脚本

## 简介

从资本手中夺回我们的时间！

看过了很多相关的脚本，都是针对性的。想开发一款通用脚本，使用配置文件来兼容各个平台，各个电商活动。

## 环境

- python3.9
- android adb工具

## 开发进度

2021.07.11: 目前处于测试阶段, 由于21年618已过, 暂时无测试环境, 项目暂停

## 配置文件解析

```json
{
    "keyword": "jingdong",		//平台名，用于定位和启动app
    "appPackage":"",			//包名，同样用于启动app
    "appActivity": "",			//Activity名
    "phoneIP": "10.10.1.137",	//phone再内网中的ip
    "phonePort": 5555,			//adb端口
    "startState": "activityPage", //首页activity名
    "switchPageDelay": 2,		//页面切换延时
    "activityPageInterface": {	//从首页进入活动页面的入口
        "position": [	//模拟点击的未知
            1000,
            1739
        ],
        "text": "瓜分"//入口关键字，如果没有定义position，使用ocr识别找到入口
    },
    "tasksPageInterface": {	//活动页面的任务列表入口
        "position": [	//入口位置
            931,
            1808
        ],
        "text": "做任务领金币"	//同上
    },
    "tasksTypes": [	//定义几种基本的任务类型
        {	
            "name": "15sView",	//任务名
            "repeat": 0,		//重复次数,如果ocr检测到了任务重复次数,该值会被忽略
            "keywrod_Description": ["浏览15秒最高可得*"],	//任务列表中的关键字,使用ocr定位该类型的任务
            "button_Name": "去完成", //执行该任务的入口,一般是"去完成"按钮
            "button_Position": [	//可有手动定义该按钮,优先使用ocr定位到的位置
                0,
                0
            ],
            "delay_after_touch": 18,	//点击任务"去完成"按钮后的延迟时间,手机反应慢可以适当增加
            "subTasks": [],	//子操作,针对复杂任务,一般浏览任务不需要定义,下面有例子
            "needRefresh": true //该任务完成后是否需要刷新(重新截图使用ocr探测任务),有时候一个任务做完会从任务列表消失,打乱其他任务的排序,入口的位置会改变
        },
        {
            "name": "8sView",
            "repeat": 0,
            "keywrod_Description": ["浏览8秒*", "参与8秒可得*"],
            "button_Name": "去完成",
            "button_Position": [
                0,
                0
            ],
            "delay_after_touch": 13,
            "subTasks": [],
            "needRefresh": true
        },
        {
            "name": "0sView",
            "repeat": 0,
            "keywrod_Description": ["参与可得*", "成功浏览可得*", "浏览并关注可得*", "逛店可得*"],
            "button_Name": "去完成",
            "button_Position": [
                0,
                0
            ],
            "delay_after_touch": 2,
            "subTasks": [],
            "needRefresh": true
        },
        {
            "name": "0sView_5Addbuy",
            "repeat": 1,
            "keywrod_Description": ["成功浏览加购5个*"],
            "button_Name": "去完成",
            "button_Position": [
                0,
                0
            ],
            "delay_after_touch": 3,
            "subTasks": [	//子操作按顺序执行,在delay_after_touch后
                {
                    "name": "touch",	//触摸操作
                    "value": [			//触摸位置,可以超出屏幕,超出屏幕时自动前置滑动操作
                        462,
                        1127
                    ]
                },
                {
                    "name": "delay",	//延时操作,等待响应,根据手机性能而定
                    "value": 1
                },
                {
                    "name": "key",		//按键操作
                    "value": "back"		//返回键
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "touch",
                    "value": [
                        969,
                        1127
                    ]
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "key",
                    "value": "back"
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "touch",
                    "value": [
                        462,
                        1846
                    ]
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "key",
                    "value": "back"
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "touch",
                    "value": [
                        969,
                        1846
                    ]
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "key",
                    "value": "back"
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "touch",
                    "value": [
                        462,
                        2586
                    ]
                },
                {
                    "name": "delay",
                    "value": 1
                },
                {
                    "name": "key",
                    "value": "back"
                },
                {
                    "name": "delay",
                    "value": 1
                }
            ],
            "needRefresh": true
        },
        {
            "name": "joinVip",
            "repeat": 0,
            "keywrod_Description": ["成功入会可得*"],
            "button_Name": "去完成",
            "button_Position": [
                0,
                0
            ],
            "delay_after_touch": 2,
            "subTasks": [
                {
                    "name": "touch",
                    "value": [
                        536,
                        2210
                    ]
                }
            ],
            "needRefresh": true
        }
    ],
    "process": { //目前没意义(未完成)
        "prcessType": "auto",
        "flow": []
    }
}
```



