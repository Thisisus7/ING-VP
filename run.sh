#!/bin/bash

# Define the model name
MODEL_NAME="gpt4o"

# Define the command to execute your Python scripts
PYTHON_CMD_1="python src/multi_step/infer.py"  # Multi-step script
PYTHON_CMD_2="python src/one_step/infer.py"  # Single-step script
PYTHON_CMD_3="python src/summary.py"  # Evaluation script

# Execute the multi-step commands simultaneously
$PYTHON_CMD_1 --mode base_image --model-name "$MODEL_NAME" --use-system-prompt True --temperature 0 --processes-nums 4 &
$PYTHON_CMD_1 --mode history_image --model-name "$MODEL_NAME" --use-system-prompt True --temperature 0 --processes-nums 4 &
$PYTHON_CMD_1 --mode base_text --model-name "$MODEL_NAME" --use-system-prompt True --temperature 0 --processes-nums 4 &
$PYTHON_CMD_1 --mode history_text --model-name "$MODEL_NAME" --use-system-prompt True --temperature 0 --processes-nums 4 &

# Wait for all multi-step background processes to finish
wait

echo "All multi-step modes executed simultaneously."

# Execute the single-step commands simultaneously
$PYTHON_CMD_2 --mode image --model-name "$MODEL_NAME" --processes-nums 4 &
$PYTHON_CMD_2 --mode text --model-name "$MODEL_NAME" --processes-nums 4 &

# Wait for all single-step background processes to finish
wait

echo "All single-step modes executed simultaneously."

$PYTHON_CMD_3

echo "The evalution is complete!"
