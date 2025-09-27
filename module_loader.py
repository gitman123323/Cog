import os
from Parser import Parser
from Lexer import Lexer

class ModuleLoader:
    def __init__(self):
        # file_path -> symbol_table dict
        self.module_symbols: dict[str, dict[str, str]] = {}

    def load_module(self, file_path: str) -> dict[str, str]:
        """ Parse a file and return its symbol table """
        if file_path in self.module_symbols:
            return self.module_symbols[file_path]  # already loaded

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Module '{file_path}' not found")

        with open(file_path, "r") as f:
            code = f.read()

        lexer = Lexer(code)
        parser = Parser(lexer)
        parser.parse_program()  # parse fully

        self.module_symbols[file_path] = parser.symbol_table
        return parser.symbol_table

    def merge_imports(self, current_symbols: dict[str, str], imports: list[str]):
        """ Merge symbols from imported modules into the current symbol table """
        for file_path in imports:
            imported_symbols = self.load_module(file_path)
            # overwrite conflicts? here we just merge
            current_symbols.update(imported_symbols)
