from json import loads
from socket import AF_INET, SOCK_STREAM, socket
import os
import configparser
from globals import get_config_path, get_config_from_file
from multiprocessing import Process
from subprocess import call

BENIGN_PROCESSES = []
SUPPORTED_BENIGN_BEHAVIORS = ["compression", "installation", "preprocessing"]


def execute_benign_behavior(path: str, duration: int = 0) -> None:
    """
    Calls the bash script at the provided path with the duration as command line argument.

    :param path: Path to behavior bash script
    :param duration: Duration in seconds, 0 for infinite execution
    :return: None
    """
    call([path, str(duration)])


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

                    # handle benign behavior
                    if new_config["benign_behavior_behavior"] in SUPPORTED_BENIGN_BEHAVIORS:
                        for proc in BENIGN_PROCESSES:
                            if proc.is_alive():
                                # kill all benign behavior processes still running
                                proc.terminate()
                                proc.join()

                        # start new benign behavior process according to new config
                        benign_proc = Process(target=execute_benign_behavior,
                                              args=("./benign_behaviors/{}.sh".format(new_config['benign_behavior_behavior']),
                                                    new_config["benign_behavior_duration"]))
                        benign_proc.start()
                        BENIGN_PROCESSES.append(benign_proc)


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
        config.add_section("BENIGN_BEHAVIOR")
    else:
        config = get_config_from_file()
    config.set("GENERAL", "algo", new_config["algo"])
    config.set("GENERAL", "rate", new_config["rate"])
    config.set("BURST", "duration", new_config["burst_duration"])
    config.set("BURST", "pause", new_config["burst_pause"])
    config.set("BENIGN_BEHAVIOR", "behavior", new_config["benign_behavior_behavior"])
    config.set("BENIGN_BEHAVIOR", "duration", new_config["benign_behavior_duration"])

    with open(os.path.join(os.path.curdir, config_path), "w") as config_file:
        config.write(config_file)
