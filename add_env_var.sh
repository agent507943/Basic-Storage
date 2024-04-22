#!/bin/bash
#

# Function to add an environment variable to ~/.bashrc
add_env_variable() {
    local var_name=$1
    local var_value=$2

    # Check if the environment variable already exists in ~/.bashrc
    if grep -q "^export $var_name=" ~/.bashrc; then
        echo "Environment variable '$var_name' already exists in ~/.bashrc."
    else
        # Append the environment variable to the last line of ~/.bashrc
        echo "export $var_name=$var_value" >> ~/.bashrc
        echo "Environment variable '$var_name' added to the last line of ~/.bashrc"
    fi
}

# Main script logic
if [[ "$1" == "-Name" && "$3" == "-equal" ]]; then
    var_name="$2"
    read -p "Enter the value for $var_name: " var_value
    add_env_variable "$var_name" "$var_value"
else
    echo "Usage: $0 -Name <variable_name> -equal"
fi
