import socket
import time
import struct
import hmac
from ntp_timestamp import to_NTPtimestamp
from packet_builder import packet_builder
from ntp_hmac import verificar_hmac, calcular_hmac

DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000
SHARED_SECRET = b'supersecret'  # Chave compartilhada para HMAC-SHA256

def verify_hmac_server(packet, chave):
    keyid = struct.unpack("!I", packet[-36:-32])[0]
    if keyid != 1:
        return False
    received_digest = packet[-32:]
    calculated_digest = calcular_hmac(packet[:-32], chave)
    return hmac.compare_digest(received_digest, calculated_digest)

def create_ntp_response(received_packet, recv_time):
    if not verificar_hmac(received_packet[:-32], SHARED_SECRET, received_packet[-32:]):
        print("HMAC verification failed")
        return None

    recv_time_ntp = to_NTPtimestamp(recv_time + 2208988800)
    transmit_time = time.time() + 2208988800
    transmit_time_ntp = to_NTPtimestamp(transmit_time)
    origin_timestamp = received_packet[40:48]
    packet = packet_builder(
        LI=0, VN=4, mode=4, stratum=2, poll=0, precision=0,
        rootdelay=0, rootdisp=0, refid=0,
        reftime=b'\x00' * 8, org=origin_timestamp, rec=recv_time_ntp,
        xmt=transmit_time_ntp, keyid=1, chave=SHARED_SECRET  # Inclui keyid e chave
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
            if response_packet:
                server.sendto(response_packet, address)

if __name__ == "__main__":
    try:
        port = int(input("Enter port number to run the NTP server (default 5000): ") or LOCAL_NTP_PORT)
    except ValueError:
        port = LOCAL_NTP_PORT
    run_ntp_server(port=port)