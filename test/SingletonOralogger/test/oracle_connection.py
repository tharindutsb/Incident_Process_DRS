import cx_Oracle
import threading
import configparser
from pathlib import Path
from logger_singleton import SingletonLogger

class OracleConnectionSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(OracleConnectionSingleton, cls).__new__(cls)
                    cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        self.logger = SingletonLogger.get_logger('dbLogger')
        try:
            # Load connection string from config
            project_root = Path(__file__).resolve().parents[1]
            config_path = project_root / 'config' / 'corefig.ini'
            config = configparser.ConfigParser()
            config.read(str(config_path))

            env = config['environment']['current'].lower()
            section = f'database_{env}'

            if section not in config or 'connection_string' not in config[section]:
                raise KeyError(f"Missing connection_string in section [{section}]")

            self.connection_string = config[section]['connection_string']
            self.connection = cx_Oracle.connect(self.connection_string)
            self.logger.info("Oracle connection established successfully.")

        except Exception as err:
            self.logger.error(f"Error connecting to Oracle: {err}")
            self.connection = None

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Oracle connection closed.")
                self.connection = None
                OracleConnectionSingleton._instance = None
            except Exception as err:
                self.logger.error(f"Error closing Oracle connection: {err}")

    def __enter__(self):
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
