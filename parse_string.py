import json

def parse_file_to_json(input_file, output_file):
    questions = []

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i in range(0, len(lines), 6):  # Each question block has 3 lines
        question_line = lines[i].strip()
        options = []
        options.append(lines[i + 1].strip())
        options.append(lines[i + 2].strip())
        options.append(lines[i + 3].strip())
        options.append(lines[i + 4].strip())

        correct_answer_line = int(lines[i + 5].strip())

        # Extract question text and placeholder
        question_text = question_line.replace("<вариант_ответа>", "____")

        correct_answer = correct_answer_line


        # Create question dictionary
        question_data = {
            "question": question_text,
            "answers": "\n".join(options) + "\n",
            "correct_answer": correct_answer
        }

        questions.append(question_data)

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"questions": questions}, file, indent=2, ensure_ascii=False)

    print(f"Successfully parsed and saved to {output_file}")

# Example usage
input_file = "input_string.txt"  # Replace with your input file name
output_file = "questions.json"  # Replace with your desired output file name
parse_file_to_json(input_file, output_file)