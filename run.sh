cmd=$(python3 /Users/masongill/Desktop/Projects/Samson/loop_agent_model.py | tr -d '\r' | awk '{$1=$1};1')

output=/Users/masongill/Desktop/Projects/Samson/output.txt

echo "Executing:"
echo "$cmd"

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
    exit 1
fi

# Wait for user confirmation before executing
echo "Press Enter to execute the command..."
read -r dummy < /dev/tty



echo "Executing: $cmd"

# Run the command directly in the current shell
eval "$cmd" 2>&1 > "/Users/masongill/Desktop/Programs/Samson/output.txt"
# Also display the output if needed
cat "/Users/masongill/Desktop/Programs/Samson/output.txt"



command="$cmd"

#This function is not yet working
while grep -qi "error\|failed\|no such file\|not found" "$output"; do
    echo "Error detected. Re-running the Python program..."

    # Generate a new command via debugger.py
    cmd=$(python3 ~/DB_Friend/debugger.py "$output" "$command" | tr -d '\r' | awk '{$1=$1};1')
    
    echo "New command generated:"
    echo "$cmd"
    
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
    
    # Wait for user confirmation before executing the command
    echo "Press Enter to execute the command..."
    read -r dummy < /dev/tty
    
    echo "Executing: $cmd"
    # Execute the command, log output to the file, and highlight any error messages
# Run the command directly in the current shell
    eval "$cmd" 2>&1 > "$HOME/DB_Friend/output.txt"
# Also display the output if needed
    cat "$HOME/DB_Friend/output.txt"
    
    # Update the command variable for the next iteration
    command="$cmd"
done
