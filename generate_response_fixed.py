
def generate_response(answer_raw, prebuilt_tooltips, frameworks_gpt):
    # Section headers expected in the answer
    response_sections = {
        "Strategy or Explanation": "",
        "Story or Analogy": "",
        "Reflection Prompts": "",
        "Concept/Tool References": ""
    }

    # Parse sections from raw answer
    current_section = None
    for line in answer_raw.split("\n"):
        line = line.strip()
        if line in response_sections:
            current_section = line
        elif current_section:
            response_sections[current_section] += line + " "

    # Ensure all sections are present
    for section in response_sections:
        if not response_sections[section].strip():
            response_sections[section] = "_[This section was not generated — please revise your prompt or add logic to fill this in.]_"

    # Combine all sections into final answer
    final_answer = ""
    for section, content in response_sections.items():
        final_answer += f"**{section}**\n{content.strip()}\n\n"

    # Inject tooltips if keywords appear
    for term, definition in prebuilt_tooltips.items():
        if term in final_answer and definition not in final_answer:
            final_answer += f"- **{term}**: {definition}\n"

    # Fallback: add framework suggestion if none found
    if "Decision Tree" not in final_answer and "GROW" not in final_answer:
        final_answer += "\n🧠 *Tip: This decision may benefit from using a Decision Tree or the GROW coaching model to evaluate options.*\n"

    return final_answer.strip()
