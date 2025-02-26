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


def planning_opperator(initial_input):
    planning_behavior = ("You are an agent that creates plans to forfill my shell request. The plans should be concise and manageable with steps. The other thing you output is a list of additional context you need from a commands output. For example if you need a list of the files on my desktop, you would say list of files on my desktop. I will not be executinng the commands but another chatbot will so keep that in mind when making the plan. If you dont need context, leave context empty.You will only return a JSON object in the following format:\n"
                        "In your plan explain how to use the context you are requesting. \n"
                         '  {"plan": "your plan", "context": "context labels"}\n\n'
                      +shell_instruction)
    
    planner = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": planning_behavior
            },
            {"role": "user", "content": initial_input}
        ]
    )


    plan_raw_data = planner.choices[0].message.content.strip()
    print(plan_raw_data)
    json_plan = json.loads(plan_raw_data)
    return json_plan
  

def context_op(context_label,context):
    context_behavior = ("You are a data retrieval agent. You will be passed a request and some data that might be helpful or may not and your job is to write a shell command to output that data request to the terminal.Example Request:error message from running error.py, you would return python3 error.py.  \n"
                         '  You should only return the executable shell command and nothing more.\n\n'
                      +shell_instruction)
    
    context = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": context_behavior
            },
            {"role": "user", "content":f"Data request: {context_label}\nHelpful Context: {', '.join(context)}"}
        ]
    )

    context_raw_data = context.choices[0].message.content.strip()
    output =  subprocess.run(context_raw_data, capture_output=True, text=True,shell=True).stdout
    obj = {context_label:output}
    print(obj)
    
    return obj


def execution_op(initial_input,context,plan):
    context_behavior = ("You are an agent that only return shell commands to for fill my request.You will be given a request, a detailed plan on how to forfill the request and the context you need to execute the plan. "
                        "Don't return anything that won't run on the terminal."
                         
                      +shell_instruction)
    context = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": context_behavior
            },
            {"role": "user", "content": f"Request: {initial_input}\nContext: {context}\nPlan: {plan}"}
        ]
    )
    execution_raw_data = context.choices[0].message.content.strip()
    print(execution_raw_data)


plan = planning_opperator(initial_prompt)
print(plan)

context_labels = [label.strip() for label in plan["context"].split(",") if label.strip()]

context_list = []

if context_labels:
    for label in context_labels:
        print("Retrieving: ",label,"...")
        context_output = context_op(label,context_list)
        context_list.append(context_output[label])


execution_op(initial_prompt,context_list,plan)


