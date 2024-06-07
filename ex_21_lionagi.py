import asyncio
import pandas as pd
from lionagi.core.message import System, Instruction
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.agent.base_agent import BaseAgent
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Comedian Agent Structure
system_prompt = """---TASK
1. You are most outstanding mystery game designer. 
2. YOU WILL NOT SKIP ANY OF THE 18 POINTS FROM THIS LIST
3. Your job is to generate a game as multiple choice quiz definition dataset. 
4. Ensure that the provided numbers of scenes and choices match the actual number of scenes and choices in the JSON structure.

---OUTPUT REQUIREMENT
5. The root key is `xrvoyage_game`
6. Under `xrvoyage_game`, include the following keys:
   - `theme`: A string indicating the theme of the game
   - `scenes`: An integer indicating the number of scenes.
   - `choices`: An integer indicating the number of choices per scene.
   - `scenes`: A list of dictionaries, where each dictionary represents a scene with:
     - `story`: A generated story from which to form questions.   
     - `question`: A string representing the title of the scene.
     - `choices`: A list of dictionaries, where each dictionary represents a choice with:
       - `name`: A short string.
       - `correct_answer`: A boolean indicating if the choice is correct.
7. Your response must be in JSON format and nothing else so it can be easily structured.
8. Ensure that the provided numbers of scenes and choices match the actual number of scenes and choices in the JSON structure.

---THE SCENE: QUESTION is SUB-THEME
9. For each scene you pick a related sub-theme from: locations, time, space, designs, engineering, art, science, curiosities, anecdotes, employees, workers and situations.
10. For each scene generate intriguing story
11. The scene story should not spoil answers to posed choices.
12. Generate question that is a mix of theme and selected sub-theme.
13. Generate all scene choices in the same sub-theme (related to question)
14. Your question is super important, all choices in that theme should stay within the theme, otherwise it will be easy to identify the answers.
15. Your questions will not reveal correct answers.

---THE CHOICES
16. Your questions will not reveal correct answers.
17. Your choices will not be obvious and keep them short.
18. Number of correct "true" choices MUST vary between 40-60% in each scene."""

vr_quiz_game_system = System(system=system_prompt)

def create_prompt_instructions(theme):
    scenes = 3
    choices = 4
    instructions = {
        "objective": f"Generate a game quiz definition dataset for the theme '{theme}'",
        "variables": ["question", "story", "choices", "correct_answer"],
        "constraints": [
            f"Create {scenes} scenes with {choices} choices per scene.",
            f"Ensure each scene has a detailed story, a question, and choices adhering to the given sub-themes."
        ],
        "requirements": [
            "Each scene should have a detailed story.",
            "Each question should be a mix of the theme and the selected sub-theme.",
            "All choices in a scene should relate to the sub-theme.",
            "Number of correct 'true' choices MUST vary between 40-60% in each scene."
        ]
    }
    return json.dumps(instructions)

json_instructions = create_prompt_instructions("mickey mouse")

vr_quiz_instruction = Instruction(instruction=json_instructions)

graph_comedian = GraphExecutor()
graph_comedian.add_node(vr_quiz_game_system)
graph_comedian.add_node(vr_quiz_instruction)
graph_comedian.add_edge(vr_quiz_game_system, vr_quiz_instruction)

def output_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        logger.debug(f"Processing branch: {branch}")
        df = branch.to_df()
        logger.debug(f"Branch DataFrame: \n{df}")
        assistant_responses = df[df['message_type'] == 'AssistantResponse']
        for content in assistant_responses['content']:
            assistant_response = content.get('assistant_response', '')
            if assistant_response.startswith('```json'):
                json_content = assistant_response.strip('```json\n').strip('\n```')
                parsed_json = json.loads(json_content)
                output.append(parsed_json)
                logger.debug(f"Parsed JSON: \n{json.dumps(parsed_json, indent=4)}")
    return output

executable = InstructionMapEngine()
comedian = BaseAgent(structure=graph_comedian, executable=executable, output_parser=output_parser)

async def main():
    result = await comedian.execute()
    return result

result = asyncio.run(main())

# Print the parsed JSON content
for json_content in result:
    print(json.dumps(json_content, indent=4))
