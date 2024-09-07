import gradio as gr
import json
from logzero import logger, loglevel
from xrvoyage import XrApiClient
from xrvoyage.common.config import get_app_config
from dotenv import load_dotenv
from gradio_toggle import Toggle


# Load environment variables
load_dotenv()
settings = get_app_config()

# Set log level based on environment variable
loglevel(settings.LOGLEVEL.upper())

# Initialize XrApiClient
xrclient = XrApiClient(settings.XRVOYAGE_CURRENT_SHIP)

def toggle_update(input):
    output = input
    return output

def call_add_five():
    try:
        result = xrclient.add_five()  # Assuming this method exists in xrclient and returns a result
        logger.debug(f"Result from add_five: {result}")
        return f"Result: {result}"
    except Exception as e:
        logger.error(f"Error in call_add_five: {str(e)}")
        return f"Error: {str(e)}"

def get_plugin_data(plugin_guid):
    try:
        plugin_data = xrclient.plugin_handler.get_plugin_by_guid(plugin_guid)
        logger.debug(f"Fetched plugin data: {plugin_data}")
        return json.dumps(plugin_data, indent=2)
    except Exception as e:
        logger.error(f"Error fetching plugin: {str(e)}")
        return f"Error fetching plugin: {str(e)}"

def toggle_dark_mode():
    return """
    () => {
        document.body.classList.toggle('dark');
    }
    """

#document.body.classList.toggle('dark');
# Gradio interface
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            with gr.Tab("Get Plugin"):
                plugin_guid = gr.Textbox(value=settings.XRVOYAGE_CURRENT_PLUGIN, lines=1, label="Plugin GUID", interactive=True)
                get_plugin_button = gr.Button("GET PLUGIN")
            with gr.Tab("State Test"):               
                add_button = gr.Button("Call Add Five")
                add_output = gr.Label(value="Result will show here")
            with gr.Tab("Functions"):               
                text_count = gr.Slider(1, 5, step=1, label="Textbox Count")

                @gr.render(inputs=text_count)
                def render_count(count):
                    boxes = []
                    for i in range(count):
                        box = gr.Textbox(key=i, label=f"Box {i}")                
                        boxes.append(box)

                    def merge(*args):
                        return " ".join(args)
                    
                    merge_btn.click(merge, boxes, output)

                    def clear():
                        return [""] * count
                            
                    clear_btn.click(clear, None, boxes)

                    def countup():
                        return [i for i in range(count)]
                    
                    count_btn.click(countup, None, boxes, queue=False)

                with gr.Row():
                    merge_btn = gr.Button("Merge")
                    clear_btn = gr.Button("Clear")
                    count_btn = gr.Button("Count")
                    
                output = gr.Textbox()            
            with gr.Tab("Theme"):                 
                dark_mode_button = gr.Button("Toggle Dark Mode")
        with gr.Column(scale=2):
            with gr.Tab("XrVoyage Plugin - Raw"):
                plugin_output = gr.Code(language='json', lines=20, label="JSON")
            with gr.Tab("XrVoyage Plugin - Decoded"):
                # input = Toggle(
                #     label="Input",
                #     value=False,
                #     info="Input version of the component",
                #     interactive=True,
                # )
                # output = Toggle(
                #     label="Output",
                #     value=False,
                #     color="blue",
                #     info="Output version of the component",
                #     interactive=False,
                # )
                    
                # input.change(fn=toggle_update, inputs=input, outputs=output)                
                plugin_source = gr.Code(language='typescript', lines=20, label="TypeScript")                

    add_button.click(fn=call_add_five, inputs=None, outputs=add_output)
    get_plugin_button.click(fn=get_plugin_data, inputs=plugin_guid, outputs=plugin_output)
    dark_mode_button.click(None, [], [], js=toggle_dark_mode())

# Launch Gradio app
demo.launch()


