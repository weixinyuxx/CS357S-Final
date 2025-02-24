import llvmlite.binding as llvm
import subprocess
import sys
import time
import random as rand
from racket2racket import r2r

start_time_total = time.time()
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

c_file_path = 'test.c'
llvm_file_path = 'test.ll'

# TODO: change to read in c file, call clang, and parse generated llvm file
# try:
#     subprocess.run(["clang", "-S", "-emit-llvm", c_file_path, "-o", llvm_file_path], check=True)
# except subprocess.CalledProcessError as e:
#     print(f"***Error in Clang conversion***")

# Read in llvm code file
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

# TODO: fix icmp
sys.stdout.flush()

alt_dest_reg = 0
llvm_mod_code = llvm_ir_code

print("Valid Instructions:")
for inst in inst_list:
    start_time_inst = time.time()
    # print(inst)
    # print('Racket:')
    inst_str = str(inst)
    res_reg = inst_str.split()[0] # result register
    old_res_reg = res_reg
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
    alt_dest_reg += 1

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
    sys.stdout.flush()
    # result = subprocess.run(['racket', 'binop_base.rkt'], capture_output=True, text=True)
    print(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]])
    alt_rkt_code = r2r(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]], op1, op2)
    # print(alt_rkt_code)
    if not alt_rkt_code:
        print("No alternative found")
        alt_rkt_code = ""

    # # Read alternative racket code from temp file
    # alt_rkt_temp_file_path = 'alt_rkt_temp.txt'
    # with open(alt_rkt_temp_file_path, 'r') as alt_rkt_temp_file:
    #     alt_rkt_code = alt_rkt_temp_file.read()

    # Convert alternate racket code to alterate llvm code
    alt_llvm_code = rkt2llvm(alt_rkt_code)
    if alt_rkt_code == "":
        alt_llvm_code = inst_str.replace(old_res_reg, res_reg).strip()
    else:
        alt_llvm_code = f"{res_reg} = {alt_llvm_code}"
    print("Alternate LLVM:", alt_llvm_code)

    # Add to llvm -> alternate llvm mapping
    alt_llvm_map[inst_str] = alt_llvm_code
    line = inst_str
    alt_line = alt_llvm_code
    num_leading_spaces = 0
    for c in line:
        if c.isspace():
            num_leading_spaces += 1
        else:
            break
    leading_spaces = num_leading_spaces * ' '
    sdc_line = f"call void @sdc_check_{str(inst.type)}({str(inst.type)} {old_res_reg}, {str(inst.type)} {res_reg})"
    print(f'Appending "{leading_spaces}{alt_line}" before "{line}"')
    print(f'Appending "{leading_spaces}{sdc_line}" after "{line}"')
    llvm_mod_code = llvm_mod_code.replace(line, f'{leading_spaces}{alt_line}\n{line}\n{leading_spaces}{sdc_line}')
    end_time_inst = time.time()
    print(f"Instruction Time: {end_time_inst - start_time_inst} s")
    print("")
    sys.stdout.flush()

print(alt_llvm_map)

# TODO: Instead of random, generate new version with all substutions
# Choose random llvm instruction to test and append alternate llvm instruction

# for line, alt_line in alt_llvm_map.items():
#     leading_spaces = 0
#     for c in line:
#         if c.isspace():
#             leading_spaces += 1
#         else:
#             break
#     replacement_line = leading_spaces * ' ' + alt_line
#     print(f'Appending "{replacement_line}" before "{line}"')
#     llvm_mod_code = llvm_mod_code.replace(line, f'{replacement_line}\n{line}')

# TODO: add code to compare alternate register value with original destination register value
# TODO: script to run and test alternate file

sdc_check_code = '''

define void @sdc_check_i32(i32 %reg1, i32 %reg2) {
entry:
    %cmp = icmp ne i32 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @abort()
    br label %done

done:
    ret void
}

define void @sdc_check_i64(i64 %reg1, i64 %reg2) {
entry:
    %cmp = icmp ne i64 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @abort()
    br label %done

done:
    ret void
}

declare void @abort()
'''
llvm_mod_code += sdc_check_code

# Create new llvm file with modified llvm code
llvm_mod_file_path = 'test_mod.txt'
with open(llvm_mod_file_path, 'w') as llvm_mod_file:
    llvm_mod_file.write(llvm_mod_code)

end_time_total = time.time()
print(f"Total Elapsed Time: {end_time_total - start_time_total} s")