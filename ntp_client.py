import socket
import struct
import time
from ntp_timestamp import to_NTPtimestamp, timestamp_to_double

DEFAULT_NTP_SERVER = "pool.ntp.org"
DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000
NTP_PACKET_FORMAT = "!BBBb11I"

def create_ntp_packet(version=4, mode=3, transmit_timestamp=None, key_id=0, key=None):
    packet = bytearray(48)
    li_vn_mode = (0 << 6) | (version << 3) | mode
    packet[0] = li_vn_mode
    
    if transmit_timestamp:
        packed_tx_timestamp = to_NTPtimestamp(transmit_timestamp)
        packet[40:48] = packed_tx_timestamp
    
    return packet

def parse_ntp_packet(packet):
    unpacked = struct.unpack("!12I", packet[:48])
    tx_timestamp = timestamp_to_double(unpacked[10:12])
    return tx_timestamp - 2208988800

def get_ntp_time(ntp_server, port=DEFAULT_NTP_PORT, version=4, key_id=0, key=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = create_ntp_packet(version=version, transmit_timestamp=time.time(), key_id=key_id, key=key)
    client.sendto(packet, (ntp_server, port))
    data, _ = client.recvfrom(1024)
    if data:
        return parse_ntp_packet(data)

if __name__ == "__main__":
    server_address = input("Enter NTP server address (leave blank to use default): ") or DEFAULT_NTP_SERVER
    port = LOCAL_NTP_PORT if server_address != DEFAULT_NTP_SERVER else DEFAULT_NTP_PORT
    
    ntp_time = get_ntp_time(server_address, port=port)
    
    if ntp_time:
        print("Raw NTP Time:", ntp_time)
        try:
            print("NTP Time:", time.ctime(ntp_time))
        except Exception as e:
            print("Error converting NTP time:", e)
    else:
        print("Failed to get NTP time from server.")