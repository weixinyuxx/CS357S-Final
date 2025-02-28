import subprocess
import sys
import time
import shutil
import os
import random as rand
import matplotlib.pyplot as plt
from tqdm import tqdm

ERR_PROB = 0.001
NUM_RUNS = 10000
INTRODUCE_ERRORS = True

# Directory and file paths
file_name = 'test_all'
test_dir_path = 'test'
temp_dir_path = 'temp'
c_file_path = os.path.join(test_dir_path, f"{file_name}.c")
llvm_file_path = os.path.join(temp_dir_path, f"{file_name}.ll")
llvm_mod_file_path = os.path.join(temp_dir_path, f"{file_name}_mod.ll")
exe_file_path = os.path.join(temp_dir_path, f"{file_name}_mod_exe")

start_str = "call void @sdc_check_"
error_idx_list = []

start_time_total = time.time()
print(f"*** SDC Analysis: {file_name} ***")

with open(llvm_mod_file_path, "r") as llvm_mod_file:
    line_idx = 0
    llvm_mod_code = llvm_mod_file.read()
    llvm_mod_file.seek(0)
    for line in llvm_mod_file:
        line = line.strip()
        # print(line)
        if line.startswith(start_str):
            line_words = line.split()
            # TODO: Does not work if the value was already -1
            line_words[3] = '-1,' if line_words[3].startswith('%') else (str(int(line_words[3]) + 1)+',')
            line_replace = ' '.join(line_words)
            llvm_mod_err_code = llvm_mod_code.replace(line, line_replace)

            # Create new llvm file with modified error llvm code
            llvm_mod_err_file_path = os.path.join(temp_dir_path, f"{file_name}_mod_err_{line_idx}.ll")
            with open(llvm_mod_err_file_path, 'w') as llvm_mod_err_file:
                llvm_mod_err_file.write(llvm_mod_err_code)
            
            # Convert llvm file to executable
            exe_err_file_path = os.path.join(temp_dir_path, f"{file_name}_mod_exe_err_{line_idx}")
            try:
                subprocess.run(["clang", llvm_mod_err_file_path, "-o", exe_err_file_path], check=True)
                print(f"Clang Conversion Successful: {llvm_mod_err_file_path} -> {exe_err_file_path}")
            except subprocess.CalledProcessError as e:
                print(f"***Error in Clang Conversion***")
            
            error_idx_list.append(line_idx)
        line_idx += 1

# Run executables for analysis
found_errors = dict()
found_error_count = 0
true_error_count = 0
total_error_prob = 1 - (1 - ERR_PROB) ** len(error_idx_list)
print("Total Error Prob:", total_error_prob)

progress = tqdm(range(NUM_RUNS))
for run_num in progress:
    progress.set_postfix({"Errors found":found_error_count, "Total Errors": true_error_count})
    curr_exe_file_path = exe_file_path

    # If INTRODUCE_ERRORS set to True, then introduce artificial errors with probability ERR_PROB
    if INTRODUCE_ERRORS and (rand.random() < total_error_prob): # error occurs
        true_error_count += 1
        curr_exe_file_path = os.path.join(temp_dir_path, f"{file_name}_mod_exe_err_{rand.choice(error_idx_list)}")
    
    result = subprocess.run([f"./{curr_exe_file_path}"], capture_output=True)
    # print(result)
    if result.returncode == 0:
        # print(f"Execution Successful: {result.returncode}")
        pass
    else:
        # print(f"***Error in Execution: {result.returncode}***")
        found_error_count += 1
        if result.returncode in found_errors:
            found_errors[result.returncode] += 1
        else:
            found_errors[result.returncode] = 1

print(f"Error Distribution: {str(found_errors)}")
print(f"Found Error Count: {found_error_count}")
print(f"True Error Count: {true_error_count}")
plt.figure(figsize=(8, 5))
plt.bar(found_errors.keys(), found_errors.values(), color="blue")

plt.xlabel("Line index")
plt.ylabel("Error Count")
plt.title("Distribution of Errors")

plt.show()
end_time_total = time.time()
print(f"Total Elapsed Time: {end_time_total - start_time_total} s")