import socket
import random
import sys
import threading
import concurrent.futures
import time

opened_port = []
closed_port = []

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        time.sleep(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            opened_port.append(port)
            msg = "{} - port {} is open".format(threading.get_ident(), port)
        else:
            closed_port.append(port)
            msg = "{} - port {} is not open".format(threading.get_ident(), port)
        sock.close()
        return msg

    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()
    except socket.gaierror:
        print("Hostname could not be resolved.")
        sys.exit()
    except socket.error:
        print("Couldn't connect to server.")
        sys.exit()

def main(host):
    num_threads = 10
    ports = list(range(1, 1025))
    random.shuffle(ports)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(scan_port, host, port) for port in ports]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(result)

    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()

if __name__ == "__main__":
    host = '192.168.35.1'
    main(host)
    print("opened_port:", opened_port)
