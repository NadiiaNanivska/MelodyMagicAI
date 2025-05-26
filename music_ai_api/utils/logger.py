import logging
import sys
from colorama import init, Fore, Style
from datetime import datetime

init()

class ColoredFormatter(logging.Formatter):
    """Кастомний форматер для додавання кольорів та покращеного форматування логів"""

    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s │ %(threadName)s[%(thread)d] │ %(name)s │ %(levelname)s │ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def format(self, record):
        orig_levelname = record.levelname
        orig_msg = record.msg

        timestamp = f"{Fore.CYAN}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        thread_info = f"{Fore.MAGENTA}{record.threadName}[{record.thread}]{Style.RESET_ALL}"
        logger_name = f"{Fore.YELLOW}{record.name}{Style.RESET_ALL}"
        level_color = self.COLORS.get(record.levelname, '')
        level_name = f"{level_color}{record.levelname:8}{Style.RESET_ALL}"

        if isinstance(record.msg, str):
            if '.mid' in record.msg.lower():
                record.msg = record.msg.replace('.mid', f'{Fore.CYAN}.mid{Style.RESET_ALL}')
            if 'успішно' in record.msg.lower():
                record.msg = record.msg.replace('успішно', f'{Fore.GREEN}успішно{Style.RESET_ALL}')
            if 'помилка' in record.msg.lower():
                record.msg = record.msg.replace('помилка', f'{Fore.RED}помилка{Style.RESET_ALL}')

        record.asctime = timestamp
        record.threadName = thread_info
        record.name = logger_name
        record.levelname = level_name

        result = logging.Formatter('%(asctime)s │ %(threadName)s │ %(name)s │ %(levelname)s │ %(message)s').format(record)

        record.levelname = orig_levelname
        record.msg = orig_msg

        return result

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(ColoredFormatter())
        logger.addHandler(stream_handler)

    return logger