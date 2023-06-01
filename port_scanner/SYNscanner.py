import socket
import sys
import random
import threading
import concurrent.futures
import time

opened_port = []
closed_port = []

def create_frame(src_ip, src_port, dest_ip, dest_port):
    ip_header = b"\x45\x00\x00\x40" # version, ihl, tos, Total length
    ip_header += b"\x00\x00\x40\x00" # id, IP flags, fragment offset
    ip_header += b"\x40\x06\x00\x00" # TTL, protocol, header checksum
    ip_header += socket.inet_aton(src_ip) # source address
    ip_header += socket.inet_aton(dest_ip) # destination address

    tcp_header = src_port.to_bytes(2, 'big') + dest_port.to_bytes(2, 'big') # source port, destination port
    tcp_header += b"\x00\x00\x00\x00" # seq number
    tcp_header += b"\x00\x00\x00\x00" # ack number
    tcp_header += b"\x50\x02\xff\xff" # offset, reserved, TCP flags, window
    tcp_header += b"\x00\x00\x00\x00" # checksum, urgent pointer

    return ip_header + tcp_header

def scan_port(src_ip, src_port, dest_ip, dest_port):
    time.sleep(2)

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    frame = create_frame(src_ip, src_port, dest_ip, dest_port)
    raw_socket.sendto(frame, (dest_ip, dest_port))

    response, _ = raw_socket.recvfrom(4096)
    if response:
        tcp_flag = int.from_bytes(response[33:34], "big")
        if tcp_flag == 18: # SYN/ACK
            msg = "{} is opened".format(dest_port)
        elif tcp_flag == 20: # RST
            msg = "{} is closed".format(dest_port)
        
        return msg

    return "No response"

def main(src_ip, src_port, dest_ip):
    num_threads = 10
    ports = list(range(1, 1025))

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(scan_port, src_ip, src_port, dest_ip, dest_port) for dest_port in ports]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(result)

    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()

if __name__ == "__main__":
    src_ip = '127.0.0.1'
    src_port = random.randint(1024, 65535)
    dest_ip = '127.0.0.1'
    
    main(src_ip, src_port, dest_ip)
    print("opened_port:", opened_port)