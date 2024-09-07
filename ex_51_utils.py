import gradio as gr

def render_func_blocks(class_functions):
    with gr.Blocks() as func_blocks:
        with gr.Row():
            for class_name, functions in class_functions.items():
                with gr.Column():
                    gr.Markdown(f"### {class_name}")
                    checkboxes = []
                    for function in functions:
                        checkbox = gr.Checkbox(label=function)
                        checkboxes.append(checkbox)
                    submit_button = gr.Button("Submit")
                    output_label = gr.Label()

                    def on_submit(*checkbox_values):
                        selected = [func for func, selected in zip(functions, checkbox_values) if selected]
                        return f"Selected functions for {class_name}: {', '.join(selected)}"

                    submit_button.click(on_submit, inputs=checkboxes, outputs=output_label)
    return func_blocks
