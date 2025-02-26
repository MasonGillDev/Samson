import subprocess
from dotenv import load_dotenv
from openai import OpenAI
import sys
import pandas as pd
import os
import json
load_dotenv()


api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("No API key found. Please set the API_KEY environment variable.")

OpenAI.api_key = api_key

client = OpenAI(api_key=api_key)

# Detect the current shell
shell_name = os.path.basename(os.environ.get("SHELL", "unknown"))


if shell_name == "zsh":
    shell_instruction = "Program for Zsh NOT BASH."
elif shell_name == "bash":
    shell_instruction = "Program for Bash."
else:
    shell_instruction = f"Program for {shell_name}, behavior may be different."

sys.stderr.write("How Can I Help You? ")
initial_prompt = input()

context_df = pd.DataFrame(columns=["prompt", "response"])





def Exbot(prompt):
    exbot_behavior = ("You are a shell command decision agent."
                      "You will analyze the users request and return a JSON object in the following format:"
                      '{"action": "execute", "command": "<shell command(s)>"}'
                      "You need to perform a command that will result in the output desired by the propt."+
                      shell_instruction)
    
    Ex = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": exbot_behavior
            },
            {"role": "user", "content": prompt}
        ]
    )


    Ex_raw_data = Ex.choices[0].message.content.strip()

    try:
        Ex_data = json.loads(Ex_raw_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Main agent response is not valid JSON: {e}")
    print("Ex Command: ",Ex_data.get("command"))
    output =  subprocess.run(Ex_data.get("command"), capture_output=True, text=True,shell=True).stdout
    print("Ex Output: ",output)
    return output


def mainbot(prompt, context):
    mainbot_behavior = ("You are a shell command agent that is an expert at shell commands. "
    "You will analyze the users request and return a JSON object in the following format:\n"
    "Follow these rules exactly:\n\n"
    "- If you can directly fulfill the request with a shell command or multiple, reply with a JSON object in this format:\n"
    '  {"action": "execute", "command": "<shell command(s)>"}\n\n'
    "This is your number one option and always try your best to forfill the request by yourself especialy if it is simple. It is always your first priority to execute the a command.\n\n"
    "- If you require additional context to reliably produce the shell command(s), reply with a JSON object in this format:\n"
    '  {"action": "context", "prompt": "<Exactly what context you need>"}\n\n'
    "The promt you provide will be fed back to yourself, so make sure you can perform an opperation to answer it. The user will not see this prompt you provide So dont ask the user questions. The context you revieve back will be the output of a shell command. But remember if you can figure out how to do the operation without context, do so.\n\n"
    " For example, your prompt may be show me all of the files names on my desktop."
    "Do not include any extra text or commentary; reply strictly with the JSON object."
    + shell_instruction)
    
    Main = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": mainbot_behavior
            },
            {"role": "user", "content": f"{prompt}\n\nContext:\n{context.to_string(index=False)}"}
        ]
    )


    Main_raw_data = Main.choices[0].message.content.strip()

    try:
        Main_data = json.loads(Main_raw_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Main agent response is not valid JSON: {e}")
    
    if Main_data.get("action") == "execute":
        print("Main Command: ",Main_data.get("command"))
        return 1
    else:
        return Main_data
    

def loop(initial_input):
    while True:
        json = mainbot(initial_input,context_df)
        if json == 1:
            break
        prompt = json.get("prompt")
        print("Context Prompt: ",prompt)
        context_data = Exbot(prompt)
        context_df.add({"prompt": prompt, "response": context_data})

loop(initial_prompt)