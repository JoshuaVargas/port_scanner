import socket
import time
from threading import Thread
from queue import Queue

N_THREADS = 400
q = Queue()

def get_banner(s):
    return s.recv(1024).decode().strip('\n')

def scan_port(port):
    try:
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect((host, port))
        try:
            banner = get_banner(sock)
            print(f"    [+] Open Port: {host}:{port}" + " | " + str(banner.decode().strip('\n')))
        except:
            print(f"    [+] Open Port {host}:{port}")
    except:
        pass
    finally:
        sock.close()


def worker():
    global q
    while True:
        t_port = q.get()
        scan_port(t_port)
        q.task_done()


def main(host, ports):
    global q
    for t in range(N_THREADS):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    for t_port in ports:
        q.put(t_port)
    
    q.join()



if __name__ == "__main__":
    print(r"""
______          _   _____                                 
| ___ \        | | /  ___|                                
| |_/ /__  _ __| |_\ `--.  ___ __ _ _ __  _ __   ___ _ __ 
|  __/ _ \| '__| __|`--. \/ __/ _` | '_ \| '_ \ / _ \ '__|
| | | (_) | |  | |_/\__/ / (_| (_| | | | | | | |  __/ |   
\_|  \___/|_|   \__\____/ \___\__,_|_| |_|_| |_|\___|_|   
""")
    hosts = input('[+] Enter Host Domain Names or IP Addresses (separate with ,): ')
    port_range = input('[+] Enter Port Range (separate with ,): ')

    first_port, last_port = port_range.split(",")
    first_port, last_port = int(first_port), int(last_port)

    ports = [ p for p in range(first_port, (last_port + 1))]

    for host in hosts.split(','):
        start_time = time.time()
        print(f"\n[Scanning] {host}")
        main(host.strip(' '), ports)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Scan completed in {execution_time} seconds.")
    print("\n")