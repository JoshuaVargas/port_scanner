![Screenshot 2024-07-07 035236](https://github.com/JoshuaVargas/port_scanner/assets/13924477/050cbfc0-3806-46a8-a9b5-9404c7f98bad)


# Port Scanning and Banner Grabbing

At the heart of information assurance is inventory management. You cannot protect something that you do not know is there. Thus, it's important to understand what information you're leaking to the greater public.

Port Scanning is an active reconnaissance technique that can be used to enumerate open ports for the purposes of discovering vulnerabilities on a host. When combined with banner grabbing, port scanning can be a powerful OSINT tool to help meet information assurance goals.

## Scanning Ports

By utilizing python's built-in ```socket``` module, we can create a socket, connect to a host at a certain port number, and either after a successful connection or a timeout, close the socket to release resources and close the connection.

Open ports can often leak valuable information to attackers regarding services running on those ports, and in this case we can declare a ```get_banner()``` function to receive and decode the banner to gain further information on the port.

```py
import socket

def get_banner(s):
    return s.recv(1024).decode().strip('\n')

def scan_ports(port):
    try:
        sock = socket.socket()
        sock.settimeout(.5)
        sock.connect((host, port))
        try:
            banner = get_banner(sock)
            print(f"    [+] Open Port: {host}:{port}" + " | " + str(banner))
        except:
            print(f"    [+] Open Port {host}:{port}")
    except:
        pass
    finally:
        sock.close()
```
The above snippet of code defines the core of the application, the ```scan_port()``` and ```get_banner``` functions. It is important to note that the number of possible targets for scanning on a single machine is 65,535 different ports. Thus, a full scan with a timeout of 1 second results in an 18 hour scan. Making the timeout longer or shorter results in more or less accurate results respectively.

However, a scan of only the well-known ports (1-1,024) results in scan times of just under 9 minutes with a timeout of 0.5 seconds. These long scan times make the need for concurrency obvious as accuracy is lost with shorter timeout lengths.

## Threading the Needle

The need for concurrency means that threading is the only viable option for increased performance without losses in accuracy. So, this project makes use of python's built in ```threading``` module.

```py
from threading import Thread
from queue import Queue

N_THREADS = 200
q = Queue()

def worker():
    global q
    while True:
        t_port = q.get()
        scan_port(t_port)
        q.task_done()


def main(host, ports):
    global q
    for t in range(THREADS):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    for t_port in ports:
        q.put(t_port)
    
    q.join()

```

By defining the number of threads we want, we can have our ```worker()``` queue up ports for scanning. The worker first gets a port number from the queue, scans it, and completes the scan. Our ```main()``` function, however, is what fills up the queue with port numbers.

At 200 threads with a 0.2 second timeout, the same task that took 18 hours to complete can suddenly be done in under two minutes. A scan of well-known ports can be done in just a few seconds. And, finally, scanning the registered port range can happen in a little over 30 seconds. However, running the optimal number of threads is requires a bit of trial and error. At 1000 threads, my CPU utilization quickly reaches 100% for long periods of time during the scan. So, I've found that setting N_THREADS to 400 is a good middle ground for speed and CPU utilization. After all, the scanner shouldn't lock up your computer.

## A Final Note On Scanning

Active scanning, while not illegal, leads to certain ethical questions being asked. Mainly, is it right to perform active recon on a system that we don't have consent to scan? The answer isn't so obvious. There is a benefit to scanning machines around us, especially in a research capacity. Knowing, for example, the most common services made visible to the internet is important to know because it can then be assumed that such services are of greater interest to attackers.

If you have any doubts about targets for scans, the best targets are usually those within your own network. In fact, it'd be wise to enumerate your network and the open ports within it.

For the most accurate and least intrusive scans, single threaded scanning with longer timeouts is best. I've found that a few ports take longer than a second to connect to, and so even an 18 hour scan might not deliver the most accurate results when using a timeout rate of one port per second.

However, scanning multiple ports concurrently is faster but also more likely to get blocked by firewalls that detect a flood of traffic coming in from a single IP address. And while a slow scan is like sneaking through a castle, a fast scan is like making a low pass in a fighter jet. Either way, both have their uses and you'll likely get the intel you need.
