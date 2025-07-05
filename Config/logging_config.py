import logging
import uuid
from flask import has_request_context, g
from logging.handlers import TimedRotatingFileHandler
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform color support
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with color support for better visibility
    """

    # Define color scheme for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN + Style.DIM,
        'INFO': Fore.GREEN + Style.BRIGHT,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR': Fore.RED + Style.BRIGHT,
        'CRITICAL': Fore.WHITE + Back.RED + Style.BRIGHT
    }

    # Define colors for different parts of the log message
    TIMESTAMP_COLOR = Fore.BLUE + Style.DIM
    REQUEST_ID_COLOR = Fore.MAGENTA + Style.DIM
    CLIENT_ID_COLOR = Fore.CYAN + Style.DIM
    LOGGER_NAME_COLOR = Fore.WHITE + Style.DIM
    RESET = Style.RESET_ALL

    def format(self, record):
        # Get the base formatted message
        log_message = super().format(record)

        # Extract log level color
        level_color = self.COLORS.get(record.levelname, '')

        # Create colored format string
        colored_format = (
            f"{self.TIMESTAMP_COLOR}%(asctime)s{self.RESET} - "
            f"{self.REQUEST_ID_COLOR}%(request_id)s{self.RESET} - "
            f"{self.CLIENT_ID_COLOR}%(user_id)s{self.RESET} - "
            f"{self.CLIENT_ID_COLOR}%(client_id)s{self.RESET} - "
            f"{level_color}%(levelname)s{self.RESET} - "
            f"{self.LOGGER_NAME_COLOR}%(name)s{self.RESET} - "
            f"{level_color}%(message)s{self.RESET}"
        )

        # Create a new formatter with the colored format
        colored_formatter = logging.Formatter(
            colored_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        return colored_formatter.format(record)


class RequestContextFormatter(logging.Formatter):
    """
    Custom formatter that includes request context information
    """

    def format(self, record):
        if has_request_context():
            values = g.get('request_context', {})
            record.request_id = values.get('request_id', 'N/A')
            record.user_id = values.get('user_id', 'N/A')
            record.client_id = values.get('client_id', 'N/A')
        else:
            record.request_id = 'N/A'
            record.user_id = 'N/A'
            record.client_id = 'N/A'
        return super().format(record)


class ColoredRequestContextFormatter(RequestContextFormatter, ColoredFormatter):
    """
    Combined formatter with both request context and color support
    """
    pass


class LoggingConfig:
    """
    Centralized logging configuration
    """

    @staticmethod
    def configure_logging(app):
        """
        Configure logging based on app configuration
        """
        log_file_path = app.config.get("LOG_FILE_PATH")
        log_level_str = app.config.get("LOG_LEVEL", "INFO")
        log_handlers = app.config.get("LOG_HANDLERS", "BOTH")
        enable_colors = app.config.get("LOG_COLORS", True)  # Enable colors by default

        log_level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        log_level = log_level_mapping.get(log_level_str.upper(), logging.INFO)

        # Choose formatter based on color preference
        if enable_colors:
            log_formatter = ColoredRequestContextFormatter(
                '%(asctime)s - %(request_id)s - %(user_id)s - %(client_id)s - %(levelname)s - %(name)s - %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_formatter = log_formatter
        else:
            log_formatter = RequestContextFormatter(
                '%(asctime)s - %(request_id)s - %(user_id)s - %(client_id)s - %(levelname)s - %(name)s - %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_formatter = log_formatter

        # File formatter should never have colors (for log files)
        file_formatter = RequestContextFormatter(
            '%(asctime)s - %(request_id)s - %(user_id)s - %(client_id)s - %(levelname)s - %(name)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(log_level)

        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()

        # Configure handlers based on LOG_HANDLERS setting
        if log_handlers.upper() in ["FILE", "BOTH"]:
            if log_file_path:
                try:
                    file_handler = TimedRotatingFileHandler(
                        log_file_path,
                        when='d',
                        interval=1,
                        backupCount=100
                    )
                    file_handler.setFormatter(file_formatter)  # No colors for file
                    file_handler.setLevel(log_level)
                    logger.addHandler(file_handler)
                except Exception as e:
                    print(f"Warning: Could not configure file handler: {e}")
            else:
                print("Warning: LOG_FILE_PATH not configured, skipping file handler")

        if log_handlers.upper() in ["CONSOLE", "STREAM", "BOTH"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)  # Use colored formatter for console
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)

        # Set third-party loggers to WARNING to reduce noise
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('pymongo').setLevel(logging.WARNING)

        # Use colored logging for the initialization message
        if enable_colors:
            initialization_msg = f"{Fore.GREEN}Logging configuration completed with enhanced colors for better visibility{Style.RESET_ALL}"
            print(initialization_msg)

        logging.info("Logging configuration completed")

    @staticmethod
    def set_request_context(request_id=None, user_id=None, client_id=None):
        """
        Set request context for logging
        """
        if not has_request_context():
            return

        if 'request_context' not in g:
            g.request_context = {}

        if request_id:
            g.request_context['request_id'] = request_id
        else:
            g.request_context['request_id'] = str(uuid.uuid4())

        if user_id:
            g.request_context['user_id'] = user_id

        if client_id:
            g.request_context['client_id'] = client_id

    @staticmethod
    def get_request_id():
        """
        Get current request ID
        """
        if has_request_context():
            return g.get('request_context', {}).get('request_id', 'N/A')
        return 'N/A'

    @staticmethod
    def disable_colors():
        """
        Disable colors for logging (useful for production environments)
        """
        colorama.deinit()