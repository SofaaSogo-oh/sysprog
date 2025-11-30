from lexems import *
from pprint import pprint
from itertools import groupby


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
    vals = [op.resolve_value(symbol_table, section, idr) for op in ops]
    try:
        if expected_size == 1:
            return ""
        strs_pattern = match_op_pattern(ops, XString) or match_op_pattern(ops, CString)
        if expected_size == 2:
            if match_op_pattern(ops, Register, Register):
                return "".join(f"{val:01x}" for val in vals)
            if match_op_pattern(ops, Number) or strs_pattern:
                return "".join(f"{val:02x}" for val in vals)
        if expected_size == 3:
            if match_op_pattern(ops, RelativeIdentifier):
                return "".join(f"{val:04X}" for val in vals)
        if expected_size == 4 or strs_pattern:
            return "".join(f"{val:06X}" for val in vals)
    except:
        return "".join(str(val) for val in vals)


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
    symbol_table: Dict[str, Dict[str, Any]],
    op_table_dict: Dict[str, Tuple[int, int]],
) -> Tuple[List[str], List[str], List[Tuple[int, str, str]]]:
    machine_code = []
    errors = []
    result = lambda: (None, errors, []) if errors else (machine_code, [], modification_table)

    # ### Формирование тела
    # Подсчет размера команд по смещениям
    adrss = [adr for adr, _, _ in auxalirity_table]
    dltas = [adr2 - adr1 for adr1, adr2 in zip([0] + adrss, adrss + [0])][1:]
    sections = groupby(zip(dltas, auxalirity_table), key=lambda x: x[1][2])
    modification_table : List[(int, str, str)] = []

    for section_name, section_iterator in sections:
        section = list(section_iterator)
        _, (last_loc, _, _) = section[-1]
        _, (first_loc, _, _) = section[0]
        prog_size = last_loc - first_loc
        section_modification_table: List[(int, str)] = []
        def write_mod_table():
            print(section_modification_table)
            for loc, name in section_modification_table:
                symbol = symbol_table[section_name][name]
                if symbol["type"] == "EXTREF":
                    machine_code.append(f"M {loc:06X} {name}")
                else:
                    machine_code.append(f"M {loc:06X}")
                modification_table.append((loc, name, section_name))

        for dlta, (location, line, _) in section:
            lineErr = lambda msg: errors.append(
                f"[{section_name}:{location:06X}]: {msg}"
            )
            mnemonic = line.command.mnemonic
            ops = line.command.operands
            # if mnemonic in ["[ESECT]"]:
            #     write_mod_table()
            #     print(line)
            #     machine_code.append(f"E {location:06X}")
            if mnemonic in ["[ESECT]", "END"]:
                write_mod_table()
                load_address = first_loc
                if match_op_pattern(ops, Number):
                    load_address = ops[0].resolve_value()
                if load_address not in [loc for _, (loc, _, _) in section]:
                    lineErr("Некорректный адрес точки входа")
                machine_code.append(f"E {0:06X}")
            if mnemonic == "START":
                machine_code.append(f"H {line.label} {location:06X} {prog_size:X}")
            if mnemonic in ["RESW", "RESB"]:
                machine_code.append(f"T {location:06X} {dlta}")
            if mnemonic == "EXTREF":
                machine_code.append(f"R {ops[0]}")
            if mnemonic == "CSECT":
                machine_code.append(f"H {line.label} {location:06X} {prog_size:X}")
            if mnemonic == "BYTE":
                machine_code.append(f"T {location:06X} {dlta} {byte_display(ops)}")
            if mnemonic == "WORD":
                machine_code.append(f"T {location:06X} {dlta} {word_display(ops)}")

            try:
                if mnemonic == "EXTDEF":
                    val = display_value(
                        ops, symbol_table, section_name, 4, location + dlta
                    )
                    machine_code.append(f"D {ops[0]} {val}")
                if mnemonic in op_table_dict:
                    opcode, expected_size = op_table_dict[mnemonic]
                    addrtype = address_type(ops)

                    op_adr_code = (opcode << 2) | addrtype
                    op_disp_val = display_value(
                        ops, symbol_table, section_name, expected_size, location + dlta
                    )
                    machine_code.append(
                        f"T {location:06X} {dlta} {op_adr_code:02X}{op_disp_val}"
                    )
                    if address_type(ops) == AddressType.DIRECT:
                        for op in ops:
                            section_modification_table.append((location, str(op)))
            except Exception as err:
                lineErr(str(err))
    
    print(modification_table)

    return result()
