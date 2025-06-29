import os

def get_files_info(working_directory, directory=None):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_dir_path = os.path.join(abs_working_dir,directory)
        if not(abs_dir_path.startswith(abs_working_dir)):
            return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
        elif not (os.path.isdir(abs_dir_path)):
            return(f'Error: "{directory}" is not a directory')
        return_str = ""
        for entry in os.listdir(abs_dir_path):
            m = os.path.join(abs_dir_path,entry)
            return_str += (f" - {entry}: file_size={os.path.getsize(m)}, is_dir={os.path.isdir(m)}\n")
            
        return return_str
    
    except Exception as e:

        return (f"Error: {e}")
    
def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_dir_path = os.path.join(abs_working_dir,file_path)
        if not(abs_dir_path.startswith(abs_working_dir)):
                return (f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
        elif not (os.path.isfile(abs_dir_path)):
                return(f'Error: File not found or is not a regular file: "{file_path}"')
        MAX_CHARS = 10001
        with open(abs_dir_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
        trunc = (f'[...File "{file_path}" truncated at 10000 characters]')
        if len(file_content_string) >= (MAX_CHARS):
            file_content_string = file_content_string[:-1] + trunc
        return file_content_string

        
    except Exception as e:

        return (f"Error: {e}")

    
def write_file(working_directory, file_path, content):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_dir_path = os.path.abspath(os.path.join(abs_working_dir,file_path))
        abs_dir_path_minus_filename = os.path.abspath(os.path.dirname(abs_dir_path))
        if not(abs_dir_path.startswith(abs_working_dir)):
                return (f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory')
        if not os.path.exists(abs_dir_path_minus_filename):
             os.makedirs(abs_dir_path_minus_filename)
        with open(abs_dir_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
     
    except Exception as e:

        return (f"Error: {e}")






     