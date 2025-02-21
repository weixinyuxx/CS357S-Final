import llvmlite.binding as llvm
import subprocess
import random as rand
from racket2racket import r2r

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

# Valid opcode mappings
valid_opcodes = {'add':'bvadd', 'sub':'bvsub', 'mul':'bvmul',
                     'shl':'bvshl', 'lshr':'bvlshr', 'ashr':'bvashr',
                     'and':'bvand', 'or':'bvor', 'xor':'bvxor',
                     'icmp eq':'bveq', 'icmp ne':'bveq', 'icmp slt':'<', 'icmp sle':'<=', 'icmp sgt':'>', 'icmp sge':'>='} # ne is different

def rkt2llvm(rkt_str):
    # TODO: Implement racket to llvm conversion
    return rkt_str


# Contains all valid instructions from llvm code
inst_list = []
# Mappings of llvm instruction to alternate llvm instruction
alt_llvm_map = dict()

# Read in llvm code file
llvm_file_path = 'test.ll'
with open(llvm_file_path, 'r') as llvm_file:
    llvm_ir_code = llvm_file.read()

# Parse the llvm code
parsed_module = parse_llvm_ir(llvm_ir_code)
print("-----------------------")
for function in parsed_module.functions:
    print(f"Function name: {function.name}")
    # print(f"Function arguments: {function.args}")
    # print(f"Function return type: {function.return_type}")
    # print(f"Function instructions: {function.instructions}")

    print("blocks:")
    for blk in function.blocks:
        print(blk)
        for inst in blk.instructions:
            print("Instruction:", inst)
            print("Opcode:", inst.opcode)
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

# TODO: have different racket output for i32 and i64
# TODO: insert alternative instructions after original instruction and change destination register
# TODO: fix icmp

alt_dest_reg = 0

print("Valid Instructions:")
for inst in inst_list:
    # print(inst)
    # print('Racket:')
    inst_str = str(inst)
    res_reg = inst_str.split()[0] # result register
    opcode = inst.opcode
    operands = inst.operands
    op1 = str(operands.next()).split()[1]
    op2 = str(operands.next()).split()[1]

    # Add constants as (bvadd %reg1 (int 5))
    try:
        op2_int = int(op2)
        op2 = f"(int {op2})"
    except ValueError:
        pass
    
    # Replace dest reg with alt dest reg
    alt_dest_reg_str = f"%dest{alt_dest_reg}"
    while alt_dest_reg_str in llvm_ir_code:
        alt_dest_reg += 1
        alt_dest_reg_str = f"%dest{alt_dest_reg}"
    res_reg = alt_dest_reg_str

    # Build racket instruction from llvm
    rkt_inst = f"({valid_opcodes[opcode]} {op1} {op2})"
    if inst.opcode == 'icmp ne':
        rkt_inst = f"(not ({rkt_inst}))"
    rkt_inst_right = rkt_inst
    rkt_inst = f"{res_reg} = {rkt_inst}"
    print(inst, '->', rkt_inst, ':', inst.type)

    # Write racket information to temp file for next racket script
    llvm_temp_file_path = 'llvm_temp.txt'
    with open(llvm_temp_file_path, 'w') as llvm_temp_file:
        llvm_temp_file.write(str(inst.type)+'\n')
        llvm_temp_file.write(rkt_inst)

    # Call instance of racket script for each instruction
    print('Running Racket script...')
    # result = subprocess.run(['racket', 'binop_base.rkt'], capture_output=True, text=True)
    print(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]])
    alt_rkt_code = r2r(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]], op1, op2)
    print(alt_rkt_code)
    if not alt_rkt_code:
        alt_rkt_code = ""

    # # Read alternative racket code from temp file
    # alt_rkt_temp_file_path = 'alt_rkt_temp.txt'
    # with open(alt_rkt_temp_file_path, 'r') as alt_rkt_temp_file:
    #     alt_rkt_code = alt_rkt_temp_file.read()

    # Convert alternate racket code to alterate llvm code
    alt_llvm_code = rkt2llvm(alt_rkt_code)
    alt_llvm_code = f"{res_reg} = {alt_llvm_code}"
    print("Alternate LLVM:", alt_llvm_code)

    # Add to llvm -> alternate llvm mapping
    alt_llvm_map[inst_str] = alt_llvm_code

print(alt_llvm_map)

# Choose random llvm instruction to test and append alternate llvm instruction
llvm_mod_code = llvm_ir_code
random_line = rand.choice(list(alt_llvm_map.keys()))
replacement_line = alt_llvm_map[random_line]
leading_spaces = 0
for c in random_line:
    if c.isspace():
        leading_spaces += 1
    else:
        break
print(leading_spaces)
replacement_line = leading_spaces * ' ' + replacement_line
print(f'Appending "{replacement_line}" before "{random_line}"')
llvm_mod_code = llvm_mod_code.replace(random_line, f'{replacement_line}\n{random_line}')

# TODO: compare alternate register value with original destination register value
# TODO: have multiple counters to count faults in llvm and print out number at end

# Create new llvm file with modified llvm code
llvm_mod_file_path = 'test_mod.txt'
with open(llvm_mod_file_path, 'w') as llvm_mod_file:
    llvm_mod_file.write(llvm_mod_code)
