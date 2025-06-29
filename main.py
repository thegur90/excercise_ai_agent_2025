import os
import sys
from dotenv import load_dotenv
from functions import get_files_info
from functions.get_files_info import *
from tests import test_from_tests_file


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
print("log 01: It's working!... so far")

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

If applicable, make sure to Specify exacly which function you will call with which arguments.
All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
MAX_ITERS = 20

#pre-written code goes here:
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Reads and returns the content from a specified file within the working directory. Truncates if the text is too large",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content should be read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file within the working directory. Creates the file if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file within the working directory and returns the output from the interpreter.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the Python file.",
                ),
                description="Optional arguments to pass to the Python file.",
            ),
        },
        required=["file_path"],
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_tests": test_from_tests_file
}

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    if not (function_name in function_map):
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
        )
    ],
)
    function_call_part.args["working_directory"] = "./calculator"
    function_result = function_map[function_call_part.name](**function_call_part.args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
    )
    ],
)
#and ends here:
messages = []
count = 0
def main(args):
    global messages
    global count
    count += 1
    feedback_loop = False

    if len(args) < 2:
        print("not enough arguments passed to script!!")
        sys.exit(1)

    messages.append(types.Content(role="user", parts=[types.Part(text=args[1])]))
    if len(messages > 20):
        messages = messages [-MAX_ITERS:]
    
    content_response = client.models.generate_content(model = "gemini-2.0-flash-001", contents = messages, config=config)
    verbose = False
    if "--verbose" in args:
        verbose = True
        print("")
        print(f"User prompt: {args[1]}")
        print(f"Prompt tokens: {content_response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {content_response.usage_metadata.candidates_token_count}")
        print("")
        pass
    
    
    if content_response.function_calls:
        for function_call_part in content_response.function_calls:
            function_call_result = call_function(function_call_part,verbose)
            if not function_call_result.parts[0].function_response.response:
                raise Exception ("fatal exception of some sort")
            if verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
    else:
        print(content_response.text)
    if count < MAX_ITERS and feedback_loop:
        main(sys.argv)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)