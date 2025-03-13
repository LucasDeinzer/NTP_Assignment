import socket
import time
import struct
from ntp_timestamp import to_NTPtimestamp, timestamp_to_double
from packet_builder import packet_builder

DEFAULT_NTP_SERVER = "pool.ntp.org"
DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000

def create_ntp_request(version=4, mode=3):
    current_time = time.time() + 2208988800  # Convert to NTP epoch
    packet = packet_builder(
        LI=0, VN=version, mode=mode, stratum=0, poll=0, precision=0,
        rootdelay=0, rootdisp=0, refid=0,
        reftime=b'\x00' * 8, org=b'\x00' * 8, rec=b'\x00' * 8,
        xmt=to_NTPtimestamp(current_time), chave=None
    )
    return packet

def parse_ntp_response(packet):
    unpacked = struct.unpack("!12I", packet[:48])
    t2 = timestamp_to_double((unpacked[8], unpacked[9]))
    t3 = timestamp_to_double((unpacked[10], unpacked[11]))
    return t2 - 2208988800, t3 - 2208988800

def get_ntp_time(ntp_server, port=DEFAULT_NTP_PORT, version=4):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = create_ntp_request(version=version, mode=3)
    t1 = time.time()
    client.sendto(packet, (ntp_server, port))
    data, _ = client.recvfrom(1024)
    t4 = time.time()
    if data:
        t2, t3 = parse_ntp_response(data)
        rtt = (t4 - t1) - (t3 - t2)
        offset = ((t2 - t1) + (t3 - t4)) / 2
        return t1, t4, t2, t3, rtt, offset

if __name__ == "__main__":
    server_address = input("Enter NTP server address (leave blank to use default): ") or DEFAULT_NTP_SERVER
    port = LOCAL_NTP_PORT if server_address != DEFAULT_NTP_SERVER else DEFAULT_NTP_PORT
    
    result = get_ntp_time(server_address, port=port)
    
    if result:
        t1, t4, t2, t3, rtt, offset = result
        print(f"T1 (Client Send Time): {t1} ({time.ctime(t1)})")
        if t2 > 0:
            print(f"T2 (Server Receive Time): {t2} ({time.ctime(t2)})")
        else:
            print(f"T2 (Server Receive Time): {t2} (Invalid timestamp)")
        if t3 > 0:
            print(f"T3 (Server Send Time): {t3} ({time.ctime(t3)})")
        else:
            print(f"T3 (Server Send Time): {t3} (Invalid timestamp)")
        print(f"T4 (Client Receive Time): {t4} ({time.ctime(t4)})")
        print(f"Round Trip Time (RTT): {rtt}")
        print(f"Offset: {offset}")
    else:
        print("Failed to get NTP time from server.")