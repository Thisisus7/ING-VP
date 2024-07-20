import os
import json
import re

def extract_instructions(output, filename):
    if filename.startswith('maze') or filename.startswith('sokoban'):
        # For maze and sokoban, extract UDLR instructions
        instructions = re.findall(r'[UDLR]+', output)
        return ''.join(instructions)
    elif filename.startswith('n-queens'):
        # For n-queens, extract the list of lists
        match = re.search(r'\[(\[[\d,\s]+\](?:,\s*\[[\d,\s]+\])*)\]', output)
        if match:
            return match.group(0)
    elif filename.startswith('sudoku'):
        # For sudoku, extract the dictionary
        match = re.search(r'\{(?:"[0-9]+"\s*:\s*\d+(?:,\s*"[0-9]+"\s*:\s*\d+)*)\}', output)
        if match:
            # Parse the matched string as JSON to remove escapes
            return json.dumps(json.loads(match.group(0)))
    
    # If no match found or unknown file type, return empty string
    return ""

def process_jsonl_files(raw_dir, formatted_dir):
    # Ensure the formatted directory exists
    os.makedirs(formatted_dir, exist_ok=True)

    # Iterate over all files in the raw directory
    for filename in os.listdir(raw_dir):
        if filename.endswith('.jsonl'):
            raw_file_path = os.path.join(raw_dir, filename)
            formatted_file_path = os.path.join(formatted_dir, filename)

            with open(raw_file_path, 'r', encoding='utf-8') as raw_file, open(formatted_file_path, 'w', encoding='utf-8') as formatted_file:
                for line in raw_file:
                    try:
                        data = json.loads(line)
                        output = data.get('output', '')
                        formatted_output = extract_instructions(output, filename)
                        data['output'] = formatted_output
                        formatted_file.write(json.dumps(data, ensure_ascii=False) + '\n')
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file {filename}, line: {line}")
                    except Exception as e:
                        print(f"Error processing file {filename}: {str(e)}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join('outputs', 'one_step', 'models', 'raw')
    formatted_dir = os.path.join('outputs', 'one_step', 'models', 'formatted')
    process_jsonl_files(raw_dir, formatted_dir)