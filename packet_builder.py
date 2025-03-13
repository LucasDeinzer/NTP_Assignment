import struct
from ntp_hmac import calcular_hmac

def packet_builder(
    LI,                             # Leap Indicator,       2 bits
    VN,                             # Version Number        3 bits
    mode,                           # mode                  3 bits      3 - client, 4 - server.
    stratum,                        # stratum               8 bits      não usado pelo client
    poll,                           # poll exponent         8 bits      frequência de envio de mensagens. 0 = uma só mensagem
    precision,                      # precision exponent    8 bits
    rootdelay,                      # root delay            32 bits, NTP short  
    rootdisp,                       # root dispersion       32 bits, NTP short
    refid,                          # reference ID          32 bits
    reftime,                        # reference timestamp   64 bits, NTP timestamp
    org,                            # origin timestamp      64 bits, NTP timestamp
    rec,                            # receive timestamp     64 bits, NTP timestamp
    xmt,                            # transmit timestamp    64 bits, NTP timestamp
    exf1=None,                      # Extension Field 1     variável
    exf2=None,                      # Extension Field 2     variável
    keyid=None,                     # key ID                32 bits
    chave=None                      # message digest        128 bits MD5 hash
):
    # Montamos o cabeçalho
    packet = struct.pack(
        "!BBBbIII",
        (LI << 6) | (VN << 3) | mode,   # LI, VN, mode  (1 byte)
        stratum,                        # stratum       (1 byte)
        poll,                           # poll          (1 byte)
        precision,                      # precision     (1 byte)
        rootdelay,                      # rootdelay     (4 bytes)
        rootdisp,                       # rootdisp      (4 bytes)
        refid                           # refid         (4 bytes)
    )
    
    # Adiciona os timestamps de 64 bits
    packet += reftime + org + rec + xmt
    
    # Adiciona Extension Field 1, se existir
    if exf1:
        exf1_padded = exf1 + b"\x00" * ((4 - len(exf1) % 4) % 4)  # Padding para múltiplo de 4 bytes
        packet += exf1_padded

    # Adiciona Extension Field 2, se existir
    if exf2:
        exf2_padded = exf2 + b"\x00" * ((4 - len(exf2) % 4) % 4)  # Padding para múltiplo de 4 bytes
        packet += exf2_padded
    
    # Adiciona o HMAC-SHA256 se keyid e chave existirem
    if keyid is not None and chave is not None:
        digest = calcular_hmac(packet, chave)
        packet += struct.pack("!I", keyid)  # Converte o keyid para binário
        packet += digest                    # Concatena o digest no final do pacote
        
    return packet