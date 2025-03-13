import struct
import time


NTP_DELTA = 2208988800  # Diferença de tempo entre 1900 e 1970


def to_NTP_timestamp(tempo):
    '''
    Converte um tempo em segundos para um timestamp NTP.

    Args:
        tempo (float): O tempo em segundos.

    Returns:
        bytes: O timestamp NTP correspond
    '''
    integer_time = int(tempo)
    fractional_time = int((tempo - integer_time) * (2**32))

    return struct.pack("!II", integer_time, fractional_time)


def timestamp_to_double(timestamp):
    '''
    Converte um timestamp NTP para um número de ponto flutuante.

    Args:
        timestamp (tuple): Um timestamp NTP de 64 bits.

    Returns:
        float: O número de ponto flutuante correspondente
    '''
    seconds, fraction = timestamp

    return seconds + (fraction / 2**32)


def NTP_timestamp():
    '''
    Retorna o timestamp NTP atual.

    Returns:
        bytes: O timestamp NTP atual
    '''
    diferenca_ntp = 2208988800
    timestamp = time.time() + diferenca_ntp
    integer_timestamp = int(timestamp)
    fractional_timestamp = int((timestamp - integer_timestamp) * (2**32))
    
    return struct.pack("!II", integer_timestamp, fractional_timestamp)