from query_engine import format_final_output

# Test the formatting function with a sample response
test_response = """**How to Strategize Your Decision**: The decision type here is dealing with uncertainty in tariffs and its impact on production planning.

**Story in Action**: individual, the production manager of a manufacturing company, is faced with the task of planning production for the upcoming year amidst uncertainty surrounding tariffs.

**Reflection Prompts**:
1. How can individual gather information and stay updated on the latest developments regarding tariffs to make informed production decisions?
2. What contingency plans can individual put in place to mitigate the risks associated with tariff uncertainty and ensure smooth production operations?

**Concepts/Tools/Practice Reference**:
- **Tariff Uncertainty**: Uncertainty surrounding changes in tariffs can impact production costs and market competitiveness.
- **Contingency Planning**: Developing alternative strategies to address potential risks and uncertainties in production planning."""

formatted = format_final_output(test_response)
print("=== FORMATTED OUTPUT ===")
print(formatted)
print("=== END FORMATTED OUTPUT ===") 