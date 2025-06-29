import os
import subprocess


def run_python_file(working_directory, file_path):

    abs_working_dir = os.path.abspath(working_directory)
    abs_dir_path = os.path.abspath(os.path.join(abs_working_dir,file_path))
    if not(abs_dir_path.startswith(abs_working_dir)):
        return (f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')
    if not (os.path.exists(abs_dir_path)):
        return (f'Error: File "{file_path}" not found.')
    if not (abs_dir_path.endswith(".py")):
        return (f'Error: "{file_path}" is not a Python file.')
    output = ("==========================================================================================\n")
    output += (f"running test on {abs_dir_path} in {abs_working_dir}\n")
    
    try:
        scary_arb_python_code_process = subprocess.run(['python3', abs_dir_path], timeout=30, capture_output=True, cwd = abs_working_dir)
        std_out = scary_arb_python_code_process.stdout.decode('utf-8')
        std_err = scary_arb_python_code_process.stderr.decode('utf-8')
        exit_code = scary_arb_python_code_process.returncode

        output += (f'STDOUT:{std_out}\nSTDERR:{std_err}\n')
        if std_out == "" and std_err == "":
            output = ("No output produced.\n")
        if (exit_code != 0):
            output += (f", Process exited with code {exit_code}")
        return output + ("==========================================================================================\n")
    except Exception as e:
        return (f"Error: executing Python file: {e}")
