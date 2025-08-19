class Styling:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class SingletonMeta(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
            cls._instance.debug(f"Created Logger singleton")
        else:
            cls._instance.debug("Reused Logger singleton")
        return cls._instance


class Logger(metaclass=SingletonMeta):
    def _log(self, level_name, color, *args, **kwargs):
        print(f"{Styling.BOLD}{color}[{level_name}]{Styling.RESET} ", end = '')
        print(*args, **kwargs)
        print(Styling.RESET, end = '')

    def info(self, *args, **kwargs):
        self._log("INFO", Styling.BRIGHT_GREEN, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._log("WARNING", Styling.BRIGHT_YELLOW, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log("ERROR", Styling.BRIGHT_RED, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self._log("DEBUG", Styling.BRIGHT_CYAN, *args, **kwargs)
