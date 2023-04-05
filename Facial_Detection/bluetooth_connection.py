from bluetooth import *
        
def rx_and_echo(sock):
    sock.send("\nsend anything\n")
    while True:
        data = sock.recv(buf_size)
        if data:
            return data

def scan_devices():
    nearby_devices = discover_devices(lookup_names=True)
    print("Found {} devices.".format(len(nearby_devices)))

    ret = ""
    for addr, name in nearby_devices:
        print("  {} - {}".format(addr, name))
        if name == "ESP32test":
            ret = addr
    return ret

def connect(addr):
    service_matches = find_service( address = addr )
    if len(service_matches) == 0:
        print("Couldn't connect =(")
        sys.exit(0)

    for s in range(len(service_matches)):
        print("\nservice_matches: [" + str(s) + "]:")
        print(service_matches[s])
    
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    port=1
    print("connecting to \"%s\" on %s, port %s" % (name, host, port))

    # Create the client socket
    sock=BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    print("connected")
    return sock

def disconnect(sock):
    sock.close()

#MAC address of ESP32
addr = "54:43:B2:2B:A3:E2"
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
#service_matches = find_service( uuid = uuid, address = addr )

buf_size = 1024
