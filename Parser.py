from Lexer import Lexer
from Token import Token, TokenType
from typing import Callable
from enum import Enum, auto

from AST import Statement, Expression, Program
from AST import ExpressionStatement, LetStatement, FunctionStatement, ReturnStatement, BlockStatement, AssignStatement, IfStatement
from AST import WhileStatement, BreakStatement, ContinueStatement, ForStatement, ImportStatement
from AST import InfixExpression, CallExpression, PrefixExpression, PostfixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral, StringLiteral
from AST import FunctionParameter

import sys, json

from Token import TYPE_KEYWORDS, KEYWORDS

# Precedence Types
class PrecedenceType(Enum):
    P_LOWEST = 0
    P_EQUALS = auto()
    P_LESSGREATER = auto()
    P_SUM = auto()
    P_PRODUCT = auto()
    P_EXPONENT = auto()
    P_PREFIX = auto()
    P_CALL = auto()
    P_INDEX = auto()

# Precedence Mapping
PRECEDENCES: dict[TokenType, int] = {
    TokenType.PLUS: PrecedenceType.P_SUM,
    TokenType.MINUS: PrecedenceType.P_SUM,
    TokenType.SLASH: PrecedenceType.P_PRODUCT,
    TokenType.ASTERISK: PrecedenceType.P_PRODUCT,
    TokenType.MODULUS: PrecedenceType.P_PRODUCT,
    TokenType.POW: PrecedenceType.P_EXPONENT,
    
    # Episode 8 NEW
    TokenType.EQ_EQ: PrecedenceType.P_EQUALS,
    TokenType.NOT_EQ: PrecedenceType.P_EQUALS,
    TokenType.LT: PrecedenceType.P_LESSGREATER,
    TokenType.GT: PrecedenceType.P_LESSGREATER,
    TokenType.LT_EQ: PrecedenceType.P_LESSGREATER,
    TokenType.GT_EQ: PrecedenceType.P_LESSGREATER,

    # Episode 9 NEW
    TokenType.LPAREN: PrecedenceType.P_CALL,

    TokenType.PLUS_PLUS: PrecedenceType.P_INDEX,
    TokenType.MINUS_MINUS: PrecedenceType.P_INDEX,
}

