import llvmlite.binding as llvm
import subprocess
import sys
import time
import os
from racket2racket import r2r
from rkt2llvm import rkt2llvm, DestReg

USE_SYNTHESIS = True

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

# Contains all valid instructions from llvm code
inst_list = []
# Mappings of llvm instruction to alternate llvm instruction
alt_llvm_map = dict()

# Directory and file paths
file_name = 'pow2'
test_dir_path = 'test'
temp_dir_path = 'temp'
c_file_path = os.path.join(test_dir_path, f"{file_name}.c")
llvm_file_path = os.path.join(temp_dir_path, f"{file_name}.ll")
if USE_SYNTHESIS:
    llvm_mod_file_path = os.path.join(temp_dir_path, f"{file_name}_mod.ll")
    exe_file_path = os.path.join(temp_dir_path, f"{file_name}_mod_exe")
else:
    llvm_mod_file_path = os.path.join(temp_dir_path, f"{file_name}_dup.ll")
    exe_file_path = os.path.join(temp_dir_path, f"{file_name}_dup_exe")
# Reset temp folder
# if os.path.exists(temp_dir_path):
#     shutil.rmtree(temp_dir_path)
# os.makedirs(temp_dir_path)

# Convert c file to llvm file
try:
    subprocess.run(["clang", "-S", "-emit-llvm", c_file_path, "-o", llvm_file_path], check=True)
except subprocess.CalledProcessError as e:
    print(f"***Error in Clang conversion***")

# Read in llvm code file
with open(llvm_file_path, 'r') as llvm_file:
    llvm_ir_code = llvm_file.read()

# Parse the llvm code
parsed_module = parse_llvm_ir(llvm_ir_code)
print("-----------------------")
for function in parsed_module.functions:
    print(f"Function name: {function.name}")

    print("blocks:")
    for blk in function.blocks:
        print(blk)
        for inst in blk.instructions:
            print("Instruction:", inst)
            print("Opcode:", inst.opcode)
            if inst.opcode in valid_opcodes:
                inst_list.append(inst)
        print()
    
    print("Type:", function.type)

    print("args:")
    for arg in function.arguments:
        print(arg)
    
    print("attributes:")
    for att in function.attributes:
        print(att)

sys.stdout.flush()

generated = 0
not_generated = 0


alt_dest_reg = 0
llvm_mod_code = llvm_ir_code
dest_reg = DestReg()
inst_types = ['i32', 'i64', 'i1']
count = 0
print("Valid Instructions:")
for inst in inst_list:
    count += 1
    start_time_inst = time.time()
    inst_str = str(inst)
    res_reg = inst_str.split()[0] # result register
    old_res_reg = res_reg
    opcode = inst.opcode
    operands = inst.operands
    operands = inst.operands
    op1_list = str(operands.next()).split()
    op1 = op1_list[0]
    if op1 in inst_types:
        op1 = op1_list[1]
    op2_list = str(operands.next()).split()
    op2 = op2_list[0]
    if op2 in inst_types:
        op2 = op2_list[1]
    print("op1:", op1)
    print("op2:", op2)

    # Add constants as (bvadd %reg1 (int 5))
    try:
        op2_int = int(op2)
        op2 = f"(int {op2})"
    except ValueError:
        pass

    try:
        op1_int = int(op1)
        op1 = f"(int {op1})"
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
    alt_rkt_code = None
    if USE_SYNTHESIS:
        print(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]], op1, op2)
        alt_rkt_code = r2r(rkt_inst_right, str(inst.type), [valid_opcodes[opcode]], op1, op2)
    if not alt_rkt_code:
        print("No alternative found")
        alt_rkt_code = ""
    alt_rkt_code = alt_rkt_code.strip()

    # Convert alternate racket code to alterate llvm code
    line = inst_str
    num_leading_spaces = 0
    for c in line:
        if c.isspace():
            num_leading_spaces += 1
        else:
            break
    leading_spaces = num_leading_spaces * ' '
    alt_llvm_code = ""
    if alt_rkt_code == "":
        alt_llvm_code = leading_spaces + inst_str.replace(old_res_reg, res_reg).strip()
        not_generated += 1
    else:
        print("alt_rkt_code:", alt_rkt_code)
        print("type:", str(inst.type))
        print("dest_reg:", dest_reg)
        if not alt_rkt_code.startswith('(') or not alt_rkt_code.endswith(')'):
            alt_dest_reg_str = alt_rkt_code
        else:
            alt_llvm_code_list, alt_dest_reg_str = rkt2llvm(alt_rkt_code, str(inst.type), dest_reg)
            for alt_line in alt_llvm_code_list:
                alt_llvm_code += leading_spaces + alt_line + "\n"
            alt_llvm_code = alt_llvm_code.rstrip()
        generated += 1

    print("Alternate LLVM:", alt_llvm_code)

    # Add to llvm -> alternate llvm mapping
    alt_llvm_map[inst_str] = alt_llvm_code
    alt_line = alt_llvm_code
    
    sdc_line = leading_spaces + f"call void @sdc_check_{str(inst.type)}({str(inst.type)} {old_res_reg}, {str(inst.type)} {alt_dest_reg_str}, i32 {count})"
    print(f'Appending "{alt_line}" before "{line}"')
    print(f'Appending "{sdc_line}" after "{line}"')
    llvm_mod_code = llvm_mod_code.replace(line, f'{alt_line}\n{line}\n{sdc_line}')
    end_time_inst = time.time()
    print(f"Instruction Time: {end_time_inst - start_time_inst} s")
    print("")
    sys.stdout.flush()

print(alt_llvm_map)


sdc_check_code = """

define void @sdc_check_i32(i32 %reg1, i32 %reg2, i32 %counter) {
entry:
    %cmp = icmp ne i32 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @exit(i32 %counter)
    br label %done

done:
    ret void
}

define void @sdc_check_i64(i64 %reg1, i64 %reg2, i32 %counter) {
entry:
    %cmp = icmp ne i64 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @exit(i32 %counter)
    br label %done

done:
    ret void
}

define void @sdc_check_i1(i1 %reg1, i1 %reg2, i32 %counter) {
entry:
    %cmp = icmp ne i1 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @exit(i32 %counter)
    br label %done

done:
    ret void
}

declare void @exit(i32)

"""

llvm_mod_code += sdc_check_code

# Create new llvm file with modified llvm code
with open(llvm_mod_file_path, 'w') as llvm_mod_file:
    llvm_mod_file.write(llvm_mod_code)

# Convert llvm file to executable
try:
    subprocess.run(["clang", llvm_mod_file_path, "-o", exe_file_path], check=True)
    print(f"Clang Conversion Successful: {llvm_mod_file_path} -> {exe_file_path}")
except subprocess.CalledProcessError as e:
    print(f"***Error in Clang Conversion***")

result = subprocess.run([f"./{exe_file_path}"])
if result.returncode == 0:
    print(f"Execution Successful: {result.returncode}")
else:
    print(f"***Error in Execution: {result.returncode}***")

end_time_total = time.time()
print(f"Total Elapsed Time: {end_time_total - start_time_total} s")
print(f"Alternative generated: {generated}")