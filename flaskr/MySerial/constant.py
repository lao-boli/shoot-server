HEADER1 = 0
HEADER2 = 1
HEADER3 = 2

# HEADER 1
CORE_WEB = 0X16
"""靶箱与后端的通信靶箱"""
CORE_GUN = 0X10
"""靶箱与模拟机枪的通信"""

# HEADER 2
ENROLL = 0X00
"""上线提示(注册)信息"""
QUIT = 0X01
"""下线确认信息"""
DATA = 0X10
"""数据信息"""
SET = 0X11
"""设置信息"""

# HEADER 3
UPLINK = 0X10
DOWNLINK = 0X01

# 数据信息帧
# 位置
DATA_TYPE = 3
"""数据类型-轨迹坐标信息或射击信息"""
HIT_RING_NUMBER = 4
AIM_RING_NUMBER = 5
GUN_SHAKING = 6
GUN_SHAKING_RATE = 7
FIRE_SHAKING = 8
FIRE_SHAKING_RATE = 9
AXIS_X_HIGH = 10
"""x坐标百分数整数位"""
AXIS_X_LOW = 11
"""x坐标百分数小数位"""
AXIS_Y_HIGH = 12
"""y坐标百分数整数位"""
AXIS_Y_LOW = 13
"""y坐标百分数小数位"""
TAIL = 14

# 值
CURVE = 0x00
"""数据类型-轨迹坐标"""
SHOOT_DATA = 0x01
"""数据类型-射击数据"""

# 注册信息帧
# 位置
GUN_ID_HIGH = 3
GUN_ID_LOW = 4
TARGET_ID_HIGH = 5
TARGET_ID_LOW = 6
ACK = 8
BULLET = 9

#  值
CONFIRM_ENROLL = 0x00
FRAME_END = 0x99
"""变长数据帧结束标志,当前版本无意义,但需下发消息时需添加"""
