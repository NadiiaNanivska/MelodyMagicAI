import logging
import sys
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama for cross-platform color support
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors and improved formatting to log messages"""
    
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
        # Save original values
        orig_levelname = record.levelname
        orig_msg = record.msg

        # Apply colors to different parts
        timestamp = f"{Fore.CYAN}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        thread_info = f"{Fore.MAGENTA}{record.threadName}[{record.thread}]{Style.RESET_ALL}"
        logger_name = f"{Fore.YELLOW}{record.name}{Style.RESET_ALL}"
        level_color = self.COLORS.get(record.levelname, '')
        level_name = f"{level_color}{record.levelname:8}{Style.RESET_ALL}"

        # Modify message with colors if it's a string
        if isinstance(record.msg, str):
            # Highlight file paths
            if '.mid' in record.msg.lower():
                record.msg = record.msg.replace('.mid', f'{Fore.CYAN}.mid{Style.RESET_ALL}')
            # Highlight success messages
            if 'успішно' in record.msg.lower():
                record.msg = record.msg.replace('успішно', f'{Fore.GREEN}успішно{Style.RESET_ALL}')
            # Highlight error-related words
            if 'помилка' in record.msg.lower():
                record.msg = record.msg.replace('помилка', f'{Fore.RED}помилка{Style.RESET_ALL}')

        # Create colored format string
        record.asctime = timestamp
        record.threadName = thread_info
        record.name = logger_name
        record.levelname = level_name

        # Format message
        result = logging.Formatter('%(asctime)s │ %(threadName)s │ %(name)s │ %(levelname)s │ %(message)s').format(record)

        # Restore original values
        record.levelname = orig_levelname
        record.msg = orig_msg

        return result

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # StreamHandler для консолі
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(ColoredFormatter())
        logger.addHandler(stream_handler)
    
    return logger