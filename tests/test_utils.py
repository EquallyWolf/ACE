import logging
from datetime import datetime as dt
import pytest

from ace import utils


class TestTextProcessor:
    processor = utils.TextProcessor()

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("\u001b[30m", ""),
            ("\u001b[30m\u001b[30m", ""),
            ("\u001b[30mHello", "Hello"),
            ("\u001b[36mExample Text", "Example Text"),
            ("\u001b[4m Another example\u001b[0m", " Another example"),
            ("\u001b[45;1mTest with a number: 123", "Test with a number: 123"),
        ],
    )
    def test_remove_ansi_escape(self, text, expected):
        assert self.processor.remove_ansi_escape(text) == expected


class TestLogger:
    logger_name = __name__

    @pytest.fixture()
    def mock_logger_stdout(self):
        return utils.Logger(
            self.logger_name,
            [("stdout", "debug")],
            "%(name)s | %(levelname)s | %(message)s",
            "debug",
            None,
        )

    def _create_test_logs(self, logger: utils.Logger):

        logger.reset_handlers()

        logger.log("debug", "Test debug")
        logger.log("info", "Test info")
        logger.log("warning", "Test warning")
        logger.log("error", "Test error")
        logger.log("critical", "Test critical")

    @pytest.mark.parametrize(
        "level,expected",
        [
            ("debug", logging.DEBUG),
            ("info", logging.INFO),
            ("warning", logging.WARNING),
            ("error", logging.ERROR),
            ("critical", logging.CRITICAL),
        ],
    )
    def test_logging_levels(self, level, expected, mock_logger_stdout):
        assert mock_logger_stdout.logging_levels[level] == expected

    def test_log(self, caplog, mock_logger_stdout):
        self._create_test_logs(mock_logger_stdout)
        assert caplog.record_tuples == [
            (__name__, logging.DEBUG, "Test debug"),
            (__name__, logging.INFO, "Test info"),
            (__name__, logging.WARNING, "Test warning"),
            (__name__, logging.ERROR, "Test error"),
            (__name__, logging.CRITICAL, "Test critical"),
        ]

    def test_log_file(self, tmp_path_factory):

        mock_log_file = tmp_path_factory.mktemp("logs") / "test.log"

        logger = utils.Logger(
            self.logger_name,
            [("file", "debug")],
            "%(name)s | %(levelname)s | %(message)s",
            "debug",
            mock_log_file,
        )

        self._create_test_logs(logger)

        assert mock_log_file.read_text() == (
            f"{__name__} | DEBUG | Test debug\n"
            + f"{__name__} | INFO | Test info\n"
            + f"{__name__} | WARNING | Test warning\n"
            + f"{__name__} | ERROR | Test error\n"
            + f"{__name__} | CRITICAL | Test critical\n"
        )

    def test_log_as_decorator_no_args_no_kwargs(self, caplog, mock_logger_stdout):
        @mock_logger_stdout.log_function
        def test_function():
            return "Test output"

        assert test_function() == "Test output"
        assert len(caplog.record_tuples) == 2
        assert caplog.record_tuples == [
            (
                __name__,
                logging.INFO,
                "Calling test_function((), {})",
            ),
            (__name__, logging.INFO, "Returning 'Test output' from 'test_function'"),
        ]

    def test_log_as_decorator_args_no_kwargs(self, caplog, mock_logger_stdout):
        @mock_logger_stdout.log_function
        def test_function(*args):
            return "Test output"

        assert test_function("arg1") == "Test output"
        assert len(caplog.record_tuples) == 2
        assert caplog.record_tuples == [
            (
                __name__,
                logging.INFO,
                "Calling test_function(('arg1',), {})",
            ),
            (__name__, logging.INFO, "Returning 'Test output' from 'test_function'"),
        ]

    def test_log_as_decorator_no_args_kwargs(self, caplog, mock_logger_stdout):
        @mock_logger_stdout.log_function
        def test_function(key1="value1"):
            return "Test output"

        assert test_function(key1="val1") == "Test output"
        assert len(caplog.record_tuples) == 2
        assert caplog.record_tuples == [
            (
                __name__,
                logging.INFO,
                "Calling test_function((), {'key1': 'val1'})",
            ),
            (__name__, logging.INFO, "Returning 'Test output' from 'test_function'"),
        ]

    def test_log_as_decorator_args_kwargs(self, caplog, mock_logger_stdout):
        @mock_logger_stdout.log_function
        def test_function(*args, **kwargs):
            return "Test output"

        assert test_function("arg1", key1="val1") == "Test output"
        assert len(caplog.record_tuples) == 2
        assert caplog.record_tuples == [
            (
                __name__,
                logging.INFO,
                "Calling test_function(('arg1',), {'key1': 'val1'})",
            ),
            (__name__, logging.INFO, "Returning 'Test output' from 'test_function'"),
        ]

    def test_log_as_context_manager(self, caplog, mock_logger_stdout):
        with mock_logger_stdout.log_context(
            "info", "Entering test context", "Exiting test context"
        ):
            pass

        assert len(caplog.record_tuples) == 2
        assert caplog.record_tuples == [
            (__name__, logging.INFO, "Entering test context"),
            (__name__, logging.INFO, "Exiting test context"),
        ]

    def test_log_invalid_handler(self):
        with pytest.raises(KeyError):
            utils.Logger(
                __name__,
                [("test", "info")],
                "%(name)s | %(levelname)s | %(message)s",
                "debug",
                None,
            )

    def test_log_file_not_specified(self):
        with pytest.raises(ValueError):
            utils.Logger(
                __name__,
                [("file", "info")],
                "%(name)s | %(levelname)s | %(message)s",
                "debug",
            )

    @pytest.mark.parametrize(
        "handler_config",
        [
            ("stdout", "test"),
            ("file", "test"),
        ],
    )
    def test_log_invalid_handler_level(self, handler_config, tmp_path):
        with pytest.raises(KeyError):
            utils.Logger(
                __name__,
                [handler_config],
                "%(name)s | %(levelname)s | %(message)s",
                "debug",
                tmp_path / "test.log",
            )

    def test_log_invalid_level(self):
        with pytest.raises(KeyError):
            utils.Logger(
                __name__,
                [("stdout", "info")],
                "%(name)s | %(levelname)s | %(message)s",
                "test",
            )

    def test_create_logger_from_toml(self, tmp_path):
        mock_toml = tmp_path / f"{dt.now().strftime('%Y-%m-%d')}.log"
        mock_toml.write_text(
            r"""
            [logger]
            level = "debug"
            reload = false
            format = "%(name)s | %(levelname)s | %(message)s"
            """
        )

        logger = utils.Logger.from_toml(
            root_dir=tmp_path,
            config_file_name=mock_toml,
            log_name="logger",
        )

        assert type(logger) == utils.Logger

    def test_create_logger_from_toml_reload_log_file(self, tmp_path):
        mock_toml = tmp_path / "test.toml"
        mock_toml.write_text(
            r"""
            [logger]
            level = "debug"
            reload = true
            format = "%(name)s | %(levelname)s | %(message)s"
            """
        )

        logs_dir = tmp_path / "logs"
        logs_dir.mkdir(exist_ok=True)

        mock_log_file = logs_dir / f"{dt.now().strftime('%Y-%m-%d')}.log"
        mock_log_file.touch()

        logger = utils.Logger.from_toml(
            root_dir=tmp_path,
            config_file_name=mock_toml,
            log_name="logger",
        )

        assert type(logger) == utils.Logger
