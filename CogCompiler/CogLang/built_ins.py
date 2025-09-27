from llvmlite import ir

def register_builtins(compiler):
    # ---------------- COG PRINT ----------------
    # Declare external printf C function
    printf_ty = ir.FunctionType(
        ir.IntType(32),
        [ir.IntType(8).as_pointer()],
        var_arg=True
    )
    cog_printIn = ir.Function(compiler.module, printf_ty, name="cog_printIn")

    # Handler for our compiler to call it in IR
    def builtin_cog_print(args):
        """
        Args: list of (ir_value, ir_type)
        """
        call_args = []
        for val, typ in args:
            if isinstance(typ, ir.IntType):
                fmt = compiler.make_string("%d")
            elif isinstance(typ, ir.FloatType):
                fmt = compiler.make_string("%f")
            else:
                fmt = compiler.make_string("%s")
                val = compiler.builder.bitcast(val, ir.IntType(8).as_pointer())
            call_args.extend([fmt, val])

        # This returns an actual LLVM IR call instruction
        return compiler.builder.call(cog_printIn, call_args)

    # Store in environment as LLVM-callable function
    compiler.env.define("cog_printIn", builtin_cog_print, ir.IntType(32))
