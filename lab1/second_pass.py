from lexems import *


def address_type(ops: List[Operand]) -> int:
    return int(any(isinstance(op, Identifier) for op in ops))


def display_value(ops: List[Operand], symbol_table, expected_size):
    vals = [op.resolve_value(symbol_table) for op in ops]
    if expected_size == 1:
        return ""
    strs_pattern = match_op_pattern(ops, XString) or match_op_pattern(ops, CString)
    if expected_size == 2:
        if match_op_pattern(ops, Register, Register):
            return "".join(f"{val:01x}" for val in vals)
        if match_op_pattern(ops, Number) or strs_pattern:
            return "".join(f"{val:02x}" for val in vals)
    if expected_size == 4 or strs_pattern:
        return "".join(f"{val:06X}" for val in vals)

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


def second_pass(
    auxalirity_table: List[Tuple[int, ParsedLine]],
    symbol_table: Dict[str, int],
    op_table_dict: Dict[str, Tuple[int, int]],
) -> Tuple[List[str], List[str]]:
    machine_code = []
    errors = []
    result = lambda: (None, errors) if errors else (machine_code, [])

    ### Формирование заголовка
    try:
        start_line_inx, start_line = auxalirity_table[0]
        end_line_inx, end_line = auxalirity_table[-1]
        machine_code.append(
            f"H {start_line.label} {start_line_inx:06X} {end_line_inx - start_line_inx:X}"
        )
    except ValueError as err:
        errors.append(str(err))
        return result()

    ### Формирование тела
    # Подсчет размера команд по смещениям
    adrss = [adr for adr, _ in auxalirity_table]
    dltas = [adr2 - adr1 for adr1, adr2 in zip([0] + adrss, adrss + [0])][1:]
    for dlta, (location, line) in zip(dltas, auxalirity_table):
        lineErr = lambda msg: errors.append(f"Строка {location}: {msg}")
        mnemonic = line.command.mnemonic
        ops = line.command.operands

        # Отдельно
        if mnemonic in ["START", "END"]:
            continue
        
        if mnemonic in ["RESW", "RESB"]:
            machine_code.append(f"T {location:06X} {dlta}")
        
        if mnemonic == "BYTE":
            machine_code.append(f"T {location:06X} {dlta} {byte_display(ops)}")
        if mnemonic == "WORD":
            machine_code.append(f"T {location:06X} {dlta} {word_display(ops)}")
        
        try:
            if mnemonic in op_table_dict:
                opcode, expected_size = op_table_dict[mnemonic]
                op_adr_code = (opcode << 2) | address_type(ops)
                machine_code.append(
                    f"T {location:06X} {dlta} {op_adr_code:02x}{display_value(ops, symbol_table, expected_size)}"
                )
        except KeyError as err:
            lineErr(f"Неизвестное символическое имя ({err})")

    ### Формирование конца
    load_address = start_line_inx
    try:
        load_address = get_operand_with_type(
            end_line.command.operands[0], Number, "Адрес"
        ).resolve_value()
    except IndexError:
        pass
    except ValueError as err:
        errors.append(f"Некорректный операнд директивы END: {err}")

    if not any(addr == load_address for addr, _ in auxalirity_table):
        errors.append("Задан некорректный адрес точки входа")

    machine_code.append(f"E {load_address:06X}")

    return result()
