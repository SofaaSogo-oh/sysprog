from dataclasses import dataclass
from typing import *


class Operand:
    def size(self):
        """Размер в байтах при использовании в данных (BYTE/WORD)"""
        pass

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        """Получение числового значения (для непосредственных операндов)"""
        pass


@dataclass
class ParsedCommand:
    mnemonic: str
    operands: List[Operand]

    def __str__(self):
        return f"{self.mnemonic} {", ".join(map(str, self.operands))}"


@dataclass
class ParsedLine:
    label: str
    command: ParsedCommand

    def __str__(self):
        return (f"{self.label}: " if self.label else "") + str(self.command)


@dataclass
class Identifier(Operand):
    data: str

    def __str__(self):
        return self.data

    def size(self):
        return 3

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        try:
            print("FOO")
            if symbol_table[section][self.data]['addr'] is None:
                print("BAR")
                return 0
            return symbol_table[section][self.data]['addr']
        except:
            raise KeyError(f"Неизвестное символическое имя: {self.data}")
        # if (
        #     symbol_table
        #     and section in symbol_table
        #     and self.data in symbol_table[section]
        # ):
        #     return symbol_table[section][self.data]['addr']
        # else:
        #     raise KeyError(f"Неизвестное символическое имя: {self.data}")


@dataclass
class RelativeIdentifier(Operand):
    data: str

    def __str__(self):
        return f"[{self.data}]"

    def size(self):
        return 2

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        try:
            if symbol_table[section][self.data]['addr'] is None:
                raise ValueError("Внешняя ссылка")
            dlta = symbol_table[section][self.data]['addr'] - idr
            adlta = abs(dlta)
            return adlta if dlta > 0 else ((~adlta + 1) & 0xFFFF)
        except ValueError:
            raise ValueError("Внешняя ссылка в относительной адресации")
        except:
            raise KeyError(f"Неизвестное символическое имя: {self.data}")


@dataclass
class Number(Operand):
    value: int

    def __str__(self):
        return str(self.value)

    def size(self):
        return 1

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        return self.value


@dataclass
class Register(Operand):
    reg: int

    def __str__(self):
        return f"R{self.reg:X}"

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        return self.reg & 0xF

    def size(self):
        return 0


@dataclass
class CString(Operand):
    data: str

    def __str__(self):
        return f"c'{self.data}'"

    def size(self):
        return len(self.data)

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        return int("".join(map(lambda x: f"{ord(x):02x}", self.data)), 16)


@dataclass
class XString(Operand):
    data: str

    def __str__(self):
        return f"x'{self.data}'"

    def size(self):
        return (len(self.data) + 1) // 2

    def resolve_value(self, symbol_table=None, section=None, idr=0):
        return int(self.data, 16)


def match_op_pattern(operands: List[Operand], *pattern: List[Type]) -> bool:
    return len(operands) == len(pattern) and all(
        isinstance(op, tp) for op, tp in zip(operands, pattern)
    )


def get_operand_with_type(operand, expected_type, description):
    if operand is None:
        raise ValueError(f"{description}: операнд отсутствует")
    if not isinstance(operand, expected_type):
        raise ValueError(
            f"{description}: ожидается {expected_type.__name__}, получен {type(operand).__name__}"
        )
    return operand
