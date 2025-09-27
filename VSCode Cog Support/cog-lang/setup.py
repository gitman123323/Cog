from setuptools import setup
from Cython.Build import cythonize

setup(
    name="CogParser",
    ext_modules=cythonize(
        ["Parser.pyx", "Lexer.pyx", "Token.pyx"],  # list all files you want to compile
        compiler_directives={"language_level": "3"},  # Python 3
    ),
    zip_safe=False,
)
