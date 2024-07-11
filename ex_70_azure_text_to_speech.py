import os
import requests
from dotenv import load_dotenv
from logzero import logger, loglevel
import logzero

# Load environment variables from .env file
load_dotenv()

# Set log level to DEBUG to show all messages
loglevel(logzero.DEBUG)

# Retrieve Azure Cognitive Services credentials from environment variables
subscription_key = os.getenv('AZURE_COGNITIVE_KEY')
endpoint = os.getenv('AZURE_COGNITIVE_ENDPOINT')

# Function to mask subscription key
def mask_key(key):
    return '*' * (len(key) - 3) + key[-3:]

def text_to_speech(text, output_file):
    url = f"{endpoint}/sts/v1.0/issuetoken"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm'
    }
    body = f"""
    <speak version='1.0' xml:lang='en-US'>
        <voice xml:lang='en-US' xml:gender='Female' name='en-US-JessaNeural'>
            {text}
        </voice>
    </speak>
    """

    try:
        logger.info("Sending request to Azure TTS service")
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request Headers: {{'Ocp-Apim-Subscription-Key': '{mask_key(subscription_key)}', 'Content-Type': 'application/ssml+xml', 'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm'}}")
        logger.debug(f"Request Body: {body}")

        response = requests.post(url, headers=headers, data=body)

        logger.info("Received response from Azure TTS service")
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        logger.debug(f"Response Body: {response.text}")

        if response.status_code == 200:
            with open(output_file, 'wb') as audio:
                audio.write(response.content)
            logger.info(f"Audio content written to file {output_file}")
        else:
            logger.error(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        logger.exception(f"Exception occurred: {str(e)}")

# Example usage
text_to_speech("Hello, this is a test.", "output.wav")
