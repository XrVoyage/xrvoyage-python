import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load API key from .env file
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Initialize Tavily client
client = TavilyClient(api_key=TAVILY_API_KEY)

# Define the search query
search_query = 'inurl:/openapi.json filetype:json'

# Perform the search
response = client.search(query=search_query)

# Check if the request was successful and print results
if 'results' in response:
    search_results = response['results']
    # Print or process the search results
    for result in search_results:
        print(result)
else:
    print("Error: No results found.")
