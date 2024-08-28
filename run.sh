#!/bin/bash
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
MODEL="gpt4v" # 'gpt4o', 'claude35', 'gpt4v', 'qwen_vl_max', 'gemini_15_pro', 'blip2'

MODES=("history_image")
# MODES=("base_image" "history_image" "base_text" "history_text")


for MODE in "${MODES[@]}"; do
    OUTPUT_IMAGE_BASE_DIR="outputs/multi_step/image_text/base"
    OUTPUT_IMAGE_HIS_DIR="outputs/multi_step/image_text/history"
    OUTPUT_TEXT_BASE_DIR="outputs/multi_step/text_only/base"
    OUTPUT_TEXT_HIS_DIR="outputs/multi_step/text_only/history"

    if [[ "$MODE" == "base_image" ]]; then
        OUTPUT_DIR="$OUTPUT_IMAGE_BASE_DIR"
        USE_HISTORY=false
        USE_TEXT=false
    elif [[ "$MODE" == "history_image" ]]; then
        OUTPUT_DIR="$OUTPUT_IMAGE_HIS_DIR"
        USE_HISTORY=true
        USE_TEXT=false
    elif [[ "$MODE" == "base_text" ]]; then
        OUTPUT_DIR="$OUTPUT_TEXT_BASE_DIR"
        USE_HISTORY=false
        USE_TEXT=true
    elif [[ "$MODE" == "history_text" ]]; then
        OUTPUT_DIR="$OUTPUT_TEXT_HIS_DIR"
        USE_HISTORY=true
        USE_TEXT=true
    else
        echo "无效的 mode: $MODE"
        exit 1
    fi

    mkdir -p "$OUTPUT_DIR/$LOG_DIR"
    LOG_FILE="$OUTPUT_DIR/$LOG_DIR/${MODE}_${MODEL}.log"
    
    python3 src/main.py --mode "$MODE" --model "$MODEL" > "$LOG_FILE" 2>&1
done
