import sys
import os

# Add parent folder of 'server' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from Lexer import Lexer
    from Parser import Parser
except Exception as e:
    print(f"Could not import compiler modules: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) >= 2:
        # read from file
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                src = f.read()
        except Exception as e:
            print(f"1:1: Could not read file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # read source from stdin
        src = sys.stdin.read()

    lexer = Lexer(src)
    parser = Parser(lexer)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        for err in parser.errors:
            if isinstance(err, dict):
                line = err.get('line', 1)
                col = err.get('col', 1)
                msg = err.get('message', str(err))
                print(f"{line}:{col}: {msg}", file=sys.stderr)
            else:
                print(f"1:1: {err}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
