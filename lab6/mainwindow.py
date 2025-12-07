# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from parser import *
from first_pass import first_pass_simple_dict
from second_pass import second_pass

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow
from collections import deque


def table_to_dict(table_widget) -> Tuple[List[str], Dict[str, Tuple[int, int]]]:
    result_dict = {}
    errs = []

    registers = [f"R{i:x}" for i in range(1, 16)]
    directives = ["START", "END", "WORD", "BYTE"]
    codops = set()

    for row in range(table_widget.rowCount()):
        lineErr = lambda msg: errs.append(
            f"Строка {row + 1} (таблица кодов операций): {msg}"
        )
        key_item = table_widget.item(row, 0)
        if key_item is None:
            continue

        key = key_item.text().strip()
        if not key:
            continue

        value1_item = table_widget.item(row, 1)
        value2_item = table_widget.item(row, 2)

        try:
            value1 = (
                number_parser.parse(value1_item.text()).value
                if value1_item and value1_item.text().strip()
                else 0
            )
            value2 = (
                number_parser.parse(value2_item.text()).value
                if value2_item and value2_item.text().strip()
                else 0
            )
        except ValueError:
            value1 = 0
            value2 = 0

        if key in result_dict:
            lineErr("Дублирующая мнемоника команды")
        if key in registers:
            lineErr("Мнемоника команды не должна совпадать с регистрами")
        if key in directives:
            lineErr("Мнемоника команды не должна совпадать с директивами")
        if not (0 <= ((value1 << 2) | 1) <= 0xFF):
            lineErr("Код операции не помещается в 6 бит")
        if not (value2 in [1, 2, 3, 4]):
            lineErr("Размер команды может быть только 1Б, 2Б, 3Б, 4Б")

        result_dict[key] = (value1, value2)
        if value1 not in codops:
            codops.add(value1)
        else:
            lineErr("Повтор кода операции")

    return errs, result_dict

def fill_symbol_table_sorted_by_address(table_widget: QTableWidget, symbol_table):
    table_widget.clear()
    table_widget.setRowCount(0)

    table_widget.setColumnCount(4)
    table_widget.setHorizontalHeaderLabels(["Метка", "Адрес", "Секция", "Тип"])

    print(symbol_table)
    table_widget.setRowCount(sum(len(symbol_table[i]) for i in symbol_table))
    row = 0
    for section_name in symbol_table:
        section = list(symbol_table[section_name].items())
        section.sort(key=lambda x: x[1]["addr"] if x[1]["addr"] is not None else -1)
        for label, record in section:
            label_item = QTableWidgetItem(label)
            address_item = QTableWidgetItem(
                f"0x{record["addr"]:06x}" if record["addr"] is not None else "None"
            )
            section_item = QTableWidgetItem(section_name)
            type_item = QTableWidgetItem(record["type"])
            table_widget.setItem(row, 0, label_item)
            table_widget.setItem(row, 1, address_item)
            table_widget.setItem(row, 2, section_item)
            table_widget.setItem(row, 3, type_item)
            row += 1

    table_widget.resizeColumnsToContents()
    table_widget.setAlternatingRowColors(True)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.codeTable.setHorizontalHeaderLabels(
            ["Мнемоника", "Код операции", "Размер"]
        )
        self.ui.firstPass.clicked.connect(self.first_pass)
        self.ui.tracePass.clicked.connect(self.trace_pass)
        self.ui.clearFirst.clicked.connect(lambda: self.ui.firstPassErr.clear())

        self.ui.srcCode.textChanged.connect(self.on_source_code_changed)

        self.ui.chooseAdrMethod.activated.connect(self.on_source_code_changed)

        self.ui.codeTable.cellChanged.connect(self.on_source_code_changed)
        self.ui.codeTable.cellClicked.connect(self.on_source_code_changed)

        self.init_structures()
        self.update_ui_state()

    def init_structures(self):
        self.symbol_table = None
        self.op_table = None

    def on_source_code_changed(self):
        self.reset_compilation_state()

    def print_results(self, res_table, symbol_table, errs):
        self.ui.binaryCode.clear()
        if res_table:
            self.ui.binaryCode.addItems(res_table)

        self.ui.symbolicNameTable.clear()
        self.ui.symbolicNameTable.setRowCount(0)
        if symbol_table:
            fill_symbol_table_sorted_by_address(self.ui.symbolicNameTable, symbol_table)

        self.ui.firstPassErr.clear()
        self.ui.firstPassErr.addItems(errs)
    
    def trace_pass(self):
        # res_table, symbol_table, errs = self.first_pass_gen.next()
        try:
            self.print_results(*next(self.first_pass_gen))
        except StopIteration:
            pass
        except TypeError as err:
            raise err
    
    def reset_compilation_state(self):
        self.first_pass_gen = None
        self.ui.binaryCode.clear()
        self.ui.firstPassErr.clear()
        self.ui.symbolicNameTable.clear()
        self.ui.symbolicNameTable.setRowCount(0)
        
        text_src = self.ui.srcCode.toPlainText()
        parsed_lines, parse_errors = parse_assembly(text_src)
        op_table_check_errs, op_table = table_to_dict(self.ui.codeTable)

        self.ui.firstPassErr.addItems(parse_errors)
        self.ui.firstPassErr.addItems(op_table_check_errs)
        if op_table_check_errs:
            self.update_ui_state()
            return

        method = self.ui.chooseAdrMethod.currentIndex()
        self.first_pass_gen = first_pass_simple_dict(parsed_lines, op_table, method)

        self.update_ui_state()

    def first_pass(self):
        try:
            self.print_results(*deque(self.first_pass_gen, maxlen=1)[-1])
        except IndexError:
            pass
        except TypeError:
            pass

    
    def update_ui_state(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

