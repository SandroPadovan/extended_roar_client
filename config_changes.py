from json import loads
from socket import AF_INET, SOCK_STREAM, socket
import os
import configparser
from globals import get_config_path, get_config_from_file


def listen_for_config_changes() -> None:
    """
    Listens for config changes sent from C2 server and updates the existing config
    """
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind(("0.0.0.0", 42666))
        sock.listen(1)

        while True:
            conn, addr = sock.accept()  # keep listening for new connections
            with conn:
                while True:
                    data = conn.recv(1024)  # listen for incoming data of connection
                    if not data:
                        break
                    new_config = loads(data.decode(encoding="utf-8"))
                    print("received", new_config)
                    update_existing_config(new_config)


def update_existing_config(new_config: dict) -> None:
    """
    Updates the config file with new values.
    :param new_config: Dict with new config values
    :return: None
    """
    config_path = get_config_path()
    if not os.path.exists(config_path):
        with open(config_path, "x"):
            pass
        config = configparser.ConfigParser()
        config.read(config_path)
        config.add_section("GENERAL")
        config.add_section("BURST")
    else:
        config = get_config_from_file()
    config.set("GENERAL", "algo", new_config["algo"])
    config.set("GENERAL", "rate", new_config["rate"])
    config.set("BURST", "duration", new_config["burst_duration"])
    config.set("BURST", "pause", new_config["burst_pause"])

    with open(os.path.join(os.path.curdir, config_path), "w") as config_file:
        config.write(config_file)
