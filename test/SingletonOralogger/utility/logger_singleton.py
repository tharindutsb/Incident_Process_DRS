from pathlib import Path
import logging
import logging.config
import configparser

class SingletonLogger:
    _instances = {}
    _configured = False
    _logs_dir = None

    @classmethod
    def configure(cls):
        # Assume logger_singleton.py is in utility/
        project_root = Path(__file__).resolve().parents[1]
        config_dir = project_root / 'config'
        corefig_path = config_dir / 'corefig.ini'

        if not corefig_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {corefig_path}")

        config = configparser.ConfigParser()
        config.read(str(corefig_path))

        # Get current environment
        if 'environment' not in config or 'current' not in config['environment']:
            raise ValueError("Missing [environment] section or 'current' key in corefig.ini")
        environment = config['environment']['current'].lower()

        # Get logger path based on environment
        logger_section = f'logger_path_{environment}'
        if logger_section not in config or 'log_dir' not in config[logger_section]:
            raise ValueError(f"Missing 'log_dir' under section [{logger_section}]")

        log_dir = Path(config[logger_section]['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        cls._logs_dir = log_dir
        print(f"Logger Path: {cls._logs_dir} (env: {environment})")

        # Load logger.ini
        logger_ini_path = config_dir / 'logger.ini'
        if not logger_ini_path.exists():
            raise FileNotFoundError(f"Logger configuration file not found: {logger_ini_path}")

        logging.config.fileConfig(str(logger_ini_path))
        cls._configured = True

    @classmethod
    def get_logger(cls, logger_name='appLogger'):
        if not cls._configured:
            raise ValueError("Logger not configured. Please call 'configure()' first.")

        if logger_name not in cls._instances:
            logger = logging.getLogger(logger_name)

            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    log_file_path = cls._logs_dir / f"{logger_name}.log"
                    handler.baseFilename = str(log_file_path)

                    if handler.stream:
                        handler.stream.close()
                    handler.stream = open(handler.baseFilename, handler.mode)

            cls._instances[logger_name] = logger

        return cls._instances[logger_name]
