
# Cog Programming Language

Cog is a custom programming language written in Python, compiling directly to LLVM via `llvmlite`. It is designed to be simple, fast, and easy to understand.  

## Requirements

- Python 3.11 or newer
- PyInstaller

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR_USERNAME/Cog.git
   cd Cog


Build the executable:

````bash
pyinstaller --onefile main.py --name cog
This will create a cog.exe (on Windows) or cog (on Linux/macOS) in the dist folder.
````

Run a Cog program:

````
./cog my_program.cog
Replace my_program.cog with the .cog file you want to execute.

````

Notes:

Cog programs are executed starting from main.py.

For full details on how to use the language, syntax, and examples, check the source code. It is designed to be self-explanatory for anyone with basic Python knowledge.

Treat it like creating a .cog file and executing it, similar to running a small C# or Python script.

Contributing:

If you want to contribute, submit a pull request. All changes will be reviewed before merging. Keep in mind that the project owner retains final approval of all contributions.
