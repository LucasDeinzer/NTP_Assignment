import socket
import time
import struct
from ntp_timestamp import to_NTPtimestamp
from packet_builder import packet_builder

DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000

def create_ntp_response(received_packet, recv_time):
    recv_time_ntp = to_NTPtimestamp(recv_time + 2208988800)
    transmit_time = time.time() + 2208988800
    transmit_time_ntp = to_NTPtimestamp(transmit_time)
    origin_timestamp = received_packet[40:48]
    packet = packet_builder(
        LI=0, VN=4, mode=4, stratum=2, poll=0, precision=0,
        rootdelay=0, rootdisp=0, refid=0,
        reftime=b'\x00' * 8, org=origin_timestamp, rec=recv_time_ntp,
        xmt=transmit_time_ntp, chave=None
    )
    return packet

def run_ntp_server(port=LOCAL_NTP_PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("", port))
    print(f"NTP server is running on port {port}")
    
    while True:
        data, address = server.recvfrom(1024)
        if data:
            print(f"Received packet from {address}")
            recv_time = time.time()
            response_packet = create_ntp_response(data, recv_time)
            server.sendto(response_packet, address)

if __name__ == "__main__":
    try:
        port = int(input("Enter port number to run the NTP server (default 5000): ") or LOCAL_NTP_PORT)
    except ValueError:
        port = LOCAL_NTP_PORT
    run_ntp_server(port=port)