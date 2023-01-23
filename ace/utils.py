import logging
import re
from typing import Callable, Union


class TextProcessor:
    """
    Class for storing helper functions related to processing
    and formatting text.
    """

    def remove_ansi_escape(self, text: str) -> str:
        """
        Remove ANSI escape sequences from a string.
        """
        return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)

    def find_match(
        self, text: str, patterns: list[str], group: Union[str, int]
    ) -> Union[str, None]:
        """
        Find a match in a string using a list of regex patterns.

        ### Parameters:

        text: str
            The text to search.

        patterns: list[str]
            A list of regex patterns to search for.

        group: str (default: "")
            The group to return from the match.

        ### Returns:

        Union[str, None]
            The match if found, otherwise None.
        """
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                return match[group] if group else match  # type: ignore
        return None


class Logger:
    """
    Class that wraps the logging module to provide a simple
    interface for creating loggers and logging messages.
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

    def log(self, level: str, message: str) -> None:
        """
        Function to log a message with the given level.

        ### Parameters:

        level: str
            The logging level to use.

        message: str
            The message to log.

        ### Returns:

        None
        """
        self._options.get(level.lower(), self._logger.info)(message)

    def log_function(self, func: Callable) -> Callable:
        """
        Decorator to log the calling and return values of a function (if there is a return value).

        Uses the given

        ### Parameters:

        func: Callable
            The function to decorate.

        ### Returns:

        Callable
            The decorated function.
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

    def reset_handlers(self) -> None:  # pragma: no cover
        """
        Reset the handlers streams.

        ### Returns:

        None
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

        ### Parameters:

        handlers: list[tuple[str, str]]
            The handlers to validate.

        valid_handlers: list[tuple[str, str]]
            The valid handlers.

        ### Returns:

        list[tuple[str, str]]
            The validated handlers.

        ### Raises:

        ValueError
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

        ### Parameters:

        level: str
            The logging level to validate.

        ### Returns:

        str
            The validated logging level.

        ### Raises:

        KeyError
            If an invalid logging level is given.
        """
        if level.lower() not in self.logging_levels:
            raise KeyError(
                f"Invalid logging level: '{level.lower()}'. Valid levels are: {', '.join(self.logging_levels)}"
            )
        return level

    def _create_logger(self) -> logging.Logger:
        """
        Helper function to create a logger object.

        ### Parameters:

        name: str
            The name of the logger.

        ### Returns:

        logging.Logger
            The logger.

        ### Raises:

        ValueError
            If an invalid handler is given.
            or
            If the file handler is given but no file path is given.
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
        Helper function to create a stream handler.

        ### Returns:

        logging.StreamHandler
            The stream handler.
        """
        handler = logging.StreamHandler()
        return self._configure_file_handler(handler, level)  # type: ignore

    def _create_file_handler(
        self, level: str = "info", file: Union[str, None] = None
    ) -> logging.FileHandler:
        """
        Helper function to create a file handler.

        ### Returns:

        logging.FileHandler
            The file handler.
        """
        handler = logging.FileHandler(file)  # type: ignore
        return self._configure_file_handler(handler, level)  # type: ignore

    def _configure_file_handler(
        self,
        handler: Union[logging.Handler, logging.StreamHandler, logging.FileHandler],
        level: str,
    ) -> Union[logging.Handler, logging.StreamHandler, logging.FileHandler]:
        """
        Helper function to configure a file handler.

        ### Parameters:

        handler: logging.Handler
            The handler to configure.

        level: str

        ### Returns:

        Union[logging.Handler, logging.StreamHandler, logging.FileHandler]
            The configured file handler.

        ### Raises:

        ValueError
            If an invalid logging level is given.
        """
        handler.setFormatter(logging.Formatter(self.format))
        handler.setLevel(self.logging_levels[level])
        return handler
