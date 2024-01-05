import os
import subprocess
import time

def run_dpll_on_file(dpll_script, cnf_file):
    try:
        result = subprocess.run(['python', dpll_script, cnf_file], capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return str(e)

def process_folder(folder_path, dpll_script, output_file):
    with open(output_file, 'w') as out_file:
        count = 0
        for filename in os.listdir(folder_path):
            if filename.endswith('.cnf'):
                print(count)
                count+=1
                file_path = os.path.join(folder_path, filename)
                result = run_dpll_on_file(dpll_script, file_path)
                out_file.write(f'File: {filename}, Result: {result}')

dpll_script = 'dpll.py'
sat_folder = 'tests/uf20-91'
# unsat_folder = 'tests/unsat'
sat_output_file = 'sat_results.txt'
# unsat_output_file = 'unsat_results.txt'

start_time = time.time()
process_folder(sat_folder, dpll_script, sat_output_file)
end_time = time.time()
print(end_time-start_time)
# process_folder(unsat_folder, dpll_script, unsat_output_file)
