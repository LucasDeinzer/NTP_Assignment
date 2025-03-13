import socket
import struct
import time
from ntp_timestamp import to_NTPtimestamp

DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000
NTP_PACKET_FORMAT = "!BBBb11I"

def create_ntp_response(received_packet, key_id=0, key=None):
    response_packet = bytearray(received_packet)
    li_vn_mode = (0 << 6) | (4 << 3) | 4
    response_packet[0] = li_vn_mode
    
    tx_timestamp = time.time() + 2208988800
    packed_tx_timestamp = to_NTPtimestamp(tx_timestamp)
    response_packet[40:48] = packed_tx_timestamp
    
    return response_packet

def run_ntp_server(port=LOCAL_NTP_PORT, key_id=0, key=None):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("", port))
    print(f"NTP server is running on port {port}")
    
    while True:
        data, address = server.recvfrom(1024)
        if data:
            print(f"Received packet from {address}")
            response_packet = create_ntp_response(data, key_id=key_id, key=key)
            server.sendto(response_packet, address)

if __name__ == "__main__":
    try:
        port = int(input("Enter port number to run the NTP server (default 5000): ") or LOCAL_NTP_PORT)
    except ValueError:
        port = LOCAL_NTP_PORT
    run_ntp_server(port=port)