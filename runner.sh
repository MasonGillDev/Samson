#!/bin/bash
# runner.h: Reads a command string from standard input, executes it, and prints the output.



read -r command

destructive_patterns=(
    "rm"
    "rm -rf"
    "rm -rf /"
    "rm -rf ~"
    "dd if=/dev/zero"
    "mkfs"
    ":(){ :|:& };:"  # Fork bomb pattern
    "shutdown"
    "reboot"
    "chmod -R 000"
    "chown -R"
)

# Check if any destructive pattern is found in the command
destructive_found=0
for pattern in "${destructive_patterns[@]}"; do
    if [[ "$command" == *"$pattern"* ]]; then
        echo "⚠️  WARNING: Destructive command pattern detected: '$pattern'"
        destructive_found=1
    fi
done
# If a destructive pattern is detected, ask for extra confirmation
if [[ $destructive_found -eq 1 ]]; then
    echo "This command may be destructive. Do you really want to continue? (yes/no)"
    read -r confirm < /dev/tty
    if [[ "$confirm" != "yes" ]]; then
        echo "Aborted."
        exit 1
    fi
    exit 1
fi

output=$(eval "$command" 2>&1)


while grep -qi "error\|failed\|no such file\|not found" "$output"; do
    echo "Error detected. Re-running the Python program..."

    # Generate a new command via debugger.py
    command=$(python3 ~/Samson/debugger.py "$output" "$command" | tr -d '\r' | awk '{$1=$1};1')
    
    
    # Define an array of destructive command patterns
    destructive_patterns=(
        "rm"
        "rm -rf"
        "rm -rf /"
        "rm -rf ~"
        "dd if=/dev/zero"
        "mkfs"
        ":(){ :|:& };:"  # Fork bomb pattern
        "shutdown"
        "reboot"
        "chmod -R 000"
        "chown -R"
    )
    
    # Check if any destructive pattern is found in the command
    destructive_found=0
    for pattern in "${destructive_patterns[@]}"; do
        if [[ "$cmd" == *"$pattern"* ]]; then
            echo "⚠️  WARNING: Destructive command pattern detected: '$pattern'"
            destructive_found=1
        fi
    done
    
    # If a destructive pattern is detected, ask for extra confirmation
    if [[ $destructive_found -eq 1 ]]; then
        echo "This command may be destructive. Do you really want to continue? (yes/no)"
        read -r confirm < /dev/tty
        if [[ "$confirm" != "yes" ]]; then
            echo "Aborted."
            exit 1
        fi
    fi
    
   
    
output=$(eval "$command" 2>&1)

done


echo "$output"