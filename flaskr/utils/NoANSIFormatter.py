import logging
import re


class NoANSIFormatter(logging.Formatter):
    """
    去除日志中的ansi代码.\n
    sqlalchemy 的原生日志的record.levelname会包含ansi字符，而作为文件log时，这并不需要。故需要去除

    """
    def format(self, record):
        ansicode_pattern = re.compile(r'\033\[(?:\d{1,3};?)+m')
        record.levelname = ansicode_pattern.sub('', record.levelname)
        return super().format(record)

