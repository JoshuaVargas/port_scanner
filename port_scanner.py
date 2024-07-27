import socket
import ssl
import time
from threading import Thread
from queue import Queue

N_THREADS = 512
q = Queue()

def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        if port == 80:
            try:
                http_request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
                sock.send(http_request.encode())
                banner = sock.recv(1024).decode("utf-8")
                print(f"    [+] Open Port {host}:{port}\n{banner}")
            except:
                print("Failed to grab HTTP Response Code")
                print(f"    [+] Open Port {host}:{port} | No banner grabbed!")
        elif port == 443:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ssl_context = ssl.create_default_context()
                ssl_socket = ssl_context.wrap_socket(s, server_hostname=host)
                ssl_socket.connect((host, port))
                http_request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
                ssl_socket.send(http_request.encode())
                banner = ssl_socket.recv(1024).decode("utf-8")
                print(f"    [+] Open Port {host}:{port}\n{banner}")
            except:
                print("Failed to grab HTTP Response Code")
                print(f"    [+] Open Port {host}:{port} | No banner grabbed!")
        else:
            try:
                banner = sock.recv(1024).decode("utf-8")
                print(f"    [+] Open Port: {host}:{port}\n{banner}")
            except:
                print(f"    [+] Open Port {host}:{port} | No banner grabbed!")
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
                                                    v 0.0.2
""")
    print("Separate all values with commas (e.g. 192.168.1.1,google.com)")
    hosts = input('[+] Enter Host Domain Names or IP Addresses: ')
    scan_type = input(f"""
[1] Well-Known Port Scan (1,1024)     [~4sec]
[2] Registered Port Scan (1025,49151) [~190sec]
[3] Ephemeral Port Scan (49152,65535) [~70sec]
[4] Full Scan (1,65535)               [~270sec]
[5] Custom Range (e.g. 22,80)         [~4.2 sec per 1024 ports]

[+] Select Scan Type: """)
    
    match scan_type:
        case "1":
            port_range = ("1,1024")
        case "2":
            port_range = ("1025,49151")
        case "3":
            port_range = ("49152,65535")
        case "4":
            port_range = ("1,65535")
        case _:
            port_range = input('\n[+] Enter Port Range: ')

    first_port, last_port = port_range.split(",")
    first_port, last_port = int(first_port), int(last_port)

    ports = [ p for p in range(first_port, (last_port + 1))]

    for host in hosts.split(','):
        open_ports = 0
        start_time = time.time()
        print(f"\n[Scanning] {host}\n")
        main(host.strip(' '), ports)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n[Scan Complete] Ports {first_port}-{last_port} scanned in {execution_time} seconds")
    print("\n")