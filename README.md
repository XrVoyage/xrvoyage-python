# xrvoyage-python
Python Client to XrVoyage 

## Example ex_01_wss.py
Establishes connection with a ship. Acts as externalized "all knowing" agent to the ship you are on.
This is the entry point. All other examples in the ex_ series are called by this script.

## Example ex_02_datahook.py
This example sends a data webhook. Data must pre-exist in the solar system. Once webhook is activated on data element you will be provided with an ID, that you can then paste into your .env file.

## Example ex_03_llm-human-in-loop.py
This example will use LangChain & LangGraph multi agent setup, with human-in-the-loop interaction requirements.
It will demonstrate how to take this interaction requirement and hand it over to XRVoyage. There is unlimited amount of ways for this to be intepreted by XRVoyage and totally flexible depending on what plugin functionality you enable to handle incoming event. Most important is that the event is stored in XRVoyage back end redistributed to the 

