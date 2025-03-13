import hmac
import hashlib

def calcular_hmac(data, chave):
    """
    Calcula o HMAC-SHA256 para os dados fornecidos usando a chave fornecida.

    Args:
        data (bytes): Os dados para os quais o HMAC será calculado.
        chave (bytes): A chave secreta compartilhada para o HMAC.

    Returns:
        bytes: O HMAC-SHA256 dos dados.
    """
    return hmac.new(chave, data, hashlib.sha256).digest()

def verificar_hmac(data, chave, hmac_recebido):
    """
    Verifica se o HMAC-SHA256 recebido corresponde aos dados e à chave fornecidos.

    Args:
        data (bytes): Os dados para os quais o HMAC foi calculado.
        chave (bytes): A chave secreta compartilhada para o HMAC.
        hmac_recebido (bytes): O HMAC-SHA256 recebido para verificação.

    Returns:
        bool: Verdadeiro se o HMAC recebido corresponde ao HMAC calculado, falso caso contrário.
    """
    hmac_calculado = calcular_hmac(data, chave)
    return hmac.compare_digest(hmac_recebido, hmac_calculado)