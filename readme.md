# Silent Data Corruption Detection with Program Synthesis

## Artifacts

- **Algorithm**: Program Synthesis via Rosette. Software augmentation via LLVM compiler pass and Clang.
- **Program**: `llvm2racket.py` and `sdc_analyzer.py`
- **Run-time environment**: Linux x64, macOS
- **Hardware**: Multi-core x86-64 microprocessor, or macOS ARM processor
- **Output**: Generated LLVM files, executable files, and graphs displaying analysis results
- **Experiment**: Each experiment is a run of `sdc_analyzer.py` for a C test program. Multiple C test programs can be evaluated.
- **Time required to complete experiments**:  
  - Around **one hour** is needed for the generation of a program with approximately **700 lines of code**.  
  - Program execution time depends on the original program, with an added overhead of **at most 3%** (experimentally).
- **Publicly available?**: Yes, at [GitHub Repository](https://github.com/weixinyuxx/CS357S-Final).

## Installation and Execution

1. Install **Racket**.
2. Install **Rosette**.
3. Clone the GitHub repository:  
   ```bash
   git clone https://github.com/weixinyuxx/CS357S-Final
   ```
4. Change the "file_name" variable in llvm2racket.py and sdc_analyzer.py to the name of the C test program.
5. Change the "ERR_PROB" variable in sdc_analyzer.py to the desired individual line error probability.
6. Change the "NUM_RUNS" variable in sdc_analyzer.py to the desired number of runtime iterations.
7. If testing on real server systems, set "INTRODUCE_ERRORS" in sdc_analyzer.py to False.
If testing with artificially injected errors, set "INTRODUCE_ERRORS" to True.
8. Run the following commands to generate alternative LLVM code and run the analysis program:
```
# Generate alternative LLVM code with program synthesis
python3 llvm2racket.py

# Run and analyze the SDC detection
python3 sdc_analyzer.py
```

## Project Layout
```
.
# the main program that does generate alternative instruction sequences
# calls racket2racket.py, rkt2llvm.py
# generate temporary racket file from racket_template.rkt and run it
├── llvm2racket.py
├── racket2racket.py
├── rkt2llvm.py
├── racket_template.rkt

# error injection and execution framework
├── sdc_analyzer.py

# test programs (not comprehensive)
├── test
│   ├── pow2.c
│   ├── prime.c
│   ├── print.c
│   ├── test1.c
│   └── test_all.c
└── test.ll

```