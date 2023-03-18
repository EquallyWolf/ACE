"""
Utility functions and classes for the ACE project.

#### Classes:

TextProcessor:
    Storing helper functions related to processing and formatting text.

Logger:
    Wraps the logging module to provide a simple interface for creating
    loggers and logging messages.

#### Functions: None
"""

import logging
import re
from contextlib import contextmanager
from datetime import datetime as dt
from pathlib import Path
from typing import Callable, Union

import toml


class TextProcessor:
    """
    Storing helper functions related to processing and formatting text.

    #### Parameters: None

    #### Methods:

    remove_ansi_escape(text: str) -> str
        Remove ANSI escape sequences from a string.

    find_match(text: str, patterns: list[str], group: Union[str, int]) -> Union[str, None]
        Find a match in a string using a list of regex patterns.

    """

    def remove_ansi_escape(self, text: str) -> str:
        """
        Remove ANSI escape sequences from a string.

        #### Parameters:

        text: str
            The text to remove ANSI escape sequences from.

        #### Returns: str
            The text with ANSI escape sequences removed.

        #### Raises: None
        """
        return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)

    def find_match(
        self, text: str, patterns: list[str], group: Union[str, int]
    ) -> Union[str, None]:
        """
        Find a match in a string using a list of regex patterns.

        #### Parameters:

        text: str
            The text to search.

        patterns: list[str]
            A list of regex patterns to search for.

        group: Union[str, int]
            The group to return from the match.

        ### Returns: Union[str, None]
            The match if found, otherwise None.
        """
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                return match[group] if group else match  # type: ignore
        return None


