from lexems import *
from pprint import pprint


def first_pass_simple_dict(
    parsed_lines: List[ParsedLine],
    op_table_dict: Dict[str, Tuple[int, int]],
    adrMethod: int,
):
    # symbol_table = {}
    auxiliary_table = []
    errors = []
    current_section = ""
    section_symbols: Dict[str, Dict[str, Any]] = {}
    section_existence = set()

    location_counter = 0
    start_found = False
    end_found = False
    extdef_flag = True

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
        if adrMethod == 0 and any(isinstance(op, RelativeIdentifier) for op in ops):
            return "Встретился операнд с относительной адресацией"
        if adrMethod == 1 and any(isinstance(op, Identifier) for op in ops):
            return "Встретился операнд с прямой адресацией"

    for line_num, line in enumerate(parsed_lines, 1):
        if end_found:
            # lineErr("Команда после END")
            break
        mnemonic = line.command.mnemonic
        ops = line.command.operands
        lineErr = lambda x: errors.append(f"Строка {line_num}: {x}")

        if mnemonic == "START":
            if start_found:
                lineErr("Повторная директива START")
            start_found = True

            if not (match_op_pattern(ops) or match_op_pattern(ops, Number)):
                lineErr("Неккоректный адрес в START")

            if match_op_pattern(ops, Number):
                location_counter = ops[0].resolve_value()

            if addr_err := validate_address_range(location_counter, "адрес загрузки"):
                lineErr(addr_err)
            if location_counter != 0:
                lineErr("Не нулевой адрес загрузки в относительном формате")
            if not line.label:
                lineErr("Отстуствует метка у директивы START")
            current_section = line.label
            section_existence.add(current_section)
            auxiliary_table.append((location_counter, line, current_section))
            section_symbols[current_section] = dict()
            continue

        if not start_found:
            lineErr("Программа не начинается с директивы START")
            # continue

        if mnemonic == "CSECT":
            extdef_flag = True
            if not line.label:
                lineErr("Отсутствует метка у директивы CSECT")
            pseudo_record = ParsedLine("", ParsedCommand("[ESECT]", ops))
            auxiliary_table.append((location_counter, pseudo_record, current_section))
            location_counter = 0
            current_section = line.label
            if current_section in section_existence:
                lineErr(f'Повторная секция "{current_section}" не допустима')
            section_existence.add(current_section)
            auxiliary_table.append((location_counter, line, current_section))
            section_symbols[current_section] = dict()
            continue

        # Обработка меток
        if line.label:
            if line.label in section_symbols[current_section]:
                record = section_symbols[current_section][line.label]
                if record["type"] == "EXTDEF" and record["addr"] is None:
                    record["addr"] = location_counter
                else:
                    lineErr("Некорректная метка")
            else:
                section_symbols[current_section][line.label] = {
                    "addr": location_counter,
                    "type": None
                }

        if mnemonic == "END":
            if not (match_op_pattern(ops) or match_op_pattern(ops, Number)):
                lineErr("Неккоректный формат директивы END")
            end_found = True
            auxiliary_table.append((location_counter, line, current_section))
            continue

        auxiliary_table.append((location_counter, line, current_section))

        # Обработка директив и команд
        if mnemonic == "WORD":
            if (
                match_op_pattern(ops, Number)
                or match_op_pattern(ops, CString)
                or match_op_pattern(ops, XString)
            ):
                location_counter += 3 * ops[0].size()
                if match_op_pattern(ops, Number):
                    value = ops[0].resolve_value()
                    if not (0 <= value <= 0xFFFFFF):
                        lineErr(f"Значение {value} выходит за пределы 3-байтного слова")
            else:
                lineErr("Некорректный операнд директивы WORD")

        elif mnemonic == "RESW":
            if match_op_pattern(ops, Number):
                words = ops[0].resolve_value()
                if words < 0:
                    lineErr("Отрицательное количество слов в RESW")
                new_address = location_counter + 3 * words
                if addr_err := validate_address_range(new_address, "после RESW"):
                    lineErr(addr_err)
                location_counter = new_address
            else:
                lineErr("Некорректный формат директивы RESW")

        elif mnemonic == "BYTE":
            if (
                match_op_pattern(ops, Number)
                or match_op_pattern(ops, CString)
                or match_op_pattern(ops, XString)
            ):
                location_counter += ops[0].size()
                if match_op_pattern(ops, Number):
                    value = ops[0].resolve_value()
                    if not (0 <= value <= 0xFF):
                        lineErr(f"Значение {value} выходит за пределы 1 Байта")
            else:
                lineErr("Некорректный операнд директивы BYTE")

        elif mnemonic == "RESB":
            if match_op_pattern(ops, Number):
                bytes = ops[0].resolve_value()
                if bytes < 0:
                    lineErr("Отрицательное количество слов в RESB")
                new_address = location_counter + bytes
                if addr_err := validate_address_range(new_address, "после RESB"):
                    lineErr(addr_err)
                location_counter = new_address
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
                            "type": 'EXTDEF',
                            "addr": None
                        }

        elif mnemonic == "EXTREF":
            if not match_op_pattern(ops, Identifier) or line.label:
                lineErr("Некорректный формат EXTREF")
            else:
                for op in ops:
                    if op.data in section_symbols[current_section]:
                        lineErr(f"Некоррректный extref")
                    section_symbols[current_section][op.data] = {
                        "addr": None,
                        "type": "EXTREF",
                    }

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
            location_counter = new_address
            if err := check_adr_method(ops):
                lineErr(err)

        else:
            lineErr(f"Неизвестная команда '{mnemonic}'")

    # Финальные проверки
    if not start_found:
        errors.append("Отсутствует директива START")
    if not end_found:
        errors.append("Отсутствует директива END")

    if addr_err := validate_address_range(location_counter, "конечный адрес"):
        errors.append(addr_err)
    
    for section_name in section_symbols:
        section = section_symbols[section_name]
        for record_name in section:
            record = section[record_name]
            print(record)
            if record["type"] == "EXTDEF" and record["addr"] is None:
                errors.append("Не всем внешним именам было присвоено значение")
    pprint(section_symbols)

    return (None, None, errors) if errors else (auxiliary_table, section_symbols, [])
