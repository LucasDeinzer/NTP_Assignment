import socket
import time
import struct
import hmac
from ntp_timestamp import to_NTP_timestamp
from packet_builder import packet_builder
from ntp_hmac import verify_hmac, calculate_hmac


DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000
SHARED_SECRET = b'supersecret'  # Chave compartilhada para HMAC-SHA256


def verify_hmac_server(packet, chave):
    '''
    Verifica se o HMAC-SHA256 recebido corresponde aos dados e à chave fornecidos.

    Args:
        packet (bytes): Os dados para os quais o HMAC foi calculado.
        chave (bytes): A chave secreta compartilhada para o HMAC.

    Returns:
        bool: Verdadeiro se o HMAC recebido corresponde ao HMAC calculado, falso caso contrário.
    '''
    keyid = struct.unpack("!I", packet[-36:-32])[0]
    if keyid != 1:
        return False
    received_digest = packet[-32:]
    
    calculated_digest = calculate_hmac(packet[:-32], chave)

    return hmac.compare_digest(received_digest, calculated_digest)


def create_ntp_response(received_packet, recv_time):
    '''
    Cria um pacote NTP de resposta para um pacote NTP recebido.

    Args:
        received_packet (bytes): O pacote NTP recebido.
        recv_time (float): O tempo de recebimento do pacote.

    Returns:
        bytes: O pacote NTP de resposta, ou None se o HMAC falhar.
    '''
    hmac_position = len(received_packet) - 32
    if hmac_position < 0:
        print("Error: Packet too short to contain HMAC")
        return None  # Evita processar pacotes inválidos

    extracted_data = received_packet[:-32]  # Remove os últimos 32 bytes (HMAC)
    extracted_hmac = received_packet[-32:]  # Últimos 32 bytes são o HMAC


    if not verify_hmac(extracted_data, SHARED_SECRET, extracted_hmac):
        print("HMAC verification failed")
        return None

    recv_time_ntp = to_NTP_timestamp(recv_time + 2208988800)
    transmit_time = time.time() + 2208988800
    transmit_time_ntp = to_NTP_timestamp(transmit_time)
    origin_timestamp = received_packet[40:48]

    packet = packet_builder(
        LI=0, VN=4, mode=4, stratum=2, poll=0, precision=0,
        rootdelay=0, rootdisp=0, refid=0,
        reftime=b'\x00' * 8, org=origin_timestamp, rec=recv_time_ntp,
        xmt=transmit_time_ntp, keyid=1, chave=SHARED_SECRET  # Inclui keyid e chave
    )
    
    return packet


def run_ntp_server(port=LOCAL_NTP_PORT):
    '''
    Roda um servidor NTP na porta especificada.

    Args:
        port (int): A porta na qual o servidor NTP deve

    Returns:
        None
    '''
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