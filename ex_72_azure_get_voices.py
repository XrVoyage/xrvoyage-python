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
region = os.getenv('AZURE_COGNITIVE_REGION')  # Change this to AZURE_COGNITIVE_REGION

# Add a check to ensure the region is not None
if not region:
    logger.error("Azure Cognitive Region is not set in the environment variables")
    exit(1)

def get_voices():
    # The correct endpoint for listing voices
    voices_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    
    try:
        logger.info(f"Sending request to Azure TTS service for voices list")
        logger.debug(f"Request URL: {voices_url}")
        logger.debug("Request Headers: {'Ocp-Apim-Subscription-Key': '[REDACTED]'}")
        
        response = requests.get(voices_url, headers=headers)
        
        logger.info(f"Received response from Azure TTS service. Status code: {response.status_code}")
        
        if response.status_code == 200:
            voices = response.json()
            voice_info = [{"Name": voice['ShortName'], "Locale": voice['Locale']} for voice in voices]
            return voice_info
        else:
            logger.error(f"Error: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request Exception occurred: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected Exception occurred: {str(e)}")
        return None

# Retrieve and print the list of voice names
voice_info = get_voices()
if voice_info:
    print("Available voices:")
    for voice in voice_info:
        print(f"Name: {voice['Name']}, Locale: {voice['Locale']}")
else:
    print("Failed to retrieve voice information")