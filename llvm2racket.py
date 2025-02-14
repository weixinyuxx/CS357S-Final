import llvmlite.binding as llvm

# Initialize the LLVM bindings
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

def parse_llvm_ir(ir_code):
    """
    Parse the provided LLVM IR code.
    
    :param ir_code: A string containing LLVM IR code.
    :return: Parsed module
    """
    # Parse the LLVM IR assembly
    mod = llvm.parse_assembly(ir_code)
    
    # Print out the module's structure
    print("Parsed LLVM IR Module:")
    print(mod)
    return mod

llvm_file_path = 'test.ll'
with open(llvm_file_path, 'r') as llvm_file:
    llvm_ir_code = llvm_file.read()

# Parse the IR code
parsed_module = parse_llvm_ir(llvm_ir_code)
print("-----------------------")
valid_opcodes = {'add':'bvadd', 'sub':'bvsub', 'mul':'bvmul',
                     'shl':'bvshl', 'lshr':'bvlshr', 'ashr':'bvashr',
                     'and':'bvand', 'or':'bvor', 'xor':'bvxor',
                     'icmp eq':'bveq', 'icmp ne':'bveq', 'icmp slt':'<', 'icmp sle':'<=', 'icmp sgt':'>', 'icmp sge':'>='} # ne is different
inst_list = []

for function in parsed_module.functions:
    print(f"Function name: {function.name}")
    # print(f"Function arguments: {function.args}")
    #print(f"Function return type: {function.return_type}")
    # print(f"Function instructions: {function.instructions}")
    print("blocks:")
    for blk in function.blocks:
        print(blk)
        for inst in blk.instructions:
            print("Instruction:", inst)
            # print("Opcode:", inst.opcode)
            if inst.opcode in valid_opcodes:
                inst_list.append(inst)
            # operands = inst.operands
            # for oper in operands:
            #     print("Operand:", oper)
        print()
    print("Type:", function.type)
    print("args:")
    for arg in function.arguments:
        print(arg)
    print("attributes:")
    for att in function.attributes:
        print(att)

# TODO: expand to all operations
# TODO: have different racket output for i32 and i64
# TODO: insert alternative instructions after original instruction and change destination register


# TODO: add constants as (bvadd %reg1 (int 5))
# TODO: for each instruction, call an instancce of the racket script
print("Valid Instructions:")
for inst in inst_list:
    # print(inst)
    # print('Racket:')
    res_reg = str(inst).split()[0]
    operands = inst.operands
    rkt_inst = f"({valid_opcodes[inst.opcode]} {str(operands.next()).split()[1]} {str(operands.next()).split()[1]})"
    if inst.opcode == 'icmp ne':
        rkt_inst = f"(not ({rkt_inst}))"
    rkt_inst = f"{res_reg} = {rkt_inst}"
    print(inst, '->', rkt_inst, ':', inst.type)


# TODO: convert racket to llvm
