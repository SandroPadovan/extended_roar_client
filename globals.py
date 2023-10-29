import configparser


CONFIG_FILE_PATH = "config.file"
RESET_FILE_PATH = "reset.marker"
TERMINATE_FILE_PATH = "terminate.marker"


def get_config_path():
    return CONFIG_FILE_PATH


def get_reset_path():
    return RESET_FILE_PATH


def get_terminate_path():
    return TERMINATE_FILE_PATH


def get_config_from_file():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config
