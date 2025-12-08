from lexems import *
from pprint import pprint


class AddressType:
    IMMEDIATE = 0
    RELATIVE = 2
    DIRECT = 1


class AddressFormat:
    ABSOLUTE = 0
    MOVABLE = 1


def address_type(ops: List[Operand]) -> int:
    if any(isinstance(op, RelativeIdentifier) for op in ops):
        return AddressType.RELATIVE
    if any(isinstance(op, Identifier) for op in ops):
        return AddressType.DIRECT
    return AddressType.IMMEDIATE
    # return int(any(isinstance(op, Identifier) for op in ops))


def display_value(ops: List[Operand], symbol_table, section, expected_size, idr) -> str:
    try:
        vals = [op.resolve_value(symbol_table, section, idr) for op in ops]
        try:
            if expected_size == 1:
                return ""
            strs_pattern = match_op_pattern(ops, XString) or match_op_pattern(
                ops, CString
            )
            if expected_size == 2:
                if match_op_pattern(ops, Number, Number):
                    return "".join(f"{val:01x}" for val in vals)
                if match_op_pattern(ops, Number) or strs_pattern:
                    return "".join(f"{val:02x}" for val in vals)
            if expected_size == 3:
                if match_op_pattern(ops, Number):
                    return "".join(f"{val:04X}" for val in vals)
            if expected_size == 4 or strs_pattern:
                return "".join(f"{val:06X}" for val in vals)
        except:
            return "".join(str(val) for val in vals)
    except KeyError:
        return ""


def byte_display(ops: List[Operand]):
    if match_op_pattern(ops, Number):
        val = ops[0].resolve_value()
        return f"{val:02x}"
    if match_op_pattern(ops, CString):
        val = ops[0].data
        return "".join(f"{ord(c):02x}" for c in val)
    if match_op_pattern(ops, XString):
        val = ops[0].data
        return "0" * ((2 - (len(val) % 2)) % 2) + val


def word_display(ops: List[Operand]):
    if match_op_pattern(ops, Number):
        val = ops[0].resolve_value()
        return f"{val:06X}"
    if match_op_pattern(ops, CString):
        val = ops[0].data
        return "".join(f"{ord(c):06X}" for c in val)
    if match_op_pattern(ops, XString):
        val = ops[0].data
        return "0" * ((6 - (len(val) % 6)) % 6) + val


@dataclass
class InterCode:
    def __str__(self):
        pass


@dataclass
class TCode(InterCode):
    adr: int
    size: int
    opcode: int | None
    ops: List[Operand]

    def __str__(self):
        vals = display_value(self.ops, None, None, self.size, self.size + self.adr)
        if self.opcode is None:
            return f"T {self.adr:06X} {self.size:X} {vals}"
        return f"T {self.adr:06X} {self.size:X} {self.opcode:02X}{vals}"


@dataclass
class TBinCode(InterCode):
    adr: int
    size: int
    binary: str

    def __str__(self):
        return f"T {self.adr:06X} {self.size:X} {self.binary}"


@dataclass
class HCode(InterCode):
    label: str
    adr: int
    size: int | None

    def __str__(self):
        if self.size is None:
            return f"H {self.label} {self.adr:06X}"
        else:
            return f"H {self.label} {self.adr:06X} {self.size:X}"


@dataclass
class ECode(InterCode):
    adr: int

    def __str__(self):
        return f"E {self.adr:06X}"


@dataclass
class MCode(InterCode):
    adr: int
    name: str | None

    def __str__(self):
        if self.name:
            return f"M {self.adr:06X} {self.name}"
        return f"M {self.adr:06X}"


class DCode(TCode):
    def __init__(self, name: Identifier):
        super().__init__(adr=0, size=4, opcode=None, ops=[name])
        self.name = name

    def __str__(self):
        vals = display_value(self.ops, None, self.adr, self.size, self.adr + self.size)
        return f"D {self.name} {vals}"


@dataclass
class RCode(InterCode):
    name: str

    def __str__(self):
        return f"R {self.name}"


