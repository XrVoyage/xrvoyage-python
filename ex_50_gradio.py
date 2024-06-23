import gradio as gr
import json
from logzero import logger, loglevel
from xrvoyage import XrApiClient
from xrvoyage.common.config import get_app_config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
settings = get_app_config()

# Set log level based on environment variable
loglevel(settings.LOGLEVEL.upper())

# Initialize XrApiClient
xrclient = XrApiClient(settings.XRVOYAGE_CURRENT_SHIP)

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

# Gradio interface
with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    with gr.Row():
        with gr.Column():
            plugin_guid = gr.Textbox(value=settings.XRVOYAGE_CURRENT_PLUGIN, lines=1, label="Plugin GUID", interactive=True)
            get_plugin_button = gr.Button("GET PLUGIN")
            add_button = gr.Button("Call Add Five")
            add_output = gr.Label(value="Result will show here")
        with gr.Column(scale=2):
            plugin_output = gr.Code(language='typescript', lines=20, label="Plugin Data")

    add_button.click(fn=call_add_five, inputs=None, outputs=add_output)
    get_plugin_button.click(fn=get_plugin_data, inputs=plugin_guid, outputs=plugin_output)

# Launch Gradio app
demo.launch()
