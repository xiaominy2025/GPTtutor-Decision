#!/usr/bin/env python3
"""
Clean V1.6.5 Query Engine - Removes all V1.6.6 streaming code
"""

import os
import sys

def clean_query_engine():
    """Remove V1.6.6 streaming code from query_engine.py"""
    
    print("🧹 Cleaning V1.6.5 query_engine.py...")
    
    # Read the current file
    with open("query_engine.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find the start of V1.6.6 streaming code
    streaming_start = None
    for i, line in enumerate(lines):
        if "# Import streaming support for V1.6.6" in line:
            streaming_start = i
            break
    
    if streaming_start is None:
        print("✅ No V1.6.6 streaming code found - file is already clean")
        return
    
    # Keep only the lines before V1.6.6 streaming code
    clean_lines = lines[:streaming_start]
    
    # Add the main execution block for V1.6.5
    clean_lines.append("\n")
    clean_lines.append("if __name__ == \"__main__\":\n")
    clean_lines.append("    if \"--test-suite\" in sys.argv:\n")
    clean_lines.append("        run_test_cases()\n")
    clean_lines.append("\n")
    clean_lines.append("# Main execution\n")
    clean_lines.append("if __name__ == \"__main__\":\n")
    clean_lines.append("    try:\n")
    clean_lines.append("        # Check if test mode is requested\n")
    clean_lines.append("        if len(sys.argv) > 1 and sys.argv[1] == \"--test\":\n")
    clean_lines.append("            # Test mode - run automated tests\n")
    clean_lines.append("            test_questions = [\n")
    clean_lines.append("                \"I've been offered a strategic HQ role but must leave a city I love.\",\n")
    clean_lines.append("                \"My mentor offered me funding for grad school, but I'm unsure I want to go.\"\n")
    clean_lines.append("            ]\n")
    clean_lines.append("            run_test_mode(test_questions)\n")
    clean_lines.append("            sys.exit(0)\n")
    clean_lines.append("        else:\n")
    clean_lines.append("            # Interactive mode\n")
    clean_lines.append("            while True:\n")
    clean_lines.append("                try:\n")
    clean_lines.append("                    query = input(\"\\nAsk a question (or type 'exit'): \")\n")
    clean_lines.append("                except (EOFError, KeyboardInterrupt):\n")
    clean_lines.append("                    print(\"\\n👋 Exiting. Goodbye!\")\n")
    clean_lines.append("                    break\n")
    clean_lines.append("                \n")
    clean_lines.append("                if query.strip().lower() == \"exit\":\n")
    clean_lines.append("                    print(\"👋 Exiting. Goodbye!\")\n")
    clean_lines.append("                    break\n")
    clean_lines.append("                \n")
    clean_lines.append("                if not query.strip():\n")
    clean_lines.append("                    print(\"⚠️ Please enter a non-empty question.\")\n")
    clean_lines.append("                    continue\n")
    clean_lines.append("                \n")
    clean_lines.append("                answer = process_query(query)\n")
    clean_lines.append("                print(f\"{answer}\")\n")
    clean_lines.append("                \n")
    clean_lines.append("    except KeyboardInterrupt:\n")
    clean_lines.append("        print(\"\\n👋 Exiting. Goodbye!\") \n")
    
    # Write the cleaned file
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.writelines(clean_lines)
    
    # Count lines removed
    original_lines = len(lines)
    cleaned_lines = len(clean_lines)
    removed_lines = original_lines - cleaned_lines
    
    print(f"✅ Cleaned query_engine.py")
    print(f"📊 Removed {removed_lines} lines of V1.6.6 streaming code")
    print(f"📊 File size reduced from {original_lines} to {cleaned_lines} lines")
    
    return removed_lines

def main():
    """Main cleaning function"""
    print("🚀 V1.6.5 QUERY ENGINE CLEANUP")
    print("=" * 50)
    
    try:
        removed_lines = clean_query_engine()
        
        if removed_lines > 0:
            print(f"\n🎉 SUCCESS: Removed {removed_lines} lines of V1.6.6 code")
            print("✅ query_engine.py is now clean V1.6.5")
            print("⚡ Performance should be much better now!")
        else:
            print("\n✅ File was already clean")
            
    except Exception as e:
        print(f"❌ Error cleaning file: {e}")

if __name__ == "__main__":
    main() 