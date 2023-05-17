import logging


# 设置不同级别日志的颜色
colors = {
    logging.DEBUG: "\033[37m",   # 白色
    logging.INFO: "\033[32m",    # 绿色
    logging.WARNING: "\033[33m", # 黄色
    logging.ERROR: "\033[31m",   # 红色
    logging.CRITICAL: "\033[35m" # 紫色
}

class ColoredLevelFormatter(logging.Formatter):
    def format(self, record):
        color = colors.get(record.levelno)
        if color:
            record.levelname = f"{color}{record.levelname}\033[0m"
        return super().format(record)


# 创建一个处理器
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# 设置处理器输出格式
formatter = ColoredLevelFormatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
# 创建一个日志对象
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 将处理器添加到日志对象中
logger.addHandler(handler)

# 输出不同级别的日志
logger.debug("This is a debug message.")
logger.info("This is an information message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
