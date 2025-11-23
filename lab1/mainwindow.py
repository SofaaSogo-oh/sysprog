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

def table_to_dict(table_widget) -> Tuple[List[str], Dict[str, Tuple[int, int]]]:
    result_dict = {}
    errs = []

    registers = [f"R{i:x}" for i in range(1,16)]
    directives = ["START", "END", "WORD", "BYTE"]
    codops = set()
    
    for row in range(table_widget.rowCount()):
        lineErr = lambda msg: errs.append(f"Строка {row + 1} (таблица кодов операций): {msg}")
        key_item = table_widget.item(row, 0)
        if key_item is None:
            continue
            
        key = key_item.text().strip()
        if not key: continue
        
        value1_item = table_widget.item(row, 1)
        value2_item = table_widget.item(row, 2)
        
        try:
            value1 = number_parser.parse(value1_item.text()).value if value1_item and value1_item.text().strip() else 0
            value2 = number_parser.parse(value2_item.text()).value if value2_item and value2_item.text().strip() else 0
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
        if not (value2 in [1, 2, 4]):
            lineErr("Размер команды может быть только 1Б, 2Б, 4Б")
        
        result_dict[key] = (value1, value2)
        if value1 not in codops:
            codops.add(value1)
        else:
            lineErr("Повтор кода операции")
    
    return errs, result_dict

def parsed_lines_to_simple_table(table_widget, code_op_table, parsed_lines_with_addresses:List[ParsedLine]):
    table_widget.clear()
    table_widget.setRowCount(0)
    
    table_widget.setColumnCount(3)
    table_widget.setHorizontalHeaderLabels(["Адрес", "Код операции", "Операнды"])
    
    table_widget.setRowCount(len(parsed_lines_with_addresses))
    
    for row, (address, parsed_line) in enumerate(parsed_lines_with_addresses):
        address_item = QTableWidgetItem(f"0x{address:06X}")
        
        mnemonic = parsed_line.command.mnemonic
        code_op_item = QTableWidgetItem(mnemonic)
        if mnemonic in code_op_table:
            code_op,_ = code_op_table[parsed_line.command.mnemonic]
            code_op_item = QTableWidgetItem(f"{code_op}")
        
        
        operands = parsed_line.command.operands
        command_text = ", ".join(map(str, operands))
        command_item = QTableWidgetItem(command_text)
        
        table_widget.setItem(row, 0, address_item)
        table_widget.setItem(row, 1, code_op_item)
        table_widget.setItem(row, 2, command_item)
    
    table_widget.resizeColumnsToContents()

def fill_symbol_table_sorted_by_address(table_widget, symbol_table):
    table_widget.clear()
    table_widget.setRowCount(0)
    
    table_widget.setColumnCount(2)
    table_widget.setHorizontalHeaderLabels(["Метка", "Адрес"])
    
    symbols_list = list(symbol_table.items())
    table_widget.setRowCount(len(symbols_list))
    
    # Сортируем по адресу
    symbols_list.sort(key=lambda x: x[1])
    
    for row, (label, address) in enumerate(symbols_list):
        label_item = QTableWidgetItem(label)
        address_item = QTableWidgetItem(f"0x{address:06X}")
        
        table_widget.setItem(row, 0, label_item)
        table_widget.setItem(row, 1, address_item)
    
    table_widget.resizeColumnsToContents()
    table_widget.setAlternatingRowColors(True)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.codeTable.setHorizontalHeaderLabels(["Мнемоника","Код операции","Размер"])
        self.ui.firstPass.clicked.connect(self.first_pass)
        self.ui.secondPass.clicked.connect(self.second_pass)
        self.ui.clearFirst.clicked.connect(lambda: self.ui.firstPassErr.clear())
        self.ui.clearSecond.clicked.connect(lambda: self.ui.secondPassErr.clear())
        self.init_structures()
    
    def init_structures(self):
        self.auxaliraty_table = None
        self.symbol_table = None
        self.op_table = None
    
    def first_pass(self):
        text_src = self.ui.srcCode.toPlainText()
        parsed_lines, parse_errors = parse_assembly(text_src)
        self.ui.firstPassErr.addItems(parse_errors)
        if parse_errors:
            return

        op_table_check_errs, op_table = table_to_dict(self.ui.codeTable)
        self.ui.firstPassErr.addItems(op_table_check_errs)
        if op_table_check_errs: 
            return
        self.op_table = op_table

        auxiliraty_table, symbol_table, first_pass_errors = first_pass_simple_dict(parsed_lines, op_table)
        if auxiliraty_table:
            parsed_lines_to_simple_table(self.ui.helpTable, op_table, auxiliraty_table)
        if symbol_table:
            fill_symbol_table_sorted_by_address(self.ui.symbolicNameTable, symbol_table)
        self.ui.firstPassErr.addItems(first_pass_errors)

        self.auxaliraty_table = auxiliraty_table
        self.symbol_table = symbol_table
    
    def second_pass(self):
        if self.auxaliraty_table is None or self.symbol_table is None or self.op_table is None:
            self.ui.secondPassErr.addItem("Сделайте первый проход")
            return
        machine_code, second_pass_errors = second_pass(self.auxaliraty_table, self.symbol_table, self.op_table)
        if machine_code:
            self.ui.binaryCode.clear()
            self.ui.binaryCode.addItems(machine_code)
        self.ui.secondPassErr.addItems(second_pass_errors)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