def first_pass_simple_dict(
    parsed_lines: List[ParsedLine],
    op_table_dict: Dict[str, Tuple[int, int]],
    adr_method: int,
):
    # Теперь symbol_table: section -> name -> type{adr: int, type: str}

    current_section = ""
    section_existence = set()

    section_symbols: Dict[str, Dict[str, Any]] = {}
    # Все равно промежуточная табличка, стоит ли разбивать ее на секции?
    symbol_table_blank_lines = {}

    def validate_symbol_table() -> None:
        for name in symbol_table_blank_lines[current_section]:
            errors.append(f"Есть ссылка на несуществующее символическое имя {name}")

    auxiliary_table = []
    errors = []

    def result():
        # result_table = [process_intercode(code, symbol_table, op_table_dict) for code in auxiliary_table]
        result_table = [str(line) for line in auxiliary_table]
        return (
            (None, section_symbols, errors)
            if errors
            else (result_table, section_symbols, [])
        )

    location_counter = 0
    address_space = [0]
    start_addr = 0
    start_found = False
    end_found = False

    modification_table: List[Tuple[int, str]] = []

    def print_modification_table():
        nonlocal modification_table
        for location, name in modification_table:
            symbol = section_symbols[current_section][name]
            if symbol["type"] == "EXTREF":
                auxiliary_table.append(MCode(location, name))
            else:
                auxiliary_table.append(MCode(location, None))
        modification_table = []

    start_inx = len(auxiliary_table)

    def validate_address_range(addr: int, context: str = "") -> str | None:
        if not (0x000000 <= addr <= 0xFFFFFF):
            return f"Адрес {hex(addr)} вне диапазона 000000-FFFFFF ({context})"

    def validate_operands_basic(
        mnemonic: str, operands: List[Operand], op_size: int
    ) -> str | None:
        not_correct_format = f"Некорректный формат команды {mnemonic} в {op_size} байт"
        if op_size == 1 and not match_op_pattern(operands):
            return not_correct_format
        strs_matches = match_op_pattern(operands, CString) or match_op_pattern(
            operands, XString
        )
        if op_size == 2:
            if not (
                match_op_pattern(operands, Number)
                or match_op_pattern(operands, Register, Register)
                or strs_matches
            ):
                return not_correct_format
            if match_op_pattern(operands, Number):
                op_value = operands[0].resolve_value()
                if not (0x00 <= op_value <= 0xFF):
                    return f"Непосредственное значение {op_value} не влезает в 1 байт"
            if strs_matches:
                if operands[0].size() > 1:
                    return f"Строковая константа c'{operands[0].resolve_value()}' не влезает в 1 байт"
        if op_size == 3:
            if not match_op_pattern(operands, RelativeIdentifier):
                return not_correct_format
        if op_size == 4:
            if not (
                match_op_pattern(operands, Identifier)
                or match_op_pattern(operands, Number)
                or strs_matches
            ):
                return not_correct_format
            if match_op_pattern(operands, Number) or strs_matches:
                op_value = operands[0].resolve_value()
                if valid_err := validate_address_range(op_value, f"Операнд {mnemonic}"):
                    return valid_err

    def check_adr_method(ops):
        if adr_method == 0 and any(isinstance(op, RelativeIdentifier) for op in ops):
            return "Встретился операнд с относительной адресацией"
        if adr_method == 1 and any(isinstance(op, Identifier) for op in ops):
            return "Встретился операнд с прямой адресацией"

    def set_location_counter(new_adr):
        nonlocal location_counter
        location_counter = new_adr
        address_space.append(new_adr)

    def resolve_or_id(op: Operand, symbol_table, section, idr):
        try:
            return Number(op.resolve_value(symbol_table, section, idr))
        except ValueError as err:
            raise err
        except:
            return op

    def resolve_t_record(trecord: TCode, section=""):
        idr = trecord.adr + trecord.size
        trecord.ops = [
            resolve_or_id(op, section_symbols, section, idr) for op in trecord.ops
        ]
        return trecord

    for line_num, line in enumerate(parsed_lines, 1):
        if end_found:
            # lineErr("Команда после END")
            break
        mnemonic = line.command.mnemonic
        ops = line.command.operands
        lineErr = lambda msg: errors.append(
            f"[{current_section}:{location_counter:06X}]: {msg}"
        )

        if mnemonic == "START":
            if start_found:
                lineErr("Повторная директива START")
            start_found = True

            if not (match_op_pattern(ops) or match_op_pattern(ops, Number)):
                lineErr("Неккоректный адрес в START")

            if match_op_pattern(ops, Number):
                location_counter = ops[0].resolve_value()
                address_space = [location_counter]
                start_addr = location_counter

            if addr_err := validate_address_range(location_counter, "адрес загрузки"):
                lineErr(addr_err)
            if location_counter != 0:
                lineErr("Не нулевой адрес загрузки в относительном формате")
            if not line.label:
                lineErr("Отстуствует метка у директивы START")
            current_section = line.label
            section_existence.add(current_section)
            # auxiliary_table.append(f"H {line.label} {location_counter:06x} ")
            start_inx = len(auxiliary_table)
            auxiliary_table.append(HCode(line.label, location_counter, None))
            section_symbols[current_section] = dict()
            continue

        if not start_found:
            lineErr("Программа не начинается с директивы START")
            # continue

        if mnemonic == "CSECT":
            if not line.label:
                lineErr("Отсутствует метка у директивы CSECT")
            print_modification_table()
            current_section = line.label
            if current_section in section_existence:
                lineErr(f'Повторная секция "{current_section}" не допустима')
            section_existence.add(current_section)
            prog_size = location_counter - start_addr
            auxiliary_table[start_inx].size = prog_size
            start_inx = len(auxiliary_table)
            location_counter = 0
            auxiliary_table.append(HCode(current_section, location_counter, None))
            section_symbols[current_section] = dict()
            continue

        # Обработка меток
        if line.label:
            if (
                line.label in section_symbols[current_section]
                and section_symbols[current_section][line.label]["addr"] is not None
            ):
                lineErr(f"Дублирующаяся метка '{line.label}'")
            else:
                if addr_err := validate_address_range(
                    location_counter, f" для метки '{line.label}'"
                ):
                    lineErr(addr_err)
                if line.label not in section_symbols[current_section]:
                    section_symbols[current_section][line.label] = {
                        "type": None,
                        "addr": None,
                    }
                section_symbols[current_section][line.label]["addr"] = location_counter
                if line.label in symbol_table_blank_lines:
                    for inx in symbol_table_blank_lines[line.label]:
                        trecord: TCode = auxiliary_table[inx]
                        try:
                            trecord = resolve_t_record(trecord, current_section)
                        except Exception as err:
                            lineErr(err)
                    symbol_table_blank_lines.pop(line.label)

        if mnemonic == "END":
            if not (match_op_pattern(ops) or match_op_pattern(ops, Number)):
                lineErr("Неккоректный формат директивы END")
            end_found = True
            prog_size = location_counter - start_addr
            # auxiliary_table = [i + f"{prog_size:x}" if i.startswith("H") else i for i in auxiliary_table]
            auxiliary_table[start_inx].size = prog_size
            addr = start_addr
            if match_op_pattern(ops, Number):
                addr = ops[0].resolve_value()
            if addr not in address_space:
                lineErr("Некорректный адрес точки входа")

            # Формирование модификаторов
            print_modification_table()
            # for location in modification_table:
            #     # auxiliary_table.append(f"M {location:06X}")
            #     auxiliary_table.append(MCode(location))

            # auxiliary_table.append(f"E {addr:06x}")
            auxiliary_table.append(ECode(addr))
            # auxiliary_table.append((location_counter, line))
            continue

        # auxiliary_table.append((location_counter, line))

        # Обработка директив и команд
        if mnemonic == "WORD":
            if (
                match_op_pattern(ops, Number)
                or match_op_pattern(ops, CString)
                or match_op_pattern(ops, XString)
            ):
                if match_op_pattern(ops, Number):
                    value = ops[0].resolve_value()
                    if not (0 <= value <= 0xFFFFFF):
                        lineErr(f"Значение {value} выходит за пределы 3-байтного слова")
                size = 3 * ops[0].size()
                # auxiliary_table.append(f"T {location_counter:06X} {size:X} {word_display(ops)}")
                auxiliary_table.append(
                    TBinCode(location_counter, size, word_display(ops))
                )
                set_location_counter(location_counter + size)
            else:
                lineErr("Некорректный операнд директивы WORD")

        elif mnemonic == "RESW":
            if match_op_pattern(ops, Number):
                words = ops[0].resolve_value()
                if words < 0:
                    lineErr("Отрицательное количество слов в RESW")
                size = 3 * words
                new_address = location_counter + size
                if addr_err := validate_address_range(new_address, "после RESW"):
                    lineErr(addr_err)
                auxiliary_table.append(TBinCode(location_counter, size, ""))
                set_location_counter(new_address)
            else:
                lineErr("Некорректный формат директивы RESW")

        elif mnemonic == "BYTE":
            if (
                match_op_pattern(ops, Number)
                or match_op_pattern(ops, CString)
                or match_op_pattern(ops, XString)
            ):
                size = ops[0].size()
                if match_op_pattern(ops, Number):
                    value = ops[0].resolve_value()
                    if not (0 <= value <= 0xFF):
                        lineErr(f"Значение {value} выходит за пределы 1 Байта")
                # auxiliary_table.append(f"T {location_counter:06X} {size:X} {byte_display(ops)}")
                auxiliary_table.append(
                    TBinCode(location_counter, size, byte_display(ops))
                )
                set_location_counter(location_counter + size)
            else:
                lineErr("Некорректный операнд директивы BYTE")

        elif mnemonic == "RESB":
            if match_op_pattern(ops, Number):
                bytes = ops[0].resolve_value()
                if bytes < 0:
                    lineErr("Отрицательное количество слов в RESB")
                size = bytes
                new_address = location_counter + size
                if addr_err := validate_address_range(new_address, "после RESB"):
                    lineErr(addr_err)
                # auxiliary_table.append(f"T {location_counter:06X} {size:X}")
                auxiliary_table.append(TBinCode(location_counter, size, ""))
                set_location_counter(new_address)
            else:
                lineErr("Некорректный формат директивы RESB")

        elif mnemonic == "EXTDEF":
            if not match_op_pattern(ops, Identifier) or line.label:
                lineErr("Некорректный формат EXTDEF")
            else:
                for op in ops:
                    if op.data in section_symbols[current_section]:
                        record = section_symbols[current_section][op.data]
                        if record["type"] is None:
                            record["type"] = "EXTDEF"
                        else:
                            lineErr("Переопределение на EXTDEF")
                    else:
                        section_symbols[current_section][op.data] = {
                            "type": "EXTDEF",
                            "addr": None,
                        }
                    auxiliary_table.append(DCode(op))
                    symbol_table_blank_lines.setdefault(op.data, []).append(
                        len(auxiliary_table) - 1
                    )

        elif mnemonic == "EXTREF":
            if not match_op_pattern(ops, Identifier) or line.label:
                lineErr("Некорректный формат EXTREF")
            else:
                for op in ops:
                    if (
                        op.data in section_symbols[current_section]
                        and section_symbols[current_section][op.data]["type"]
                        is not None
                    ):
                        lineErr(f"Некорректный extref")
                    section_symbols[current_section][op.data] = {
                        "addr": None,
                        "type": "EXTREF",
                    }
                    auxiliary_table.append(RCode(op.data))

        elif mnemonic in op_table_dict:
            opcode, op_size = op_table_dict[mnemonic]

            # Проверка операндов команды
            if operands_err := validate_operands_basic(
                mnemonic, line.command.operands, op_size
            ):
                lineErr(operands_err)

            new_address = location_counter + op_size
            if addr_err := validate_address_range(
                new_address, f" после команды {mnemonic}"
            ):
                lineErr(addr_err)

            addrtype = address_type(ops)
            op_addr_code = (opcode << 2) | addrtype
            disp = display_value(ops, section_symbols, "", op_size, new_address)
            # auxiliary_table.append(f"T {location_counter:06X} {op_size} {op_addr_code:02X}{disp}")
            trecord = TCode(location_counter, op_size, op_addr_code, ops)
            try:
                trecord = resolve_t_record(trecord, current_section)
            except Exception as err:
                lineErr(err)
            auxiliary_table.append(trecord)

            if address_type(ops) == AddressType.DIRECT:
                for op in ops:
                    modification_table.append((location_counter, str(op)))

            set_location_counter(new_address)

            if err := check_adr_method(ops):
                lineErr(err)

            for i in ops:
                if (
                    isinstance(i, Identifier) or isinstance(i, RelativeIdentifier)
                ) and i.data not in section_symbols[current_section]:
                    section_symbols[current_section][i.data] = {
                        "addr": None,
                        "type": None,
                    }
                    symbol_table_blank_lines.setdefault(i.data, []).append(
                        len(auxiliary_table) - 1
                    )

        else:
            lineErr(f"Неизвестная команда '{mnemonic}'")

        yield result()

    # Финальные проверки
    if not start_found:
        errors.append("Отсутствует директива START")
    if not end_found:
        errors.append("Отсутствует директива END")

    if addr_err := validate_address_range(location_counter, "конечный адрес"):
        errors.append(addr_err)

    # Проверка на корректность тси
    # Будто бы мы должны делать это после каждой секции
    # for section in symbol_table:
    #     for name in symbol_table[section]:
    #         symbol = symbol_table[section][name]
    #         if symbol["addr"] is None and symbol["type"] != "EXTREF":
    #             errors.append(f"Есть ссылка на несуществующее символическое имя {i}")

    yield result()
