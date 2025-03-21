import socket
import time
import struct
from ntp_timestamp import to_NTP_timestamp, timestamp_to_double
from packet_builder import packet_builder
from ntp_hmac import calculate_hmac

DEFAULT_NTP_SERVER = "pool.ntp.org"
DEFAULT_NTP_PORT = 123
LOCAL_NTP_PORT = 5000
SHARED_SECRET = b'supersecret'  # Chave compartilhada para HMAC-SHA256


def create_ntp_request(version=4, mode=3, flag=0):
    '''
    Cria um pacote NTP de requisição para o servidor NTP.

    Args:
        version (int): A versão do protocolo NTP.
        mode (int): O modo da mensagem NTP.
        flag (int): Flag para indicar se a requisição é para um servidor específico.

    Returns:
        bytes: O pacote NTP de requisição.
    '''
    current_time = time.time() + 2208988800
    packet = packet_builder(
        LI=0, VN=version, mode=mode, stratum=0, poll=0, precision=0,
        rootdelay=0, rootdisp=0, refid=0,
        reftime=struct.pack("!Q", 0), org=struct.pack("!Q", 0), rec=struct.pack("!Q", 0),
        xmt=to_NTP_timestamp(current_time), keyid=1, chave=SHARED_SECRET
    )

    if flag == 0:
        return packet

    else:
        hmac_calculado = calculate_hmac(packet[:-32], SHARED_SECRET)
        packet_with_hmac = packet[:-32] + hmac_calculado

        return packet_with_hmac


def parse_ntp_response(packet):
    '''
    Extrai os timestamps T2 e T3 de uma resposta NTP.

    Args:
        packet (bytes): O pacote NTP de resposta.

    Returns:
        tuple: Uma tupla contendo os timestamps T2 e T3.
    '''
    unpacked = struct.unpack("!12I", packet[:48])
    t2 = timestamp_to_double((unpacked[8], unpacked[9]))
    t3 = timestamp_to_double((unpacked[10], unpacked[11]))

    return t2 - 2208988800, t3 - 2208988800


def get_ntp_time(ntp_server, port=DEFAULT_NTP_PORT, version=4):
    '''
    Envia uma requisição NTP para um servidor NTP e retorna os timestamps relevantes.

    Args:
        ntp_server (str): O endereço IP ou nome do servidor NTP.
        port (int): A porta do servidor NTP.
        version (int): A versão do protocolo NTP.

    Returns:
        tuple: Uma tupla contendo os timestamps T1, T4, T2, T3, RTT e offset.
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if ntp_server == "pool.ntp.org":
        flag = 0
    else:
        flag = 1

    packet = create_ntp_request(version=version, mode=3, flag=flag)
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
    if server_address == DEFAULT_NTP_SERVER:
        print(f"Using default NTP server: {DEFAULT_NTP_SERVER}")
        
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