# Jack Compiler
Toy compiler for the Jack language as specified in [Nand to Tetris](https://www.nand2tetris.org/course) course

# Components
### Initialization
- JackCompiler: top-level driver that sets up and invokes the other modules
- ClassRecord: class for maintaining list of all files being compiled
## Syntax analysis
- JackTokenizer: module that parses and tokenizes Jack files
- JackToken: class for handling individual tokens
## Code generation
- SymbolTable: module that creates a symbol table for each Jack class and subroutine
- Symbol: class for handling individual symbols
- VMWriter: output module for generating VM code
- CompilationEngine: recursive top-down compilation engine
