from lexems import *
from parsec import *


@generate
def identifier_parser():
    name = yield regex(r"[A-Za-z_][A-Za-z0-9_]*")
    return name

@generate
def relative_id_parser():
    # name = yield string("[") >> identifier_parser << string("]")
    name = yield string("@") > identifier_parser
    return RelativeIdentifier(name)

@generate
def direct_id_parser():
    name = yield identifier_parser
    return Identifier(name)

@generate
def hexadecimal_number_parser():
    sign = yield optional(string("-"))
    yield string("0x")
    digits = yield regex(r"[0-9A-Fa-f]+")
    value = int(digits, 16)
    return -value if sign else value


@generate
def octal_number_parser():
    sign = yield optional(string("-"))
    yield string("0o")
    digits = yield regex(r"[0-7]+")
    value = int(digits, 8)
    return -value if sign else value

@generate
def binary_number_parser():
    sign = yield optional(string("-"))
    yield string("0b")
    digits = yield regex(r"[0-1]+")
    value = int(digits, 2)
    return -value if sign else value

@generate
def decimal_number_parser():
    sign = yield optional(string("-"))
    digits = yield regex(r"[0-9]+")
    value = int(digits)
    return -value if sign else value


@generate
def number_parser():
    res = yield (
         hexadecimal_number_parser ^ binary_number_parser ^ octal_number_parser ^ decimal_number_parser
    )
    return Number(res)

    # vx = lambda br: string(pref) >> string(br) >> many(none_of(br)) << string(br)
    # res = yield vx('"') ^ vx("'")


# def string_parser(pref: str = ""):
#     @generate
#     def parser():
#         quote = yield string(pref) >> one_of("'\"")
#         chars = yield many(none_of(quote)) << string(quote)
#         return "".join(chars)

#     return parser


# @generate
# def xstring_parser():
#     res = yield string_parser("x")
#     return XString(res)

@generate
def xstring_parser():
    quote = yield string("x") >> one_of("'\"")
    chars = yield regex(r"[0-9A-Fa-f]+") << string(quote)
    return XString("".join(chars))

# @generate
# def cstring_parser():
#     res = yield string_parser("c")
#     return CString(res)

@generate
def cstring_parser():
    quote = yield string("c") >> one_of("'\"")
    @generate
    def go():
        chars = yield (many(none_of(quote+";")) >> string(";") >> spaces() >> string(quote) >> many(any())) ^ (spaces() >> string(quote) >> many(any()))
        # chars = yield (many(none_of(quote)) >> string(";") >> spaces() >> string(quote) >> many(any()))
        return chars
    chars = yield many(any())
    chars = "".join(chars)[::-1]
    try:
        chars = "".join(go.parse(chars)[::-1])
    except ParseError:
        yield fail_with("Not in quotes")
    # print(f"({chars})")
    return CString(chars)

@generate
def register_parser():
    pref = one_of("Rr") >> decimal_number_parser
    x = yield exclude(pref, pref >> identifier_parser)
    if 0 <= x < 16:
        return Register(x)
    else:
        yield fail_with(f"Invalid register number: {x}. Must be between 0 and 15")


@generate
def operand_parser():
    res = (
        yield register_parser
        ^ number_parser
        ^ xstring_parser
        ^ cstring_parser
        ^ relative_id_parser
        ^ direct_id_parser
    )
    return res


@generate
def command_parser():
    yield spaces()
    mnemonic = yield identifier_parser << spaces()
    operands = yield sepBy(operand_parser, string(",") << spaces())
    yield lookahead(tail_parser)
    return ParsedCommand(mnemonic, operands)


@generate
def label_parser():
    lbl = yield identifier_parser << string(":")
    return lbl


@generate
def comment_parser():
    yield string(";") >> many(none_of("\n"))


@generate
def tail_parser():
    yield spaces() >> (eof() | comment_parser)


@generate
def line_parser():

    @generate
    def go():
        yield spaces()
        lbl = yield optional(label_parser) << spaces()
        cmd = yield command_parser << spaces()
        yield tail_parser
        return ParsedLine(lbl, cmd)

    res = yield tail_parser ^ go
    return res


def parse_assembly(source: str) -> Tuple[List[ParsedLine], List[str]]:
    lines = source.split("\n")
    errors = []
    results = []

    for i, line in enumerate(lines, 1):
        try:
            result = line_parser.parse(line)
            if result is not None:
                results.append(result)
        except ParseError as err:
            errors.append(f"Line {i}: '{line.strip()} --- {err}'")

    return (results, errors)
