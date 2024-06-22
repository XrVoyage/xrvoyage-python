import re
import json
import gradio as gr

# Function to detect functions in TypeScript code
def detect_functions(ts_code):
    function_pattern = re.compile(r'^\s*(public|private|protected)?\s*(async\s+)?(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\)\s*{', re.MULTILINE)
    matches = function_pattern.finditer(ts_code)
    functions = []
    
    for match in matches:
        func_name = match.group(3)
        line_number = ts_code[:match.start()].count('\n') + 1
        # Check if the function is commented
        is_commented = ts_code[:match.start()].strip().startswith('//')
        functions.append({'name': func_name, 'commented': is_commented, 'line': line_number})
    
    # Filtering out invalid detections like 'if', 'else', etc.
    functions = [func for func in functions if func['name'] not in ['if', 'for', 'while', 'switch', 'case', 'else', 'return']]
    
    print("Detected functions:", functions)  # Logging detected functions
    return functions

# Function to display the detected functions
def display_functions(ts_code):
    functions = detect_functions(ts_code)
    function_names = [func['name'] for func in functions]
    print("Function names:", function_names)  # Logging function names
    return function_names, json.dumps(functions, indent=2)

# Function to execute the provided code (dummy implementation for TypeScript)
def execute_code(code):
    print("Executing code...")  # Logging code execution
    return "Code execution is not supported for TypeScript in this demo."

# Function to update the JSON representation of functions
def update_functions_json(selected_functions):
    functions = [{'name': func['name'], 'commented': (func['name'] not in selected_functions), 'line': func['line']} for func in all_functions]
    print("Updated functions JSON:", functions)  # Logging updated functions JSON
    return json.dumps(functions, indent=2)

# Function to handle the update of detected functions
def update_detected_functions(ts_code):
    global all_functions
    function_names, functions_json_content = display_functions(ts_code)
    all_functions = detect_functions(ts_code)
    print("Updated all_functions:", all_functions)  # Logging all functions
    return gr.CheckboxGroup(choices=function_names, value=[func['name'] for func in all_functions if not func['commented']], interactive=True), gr.Textbox(value=functions_json_content, interactive=True)

# Creating the Gradio interface
with gr.Blocks() as demo:
    ts_code = gr.Code(language='typescript', lines=20, label="TypeScript Code")
    function_display = gr.CheckboxGroup(label="Detected Functions", choices=[], interactive=True)
    functions_json = gr.Textbox(lines=10, label="Functions JSON", interactive=True)
    execute_button = gr.Button("Execute")
    output = gr.Textbox(lines=10, label="Output", interactive=True)

    all_functions = []

    ts_code.change(fn=update_detected_functions, inputs=ts_code, outputs=[function_display, functions_json])
    function_display.change(fn=update_functions_json, inputs=function_display, outputs=functions_json)
    execute_button.click(fn=execute_code, inputs=ts_code, outputs=output)

    demo.launch()
