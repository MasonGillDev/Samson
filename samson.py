import subprocess
from dotenv import load_dotenv
from openai import OpenAI
import sys
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

with open("./prompt.txt", "w") as f:
    f.write(initial_prompt)

level = 0
main_system_prompt = (
    "You are a shell command decision agent. Your task is to analyze the user's request "
    "and decide whether you can directly fulfill it with shell commands or if you require additional context in the form of output from other commands. For Example if you need particular file names to perform your task you would say so. "
    "Follow these rules exactly:\n\n"
    "- If you can directly fulfill the request, reply with a JSON object in this format:\n"
    '  {"action": "execute", "command": "<shell command(s)>"}\n\n'
    "This is your number one option and always try your best to forfill the request by yourself esspecialy if it is simple.\n\n"
    "- If you require additional context to reliably produce the shell command(s), reply with a JSON object in this format:\n"
    '  {"action": "context", "prompt": "<follow-up question asking for more details>"}\n\n'
    "The promt you provide will be fed to a seperate agent that only know what you tell it so make sure it is delailed and makes it clear what you need to perform your task. The user will not see this prompt only another agent.\n\n"
    "Your prompt should only present a clear goal and not ask questions. For example, your prompt may be show me all of the files names on my desktop."
    "Do not include any extra text or commentary; reply strictly with the JSON object."
    + shell_instruction
)

sub_system_prompt = (
    "You are a shell command execution agent. Based on the provided request and the complete context already gathered, "
    "your job is to generate correct and safe shell command(s) for execution. You must output your response as a JSON object strictly in the following format:\n\n"
    '{"action": "execute", "command": "<shell command(s)>"}\n\n'
    "Do not include any extra text, commentary, or requests for more context."
    + shell_instruction
)



def samson(prompt,level):
    # Call the OpenAI API
    #Main Agent responcible for determining whether it needs more context or can forfill request going alone.
    Main = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": main_system_prompt
            },
            {"role": "user", "content": prompt}
        ]
    )
    #This should be in json format
    raw_response = Main.choices[0].message.content.strip()



    try:
        Main_data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Main agent response is not valid JSON: {e}")
    

    if Main_data.get("action") == "execute":
        if level == 0:
            print(Main_data.get("command"))
            return 
        else:
            with open("prompt.txt", "a") as f:
                f.write(Main_data.get("command"))
            output =  subprocess.run(Main_data.get("command"), capture_output=True, text=True,shell=True).stdout
            with open("output.txt", "a") as f:
                f.write(output)
            return output
    elif Main_data.get("action") == "context":
        with open("prompt.txt", "a") as f:
                f.write(Main_data.get("prompt"))
        context = samson(Main_data.get("prompt"), level + 1)
    


    # Sub Agent responcible for executing commands.
    Sub = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": sub_system_prompt
            },
            {"role": "user", "content": prompt + context}
        ]
    )

    Sub_raw_data = Sub.choices[0].message.content.strip()

    try:
        Sub_data = json.loads(Sub_raw_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Main agent response is not valid JSON: {e}")

    if Sub_data.get("action") == "execute":
        if level == 0:
            print(Sub_data.get("command"))
            return Sub_data.get("command")
        else:
            with open("prompt.txt", "a") as f:
                f.write(Sub_data.get("command"))
            output =  subprocess.run(Sub_data.get("command"), capture_output=True, text=True,shell=True).stdout
            with open("output.txt", "a") as f:
                f.write(output)
            return output
    else:
         raise ValueError("Sub agent returned an unrecognized action or attempted to request more context.")
    
samson(initial_prompt,level)