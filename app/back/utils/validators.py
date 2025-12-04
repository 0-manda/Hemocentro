import re

def only_numbers(value: str) -> str:
    return ''.join(filter(str.isdigit, value or ''))

def is_cnpj(value: str) -> bool:
    if not value:
        return True
    
    c = only_numbers(value)
    if len(c) != 14 or c == c[0] * 14:
        return False
    
    def calc_digit(digs):
        s = 0
        peso = len(digs) - 7
        for ch in digs:
            s += int(ch) * peso
            peso -= 1
            if peso < 2:
                peso = 9
        res = 11 - (s % 11)
        return '0' if res >= 10 else str(res)
    
    return c[-2:] == calc_digit(c[:12]) + calc_digit(c[:12] + calc_digit(c[:12]))

def is_cpf(value: str) -> bool:
    if not value:
        return True
    
    p = only_numbers(value)
    if len(p) != 11 or p == p[0] * 11:
        return False
    
    def calc_digit(digs):
        s = 0
        peso = len(digs) + 1
        for ch in digs:
            s += int(ch) * peso
            peso -= 1
        res = 11 - (s % 11)
        return '0' if res >= 10 else str(res)
    
    return p[-2:] == calc_digit(p[:9]) + calc_digit(p[:9] + calc_digit(p[:9]))