class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer: Lexer = lexer
        
        # Just a list of errors caught during parsing
        self.errors: list[str] = []

        # Symbol table: variable_name -> type
        self.symbol_table: dict[str, str] = {}

        self.previous_token: Token = None    # <-- NEW
        self.current_token: Token = None
        self.peek_token: Token = None

        self.prefix_parse_fns: dict[TokenType, Callable] = {
            TokenType.IDENT: self.__parse_identifier,
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,

            # Episode 8 NEW
            TokenType.IF: self.__parse_if_statement,
            TokenType.TRUE: self.__parse_boolean,
            TokenType.FALSE: self.__parse_boolean,

            # Episode 11 NEW
            TokenType.STRING: self.__parse_string_literal,

            TokenType.MINUS: self.__parse_prefix_expression,
            TokenType.BANG: self.__parse_prefix_expression,
        }
        self.infix_parse_fns: dict[TokenType, Callable] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.POW: self.__parse_infix_expression,
            TokenType.MODULUS: self.__parse_infix_expression,

            # Episode 8 NEW
            TokenType.EQ_EQ: self.__parse_infix_expression,
            TokenType.NOT_EQ: self.__parse_infix_expression,
            TokenType.LT: self.__parse_infix_expression,
            TokenType.GT: self.__parse_infix_expression,
            TokenType.LT_EQ: self.__parse_infix_expression,
            TokenType.GT_EQ: self.__parse_infix_expression,

            # Episode 9 NEW
            TokenType.LPAREN: self.__parse_call_expression,

            TokenType.PLUS_PLUS: self.__parse_postfix_expression,
            TokenType.MINUS_MINUS: self.__parse_postfix_expression,
        }

        # Populate the current_token and peek_token
        self.__next_token()
        self.__next_token()

    def dump_symbol_table(self, filename: str = "symbol_table.json"):
        """ Dumps the current symbol table to a JSON file for inspection. """
        with open(filename, "w") as f:
            json.dump(self.symbol_table, f, indent=4)
        print(f"Symbol table dumped to {filename}")

    # region Parser Helpers
    def __next_token(self) -> None:
        """ Advances the lexer to retrieve the next token """
        self.previous_token = self.current_token
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def __current_token_is(self, tt: TokenType) -> bool:
        return self.current_token.type == tt

    def __peek_token_is(self, tt: TokenType) -> bool:
        """ Peeks one token ahead and checks the type """
        return self.peek_token.type == tt
    
    def __peek_token_is_assignment(self) -> bool:
        assignment_operators: list[TokenType] = [
            TokenType.EQ,
            TokenType.PLUS_EQ,
            TokenType.MINUS_EQ,
            TokenType.MUL_EQ,
            TokenType.DIV_EQ
        ]
        return self.peek_token.type in assignment_operators
    
    def __expect_peek(self, tt: TokenType) -> bool:
        if self.__peek_token_is(tt):
            self.__next_token()
            return True
        else:
            self.__peek_error(tt)
            return False
    
    def __current_precedence(self) -> PrecedenceType:
        prec: int | None = PRECEDENCES.get(self.current_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST
        return prec
    
    def __peek_precedence(self) -> PrecedenceType:
        prec: int | None = PRECEDENCES.get(self.peek_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST
        return prec
    
    def __peek_error(self, tt: TokenType) -> None:
        #expected = TOKEN_DISPLAY.get(tt, tt.name)

        # Position the squiggle right *after* current_token
        line = self.current_token.line_no
        col = self.current_token.col_no + len(str(self.current_token.literal))

        print(
            f"{line}:{col}: [COG] Error: '{tt.name}' Expected",
            file=sys.stderr
        )

    def __no_prefix_parse_fn_error(self, tt: TokenType):
        self.errors.append(f"No Prefix Parse Function for {tt} found")
    # endregion
    
    def parse_program(self) -> None:
        """ Main execution entry to the Parser """
        program: Program = Program()

        while self.current_token.type != TokenType.EOF:
            stmt: Statement = self.__parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            
            self.__next_token()

        return program

    # region Statement Methods

    def __expect_keyword(self, tt: TokenType) -> bool:
        """
        Like __expect_peek but if the peek is an IDENT, produce
        "Unknown or misspelled keyword 'xxx' (expected ...)" and recover.
        Use this only where the grammar requires a keyword (e.g. for-loop initializer).
        """
        if self.__peek_token_is(tt):
            self.__next_token()
            return True

        # nicer message for IDENTs (probable typo)
        if self.peek_token.type == TokenType.IDENT:
            line = self.peek_token.line_no
            col  = self.peek_token.col_no
            print(
                f"{line}:{col}: [COG] Error: Unknown or misspelled keyword '{self.peek_token.literal}' (expected '{tt.name.lower()}')",
                file=sys.stderr
            )
            #self.errors.append(f"Unknown or misspelled keyword '{self.peek_token.literal}'")
            # consume the ident to try to recover and continue parsing
            self.__next_token()
            return False

        # fallback to normal peek error
        self.__peek_error(tt)
        return False

    def __check_double_semicolon(self) -> None:
        if self.__current_token_is(TokenType.SEMICOLON) and self.__peek_token_is(TokenType.SEMICOLON):
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(f"{line}:{col}: [COG] Syntax_Error: Unexpected double semicolon ';;'", file=sys.stderr)
            # Skip the extra semicolon to prevent repeated errors
            
            self.__next_token()


    def __parse_statement(self) -> Statement:
        # Disallow bare type declarations outside 'let'

        self.__check_double_semicolon()
        # In your __parse_statement or a dedicated check function
        if self.current_token.type == TokenType.TYPE and self.__peek_token_is(TokenType.IDENT):
            if self.previous_token is None or self.previous_token.type != TokenType.LET:
                line = self.current_token.line_no
                col  = self.current_token.col_no
                print(
                    f"{line}:{col}: [COG] Invalid_Assign_Error: Assigning type directly like '{self.current_token.literal} {self.peek_token.literal} = ...' "
                    f"instead of 'let {self.peek_token.literal}: {self.current_token.literal} = ...'. "
                    f"This is not allowed and not recommended(your program may throw an exception).",
                    file=sys.stderr
                )
                return
                # Optionally: continue parsing as if 'let' were there

        # Trigger only if colon appears without LET or IDENT before
        if (
            self.current_token.type == TokenType.COLON
            and self.__peek_token_is(TokenType.TYPE)
            and (self.previous_token is None or self.previous_token.type not in [TokenType.LET, TokenType.IDENT])
        ):
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(
                f"{line}:{col}: [COG] Invalid_Declr_Error: Type annotation without a variable name is not allowed. "
                f"Found '{self.current_token.literal}{self.peek_token.literal}'",
                file=sys.stderr
            )
            # Skip to semicolon or EOF to recover
            #while not self.__current_token_is(TokenType.SEMICOLON) and not self.__current_token_is(TokenType.EOF):
                #self.__next_token()
            #if self.__current_token_is(TokenType.SEMICOLON):
                #self.__next_token()
            #return None
        
        # --- EQ checks: assignment without a variable ---
        
        if (
            self.current_token.type == TokenType.EQ
            and (self.previous_token is None or self.previous_token.type not in [TokenType.LET, TokenType.IDENT])
        ):
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(
                f"{line}:{col}: [COG] Invalid_Assign_Error: Unexpected '='. You may have forgotten 'let', used ':type =' incorrectly, or typed '=' without a variable name.",
                file=sys.stderr
            )
            return None

        if self.current_token.type == TokenType.IDENT and self.__peek_token_is(TokenType.COLON):
            # Something like "b: bool = true;" → illegal
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(f"{line}:{col}: [COG] Invalid_Declr_Error: Type annotations are only allowed in 'let' declarations", file=sys.stderr)
            self.__peek_error(TokenType.LET)
            return None
        
        if self.current_token.type == TokenType.IDENT and self.__peek_token_is(TokenType.TYPE):
            # Invalid_Declr_Error
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(f"{line}:{col}: [COG] Invalid_Declr_Error: Standalone declaration '{self.current_token.literal} {self.peek_token.literal}' is not allowed.", file=sys.stderr)
            #self.__peek_error(TokenType.TYPE)
            return None
        
        #if self.__peek_token_is(TokenType.IDENT) and self.current_token.type == TokenType.IDENT:
            #self.__peek_error(TokenType.LET)
            #return None
            
        match self.current_token.type:
            case TokenType.LET:
                return self.__parse_let_statement()
            case TokenType.FN:
                return self.__parse_function_statement()
            case TokenType.RETURN:
                return self.__parse_return_statement()
            case TokenType.WHILE:
                return self.__parse_while_statement()
            case TokenType.BREAK:
                return self.__parse_break_statement()
            case TokenType.CONTINUE:
                return self.__parse_continue_statement()
            case TokenType.FOR:
                return self.__parse_for_statement()
            case TokenType.IMPORT:
                return self.__parse_import_statement()
            case _:
                return self.__parse_expression_statement()
    
    # --- HELPER: ILLEGAL OPERATOR / COMPARISON CHECK ---
    def __check_illegal_operator_usage(self, expr: Expression) -> None:
        """
        Checks for illegal use of operators and comparisons:
        1. Bare math operators (+, -, *, /, %) without assignment
        2. Comparisons (==, !=, <, >, <=, >=) outside conditional contexts
        3. Incomplete assignments (+=, -=, *=, /=) without right-hand value
        4. Standalone identifiers used without assignment or operation
        """

        # Infix expressions
        if isinstance(expr, InfixExpression):
            left_node = expr.left_node
            operator = expr.operator

            # Comparisons only allowed in conditionals
            if operator in ("==", "!=", "<", ">", "<=", ">="):
                if self.previous_token is None or self.previous_token.type not in [TokenType.IF, TokenType.WHILE, TokenType.FOR]:
                    line, col = self.current_token.line_no, self.current_token.col_no
                    print(
                        f"{line}:{col}: [COG] Syntax_Error: Comparison '{left_node.value} {operator} ...' used outside conditional",
                        file=sys.stderr
                    )
            
            # Bare math operators without assignment
            if operator in ("+", "-", "*", "/", "%") and not self.__peek_token_is_assignment():
                if isinstance(left_node, IdentifierLiteral):
                    var_name = left_node.value
                    line, col = self.current_token.line_no, self.current_token.col_no
                    print(
                        f"{line}:{col}: [COG] Syntax_Error: Illegal use of '{operator}' on variable '{var_name}' without assignment (use '{var_name} {operator}= value')",
                        file=sys.stderr
                    )
    
    def __parse_expression_statement(self) -> ExpressionStatement:
        expr = self.__parse_expression(PrecedenceType.P_LOWEST)
        
        # --- BARE IDENTIFIER CHECK ---
        if isinstance(expr, IdentifierLiteral):
            var_name = expr.value
            if var_name not in self.symbol_table:
                line, col = self.current_token.line_no, self.current_token.col_no
                print(f"{line}:{col}: [COG] Name_Error: '{var_name}' is not declared", file=sys.stderr)
                return None
            # If identifier is alone without assignment or operation → illegal
            if not self.__peek_token_is_assignment() and not self.__peek_token_is(TokenType.SEMICOLON) and not self.__peek_token_is(TokenType.LPAREN):
                line, col = self.current_token.line_no, self.current_token.col_no
                print(f"{line}:{col}: [COG] Syntax_Error: Bare variable '{var_name}' used without operation or assignment", file=sys.stderr)
                return None

        # --- ENFORCE FUNCTION CALLS ---
        
        if isinstance(expr, IdentifierLiteral):
            var_name = expr.value
            # Check if this identifier is a function in the symbol table
            if self.symbol_table.get(var_name) == "function":
                # If the next token is NOT a LPAREN → error
                if not self.__peek_token_is(TokenType.LPAREN):
                    line = self.current_token.line_no
                    col = self.current_token.col_no + len(var_name)
                    print(
                        f"{line}:{col}: [COG] Function_Call_Error: Function '{var_name}' must be called with parentheses '()'",
                        file=sys.stderr,
                    )

        # Check if this is an assignment: IDENT = something
        if isinstance(expr, IdentifierLiteral) and self.__peek_token_is(TokenType.EQ):
            self.__next_token()  # skip '='
            self.__next_token()  # skip to the right-hand side
            right_expr = self.__parse_expression(PrecedenceType.P_LOWEST)
            var_name = expr.value

            # --- Require semicolon after assignment ---
            if not self.__peek_token_is(TokenType.SEMICOLON):
                self.__peek_error(TokenType.SEMICOLON)
                return None
            else:
                self.__next_token()  # consume semicolon

            # Does the variable exist?
            if var_name not in self.symbol_table:
                line = self.current_token.line_no
                col = self.current_token.col_no
                print(f"{line}:{col}: [COG] Name_Error: '{var_name}' is not declared", file=sys.stderr)
                return None

            # Check mutability
            var_info = self.symbol_table[var_name]
            if not var_info.get("mutable", False):
                line = self.current_token.line_no
                col = self.current_token.col_no
                print(f"{line}:{col}: [COG] Mutability_Error: Cannot assign to immutable variable '{var_name}'", file=sys.stderr)
                return None

            # Optional: type check
            assigned_type = self.__infer_expression_type(right_expr)
            if var_info["type"] != assigned_type:
                line = self.current_token.line_no
                col = self.current_token.col_no
                print(f"{line}:{col}: [COG] Type_Error: Cannot assign '{assigned_type}' to '{var_name}' of type '{var_info['type']}'", file=sys.stderr)
                return None

        
        #Requires a Semicolon to end the function call.
        # ✅ If the expression is a call and no semicolon follows → error
        if isinstance(expr, CallExpression):
            if not self.__peek_token_is(TokenType.SEMICOLON):
                # Show an error right after call.
                self.__peek_error(TokenType.SEMICOLON)
                # Don’t consume; just let parser continue gracefully
            else:
                self.__next_token()  # consume the semicolon
        else:
            # Normal expressions can optionally end with a semicolon
            if self.__peek_token_is(TokenType.SEMICOLON):
                self.__next_token()


        if self.__peek_token_is(TokenType.SEMICOLON):
            self.__next_token()

        self.__check_illegal_operator_usage(expr)

        return ExpressionStatement(expr=expr)

    
    def __infer_expression_type(self, expr: Expression) -> str:
        if isinstance(expr, IntegerLiteral):
            return "int"
        elif isinstance(expr, FloatLiteral):
            return "float"
        elif isinstance(expr, BooleanLiteral):
            return "bool"
        elif isinstance(expr, StringLiteral):
            return "str"
        elif isinstance(expr, IdentifierLiteral):
            # Return the declared type from the symbol table
            return self.symbol_table.get(expr.value, "unknown")
        # Extend for more complex expressions if needed
        return "unknown"


    def __parse_let_statement(self) -> LetStatement:
        stmt: LetStatement = LetStatement()
    
        # let a: int = 10;
        
        # Check for optional 'mut' keyword
        if self.__peek_token_is(TokenType.MUT):
            if not self.__expect_peek(TokenType.MUT):
                return None            # shouldn't happen, but keeps flow consistent
            stmt.is_mutable = True
        # If peek is NOT MUT, we do NOTHING—no advance, no error.


        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        stmt.name = IdentifierLiteral(value=self.current_token.literal)

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        if not self.__expect_peek(TokenType.TYPE):
            return None
        
        stmt.value_type = self.current_token.literal

        # Register variable in symbol table
        # In __parse_let_statement, after parsing name and type:
        self.symbol_table[stmt.name.value] = {
            "type": stmt.value_type,
            "mutable": getattr(stmt, "is_mutable", False)
        }


        # ❌ Check for incomplete assignment
        if not self.__peek_token_is(TokenType.EQ):
            line = self.current_token.line_no
            col = self.current_token.col_no
            print(
                f"{line}:{col}: [COG] Invalid_Let_Error: Incomplete let statement. "
                f"Found 'let {stmt.name.value}: {stmt.value_type}' without a value assignment. "
                f"Did you forget '= <value>'?",
                file=sys.stderr
            )
            return None

        # ✅ Check if type is valid
        if stmt.value_type not in TYPE_KEYWORDS:
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(f"{line}:{col}: [COG] Type_Error: Unknown type '{stmt.value_type}'", file=sys.stderr)
            # self.errors.append(f"Unknown type '{stmt.value_type}'")  # optional for recovery
            #return None  # optionally stop parsing this statement
        elif stmt.value_type == 'void':
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(f"{line}:{col}: [COG] Type_Error: Cannot use type '{stmt.value_type}'", file=sys.stderr)
            return None

        if not self.__expect_peek(TokenType.EQ):
            return None
        
        self.__next_token()
        stmt.value = self.__parse_expression(PrecedenceType.P_LOWEST)

        # ✅ NEW: Type-mismatch check
        inferred_type = self.__infer_expression_type(stmt.value)
        declared_type = stmt.value_type

        if inferred_type != "unknown" and inferred_type != declared_type:
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(
                f"{line}:{col}: [COG] Type_Error: Cannot assign '{inferred_type}' "
                f"to variable '{stmt.name.value}' of type '{declared_type}'",
                file=sys.stderr
            )

        # ✅ Require a semicolon
        if not self.__expect_peek(TokenType.SEMICOLON):
            # Instead of letting the parser drift → trigger proper semicolon error
            return None

        return stmt
    
    def __parse_function_statement(self) -> FunctionStatement:
        stmt: FunctionStatement = FunctionStatement()

        if not self.__expect_peek(TokenType.IDENT):
            return None
        stmt.name = IdentifierLiteral(value=self.current_token.literal)

        # MARK IN SYMBOL TABLE
        self.symbol_table[stmt.name.value] = "function"
        # MARK INTERNAL PRINT FUNCTION IN SYMBOL TABLE
        self.symbol_table['CogPrint'] = "function"

        if not self.__expect_peek(TokenType.LPAREN):
            return None
        stmt.parameters = self.__parse_function_parameters()

        if not self.__expect_peek(TokenType.ARROW):
            return None

        self.__next_token()   # <-- now at the type token
        stmt.return_type = self.current_token.literal

        # ✅ NEW: validate return type
        if stmt.return_type not in TYPE_KEYWORDS:
            line = self.current_token.line_no
            col  = self.current_token.col_no
            print(
                f"{line}:{col}: [COG] Type_Error: Unknown return type '{stmt.return_type}'",
                file=sys.stderr
            )
            # you can also append to self.errors if you want parser to keep going
            #self.errors.append(f"Unknown return type '{stmt.return_type}'")
            # optionally bail out early:
            # return None

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        stmt.body = self.__parse_block_statement()

        return stmt
    
    def __parse_function_parameters(self) -> list[FunctionParameter]:
        params: list[FunctionParameter] = []

        if self.__peek_token_is(TokenType.RPAREN):
            self.__next_token()
            return params
        
        self.__next_token()

        first_param: FunctionParameter = FunctionParameter(name=self.current_token.literal)

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        self.__next_token()

        first_param.value_type = self.current_token.literal
        params.append(first_param)

        while self.__peek_token_is(TokenType.COMMA):
            self.__next_token()
            self.__next_token()

            param: FunctionParameter = FunctionParameter(name=self.current_token.literal)

            if not self.__expect_peek(TokenType.COLON):
                return None
            
            self.__next_token()

            param.value_type = self.current_token.literal

            params.append(param)

        if not self.__expect_peek(TokenType.RPAREN):
            return None

        return params

    def __parse_block_statement(self) -> BlockStatement:
        block_stmt: BlockStatement = BlockStatement()

        self.__next_token()

        while not self.__current_token_is(TokenType.RBRACE) and not self.__current_token_is(TokenType.EOF):
            stmt: Statement = self.__parse_statement()
            if stmt is not None:
                block_stmt.statements.append(stmt)

            self.__next_token()

        return block_stmt

    def __parse_return_statement(self) -> ReturnStatement:
        stmt: ReturnStatement = ReturnStatement()

        self.__next_token()

        stmt.return_value = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None
        
        return stmt
    
    def __parse_assignment_statement(self) -> AssignStatement:
        stmt: AssignStatement = AssignStatement()

        stmt.ident = IdentifierLiteral(value=self.current_token.literal)

        self.__next_token() # skips the 'IDENT'

        stmt.operator = self.current_token.literal
        self.__next_token() # skips the op

        stmt.right_value = self.__parse_expression(PrecedenceType.P_LOWEST)

        # ✅ Require a semicolon here
        if not self.__expect_peek(TokenType.SEMICOLON):
            # Don't advance if it's missing; emit an error
            return None

        return stmt
    
    def __parse_if_statement(self) -> IfStatement:
        condition: Expression = None
        consequence: BlockStatement = None
        alternative: BlockStatement = None

        self.__next_token()

        condition = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.LBRACE):
            return None

        consequence = self.__parse_block_statement()

        if self.__peek_token_is(TokenType.ELSE):
            self.__next_token()

            if not self.__expect_peek(TokenType.LBRACE):
                return None
            
            alternative = self.__parse_block_statement()

        return IfStatement(condition=condition, consequence=consequence, alternative=alternative)
    
    def __parse_while_statement(self) -> WhileStatement:
        condition: Expression = None
        body: BlockStatement = None

        self.__next_token()  # Skip WHILE

        condition = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        body = self.__parse_block_statement()

        return WhileStatement(condition=condition, body=body)
    
    def __parse_break_statement(self) -> BreakStatement:
        
        # Advance *once* to look at the token after 'break'
        if not self.__expect_peek(TokenType.SEMICOLON):
        # Instead of letting the parser drift → trigger proper semicolon error
            return None

        #self.__next_token()
        return BreakStatement()
    
    def __parse_continue_statement(self) -> ContinueStatement:
        #self.__next_token()

        if not self.__expect_peek(TokenType.SEMICOLON):
        # Instead of letting the parser drift → trigger proper semicolon error
            return None

        return ContinueStatement()
    
    def __parse_for_statement(self) -> ForStatement:
        """ for (let i: int = 0; i < 10; i = i + 1) { } """
        stmt: ForStatement = ForStatement()

        if not self.__expect_peek(TokenType.LPAREN):
            return None
        
        if not self.__expect_keyword(TokenType.LET):
            return None

        stmt.var_declaration = self.__parse_let_statement()

        self.__next_token()  # Skip ;

        stmt.condition = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None
        
        self.__next_token() # Skip ;

        stmt.action = self.__parse_expression(PrecedenceType.P_LOWEST)
        
        self.__next_token()

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        stmt.body = self.__parse_block_statement()

        return stmt
    
    def __parse_import_statement(self) -> ImportStatement:
        if not self.__expect_peek(TokenType.STRING):
            return None

        stmt = ImportStatement(file_path=self.current_token.literal)

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None

        return stmt
    # endregion

    # region Expression Methods
    def __parse_expression(self, precedence: PrecedenceType) -> Expression:
        prefix_fn: Callable | None = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            #self.__no_prefix_parse_fn_error(self.current_token.type)
            return None
        
        left_expr: Expression = prefix_fn()
        while not self.__peek_token_is(TokenType.SEMICOLON) and precedence.value < self.__peek_precedence().value:
            infix_fn: Callable | None = self.infix_parse_fns.get(self.peek_token.type)
            if infix_fn is None:
                return left_expr
            
            self.__next_token()

            left_expr = infix_fn(left_expr)
        
        return left_expr
    
    def __parse_infix_expression(self, left_node: Expression) -> Expression:
        operator = self.current_token.literal
        infix_expr = InfixExpression(left_node=left_node, operator=operator)

        precedence = self.__current_precedence()
        self.__next_token()
        infix_expr.right_node = self.__parse_expression(precedence)

        # --- Check illegal standalone + or - usage ---
        # Already handled in the __check_illegal_operator_usage method.

        return infix_expr

    
    def __parse_grouped_expression(self) -> Expression:
        self.__next_token()

        expr: Expression = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.RPAREN):
            return None
        
        return expr
    
    def __parse_call_expression(self, function: Expression) -> CallExpression:
        expr: CallExpression = CallExpression(function=function)
        expr.arguments = self.__parse_expression_list(TokenType.RPAREN)
        
        return expr
    
    def __parse_expression_list(self, end: TokenType) -> list[Expression]:
        e_list: list[Expression] = []

        if self.__peek_token_is(end):
            self.__next_token()
            return e_list
        
        self.__next_token()
        
        e_list.append(self.__parse_expression(PrecedenceType.P_LOWEST))

        while self.__peek_token_is(TokenType.COMMA):
            self.__next_token()
            self.__next_token()

            e_list.append(self.__parse_expression(PrecedenceType.P_LOWEST))

        if not self.__expect_peek(end):
            return None
        
        return e_list
    
    def __parse_prefix_expression(self) -> PrefixExpression:
        prefix_expr: PrefixExpression = PrefixExpression(operator=self.current_token.literal)

        self.__next_token()

        prefix_expr.right_node = self.__parse_expression(PrecedenceType.P_PREFIX)

        return prefix_expr
    
    def __parse_postfix_expression(self, left_node: Expression) -> PostfixExpression:
        operator = self.current_token.literal
        postfix_expr = PostfixExpression(left_node=left_node, operator=operator)

        # --- Type check for ++/--
        if isinstance(left_node, IdentifierLiteral):
            var_name = left_node.value
            var_info = self.symbol_table.get(var_name)

            if var_info is None:
                line, col = self.current_token.line_no, self.current_token.col_no
                print(f"{line}:{col}: [COG] Name_Error: '{var_name}' is not declared", file=sys.stderr)
            else:
                # Only allow ++/-- on int
                if operator in ("++", "--") and var_info["type"] != "int":
                    line, col = self.current_token.line_no, self.current_token.col_no
                    print(f"{line}:{col}: [COG] Type_Error: Cannot use '{operator}' on type '{var_info['type']}'", file=sys.stderr)

        return postfix_expr

    # endregion

    # region Prefix Methods
    def __parse_identifier(self) -> IdentifierLiteral:
        ident_name = self.current_token.literal

        # Only check if it's an undefined variable, skip functions
        if ident_name not in self.symbol_table:
            # Check if it looks like a function by seeing if the next token is a '('
            is_function_call = self.__peek_token_is(TokenType.LPAREN)

            if not is_function_call:
                line = self.current_token.line_no
                col = self.current_token.col_no
                print(
                    f"{line}:{col}: [COG] Name_Error: '{ident_name}' is not defined",
                    file=sys.stderr
                )

        return IdentifierLiteral(value=ident_name)


    def __parse_int_literal(self) -> IntegerLiteral:
        """ Parses an IntegerLiteral Node from the current token """
        int_lit: IntegerLiteral = IntegerLiteral()

        try:
            int_lit.value = int(self.current_token.literal)
        except:
            self.errors.append(f"Could not parse `{self.current_token.literal}` as an integer.")
            return None
        
        return int_lit
    
    def __parse_float_literal(self) -> FloatLiteral:
        """ Parses an FloatLiteral Node from the current token """
        float_lit: FloatLiteral = FloatLiteral()

        try:
            float_lit.value = float(self.current_token.literal)
        except:
            self.errors.append(f"Could not parse `{self.current_token.literal}` as an float.")
            return None
        
        return float_lit
    
    def __parse_boolean(self) -> BooleanLiteral:
        return BooleanLiteral(value=self.__current_token_is(TokenType.TRUE))
    
    def __parse_string_literal(self) -> StringLiteral:
        return StringLiteral(value=self.current_token.literal)
    # endregion