class Logger:
    """
    Wraps the logging module to provide a simple interface for creating
    loggers and logging messages.

    #### Parameters:

    name: str (default: "main")
        The name of the logger.

    handlers: list[tuple[str, str]] (default: [("stdout", "info")])
        A list of tuples containing the handler name and the logging level
        to use for that handler.

    format: str (default: "%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        The format to use for the logger.

    level: str (default: "info")
        The logging level to use for the logger.

    file: str (default: None)
        The file to log to if the file handler is used.

    #### Methods:

    log(level: str, message: str, exc_info: bool = False) -> None
        Function to log a message with the given level.

    log_function(func: Callable) -> Callable
        Decorator to log the start and end of a function.

    log_context(level: str, start_message: str, end_message: str) -> contextmanager
        Context manager to log the start and end of a block of code.
    """

    logging_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    valid_handlers = [("file", "info"), ("stdout", "info")]

    def __init__(
        self,
        name: str = "main",
        handlers: Union[list[tuple[str, str]], None] = None,
        format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level: str = "info",
        file: Union[str, None] = None,
    ) -> None:
        self.name = name
        self.handlers = self._validate_handlers(
            handlers or [("stdout", "info")], self.valid_handlers
        )
        self.format = format
        self.file = file
        self.level = self._validate_level(level.lower())

        self._logger = self._create_logger()

        self._options = {
            "debug": self._logger.debug,
            "info": self._logger.info,
            "warning": self._logger.warning,
            "error": self._logger.error,
            "critical": self._logger.critical,
        }

    def log(self, level: str, message: str, exc_info: bool = False) -> None:
        """
        Function to log a message with the given level.

        #### Parameters:

        level: str
            The logging level to use.

        message: str
            The message to log.

        exc_info: bool (default: False)
            Whether to log exception information.

        #### Returns: None

        #### Raises: None
        """
        self._options.get(level.lower(), self._logger.info)(message, exc_info=exc_info)

    # TODO: Remove this method as it doesn't really work and is no longer used.
    def log_function(self, func: Callable) -> Callable:
        """
        Decorator to log the calling and return values of a function (if there is a return value).

        #### Parameters:

        func: Callable
            The function to decorate.

        #### Returns: Callable
            The decorated function.

        #### Raises: None
        """

        def wrapper(*args, **kwargs):
            func_name, level = (
                (func.__qualname__, "debug")
                if func.__name__.startswith("__")
                else (func.__name__, "info")
            )

            self.log(level, f"Calling {func_name}({args}, {kwargs})")

            result = func(*args, **kwargs)

            if result:
                self.log(level, f"Returning '{result}' from '{func_name}'")

            return result

        return wrapper

    @contextmanager  # type: ignore
    def log_context(self, level: str, enter_message: str, exit_message: str) -> None:  # type: ignore
        """
        Context manager to log the given messages at the given level.

        #### Parameters:

        level: str
            The logging level to use.

        enter_message: str
            The message to log when entering the context.

        exit_message: str
            The message to log when exiting the context.

        #### Returns: None

        #### Raises: None
        """
        self.log(level, enter_message)
        yield
        self.log(level, exit_message)

    def reset_handlers(self) -> None:  # pragma: no cover
        """
        Reset the handlers streams.

        #### Parameters: None

        #### Returns: None

        #### Raises: None
        """
        for handler in self._logger.handlers:
            self._logger.removeHandler(handler)

        for handler, handler_level in self.handlers:
            if handler == "stdout":
                self._logger.addHandler(self._create_stream_handler(handler_level))
            elif handler == "file":
                if not self.file:
                    raise ValueError(
                        "Invalid handler: 'file' handler requires a file path"
                    )
                self._logger.addHandler(
                    self._create_file_handler(handler_level, self.file)
                )

    def _validate_handlers(
        self, handlers: list[tuple[str, str]], valid_handlers: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """
        Helper function to validate the given handlers. If the handler is valid, returns the handlers list.

        #### Parameters:

        handlers: list[tuple[str, str]]
            The handlers to validate.

        valid_handlers: list[tuple[str, str]]
            The valid handlers.

        #### Returns: list[tuple[str, str]]
            The validated handlers.

        #### Raises: KeyError
            If an invalid handler is given.
        """
        if any(
            handler[0] not in [valid_handler[0] for valid_handler in valid_handlers]
            for handler in handlers
        ):
            raise KeyError(
                f"Invalid handlers given: {', '.join([handler[0] for handler in handlers])}."
                + f" Valid handlers: {', '.join([handler[0] for handler in valid_handlers])}"
            )
        return handlers

    def _validate_level(self, level: str) -> str:
        """
        Helper function to validate the given logging level. If the level is valid, returns the level.

        #### Parameters:

        level: str
            The logging level to validate.

        #### Returns: str
            The validated logging level.

        #### Raises: KeyError
            If an invalid logging level is given.
        """
        if level.lower() not in self.logging_levels:
            raise KeyError(
                f"Invalid logging level: '{level.lower()}'. Valid levels are: {', '.join(self.logging_levels)}"
            )
        return level

    def _create_logger(self) -> logging.Logger:
        """
        Helper function to create a logger object and add the handlers and logging level
        defined in the class initialisation.

        #### Parameters: None

        #### Returns: logging.Logger
            The logger object with the handlers and logging level supplied.

        #### Raises: ValueError
            Due to one of the following reasons:
                -> If an invalid handler is given.

                -> If the file handler is given but no file path is given.
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.logging_levels[self.level])

        for handler, handler_level in self.handlers:
            if handler == "stdout":
                logger.addHandler(self._create_stream_handler(handler_level))
            elif handler == "file":
                if not self.file:
                    raise ValueError(
                        "Invalid handler: 'file' handler requires a file path"
                    )
                logger.addHandler(self._create_file_handler(handler_level, self.file))  # type: ignore
        return logger

    def _create_stream_handler(self, level: str = "info") -> logging.StreamHandler:
        """
        Helper function to create a stream handler (stdout) and set the logging level.

        #### Parameters:

        level: str (default: "info")
            The logging level to use.

        #### Returns: logging.StreamHandler
            The stream handler.

        #### Raises: None
        """
        return self._configure_handler(logging.StreamHandler(), level)  # type: ignore

    def _create_file_handler(
        self, level: str = "info", file: Union[str, None] = None
    ) -> logging.FileHandler:
        """
        Helper function to create a file handler.

        #### Parameters:

        level: str (default: "info")
            The logging level to use.

        file: str (default: None)
            The file path to use.

        #### Returns: logging.FileHandler
            The file handler.

        #### Raises: None
        """
        return self._configure_handler(logging.FileHandler(file), level)  # type: ignore

    def _configure_handler(
        self,
        handler: Union[logging.Handler, logging.StreamHandler, logging.FileHandler],
        level: str,
    ) -> Union[logging.Handler, logging.StreamHandler, logging.FileHandler]:
        """
        Helper function to configure a handler.

        #### Parameters:

        handler: logging.Handler
            The handler to configure.

        level: str

        #### Returns: Union[logging.Handler, logging.StreamHandler, logging.FileHandler]
            The configured file handler.

        ### Raises: ValueError
            If an invalid logging level is given.
        """
        handler.setFormatter(
            logging.Formatter(self.format, style="{" if "{" in self.format else "%")
        )
        handler.setLevel(self.logging_levels[level])
        return handler

    @staticmethod
    def from_toml(
        root_dir: Union[Path, str] = Path.cwd(),
        config_file_name: str = "logs.toml",
        log_name: str = "main",
    ) -> "Logger":
        """
        Creates a logger object and sets up its configuration based on the values
        from a toml file stored in the "config" directory.

        The logger can be used for logging messages in the current script and can
        save the log files in the "logs" directory.

        #### Parameters:

        root_dir: Path or str (default: Path.cwd())
            The root directory of the project.

        config_file_name: str
            The file name of the file that contains the logging configuration.

        log_name: str
            The name of the configuration to use from the logs.toml file.

        #### Returns: Logger
            The logger.

        #### Raises: None
        """
        logs_dir = Path.joinpath(Path(root_dir), "logs")
        logs_dir.mkdir(exist_ok=True)

        log_file = Path.joinpath(logs_dir, f"{dt.now().strftime('%Y-%m-%d')}.log")
        log_config_file = Path.joinpath(Path(root_dir), "config", config_file_name)

        log_config = toml.load(log_config_file).get(
            log_name, toml.load(log_config_file).get("main", {})
        )

        if log_file.exists() and log_config.get("reload", False):
            log_file.unlink()

        return (
            Logger(
                *filter(  # type: ignore
                    None,
                    [
                        log_name,
                        [
                            (handler.get("type"), handler.get("level"))
                            for handler in log_config.get(
                                "handlers", [{"type": "stdout", "level": "info"}]
                            )
                        ],
                        log_config.get("format", None),
                        log_config.get("level", None),
                        log_file,
                    ],
                )
            )
            if log_config
            else Logger()
        )
