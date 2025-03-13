import struct
import time

NTP_DELTA = 2208988800  # Diferença de tempo entre 1900 e 1970

def to_NTPtimestamp(tempo):
    inteiro = int(tempo)
    fracionario = int((tempo - inteiro) * (2**32))
    return struct.pack("!II", inteiro, fracionario)

def timestamp_to_double(timestamp):
    seconds, fraction = timestamp
    return seconds + (fraction / 2**32)

def NTP_timestamp():
    diferenca_ntp = 2208988800
    timestamp = time.time() + diferenca_ntp
    inteiro = int(timestamp)
    fracionario = int((timestamp - inteiro) * (2**32))
    return struct.pack("!II", inteiro, fracionario)