#!/usr/bin/env python3
"""
Direct alignment of course glossary with query engine concepts
"""
import json

def create_aligned_glossary():
    """Create a complete glossary aligned with query_engine.py"""
    
    # This is the complete glossary from query_engine.py
    aligned_glossary = {
        "strategic framing": {
            "definition": "Structuring the decision problem to clarify objectives and alternatives",
            "core": True,
            "aliases": ["strategic analysis", "problem framing", "decision framing"]
        },
        "stakeholder alignment": {
            "definition": "Ensuring all parties' interests are considered and balanced",
            "core": True,
            "aliases": ["stakeholder management", "stakeholder engagement", "alignment"]
        },
        "risk assessment": {
            "definition": "Systematic evaluation of potential threats and their impact on decision outcomes",
            "core": True,
            "aliases": ["risk evaluation", "risk analysis", "threat assessment"]
        },
        "scenario planning": {
            "definition": "Exploring different future possibilities to prepare for uncertainty",
            "core": True,
            "aliases": ["scenario analysis", "future planning", "uncertainty planning"]
        },
        "scenario analysis": {
            "definition": "A modeling approach that explores different future possibilities and outcomes to prepare for uncertainty in decision-making",
            "core": True,
            "aliases": ["scenario planning", "model uncertainty", "uncertainty modeling"]
        },
        "contingency planning": {
            "definition": "Developing backup strategies to prepare for uncertainty",
            "core": False,
            "aliases": ["backup planning", "emergency planning", "fallback strategies"]
        },
        "cost-benefit analysis": {
            "definition": "Comparing the advantages and disadvantages of different options",
            "core": True,
            "aliases": ["cost benefit", "compare alternatives", "trade-off analysis", "benefit cost analysis"]
        },
        "decision tree": {
            "definition": "A visual tool that maps out different options and their potential outcomes",
            "core": True,
            "aliases": ["decision mapping", "option tree", "outcome mapping"]
        },
        "swot analysis": {
            "definition": "A framework that helps identify strengths, weaknesses, opportunities, and threats",
            "core": True,
            "aliases": ["swot", "strengths weaknesses", "opportunities threats"]
        },
        "monte carlo simulation": {
            "definition": "A statistical tool that uses random sampling to simulate thousands of potential outcomes under uncertainty",
            "core": True,
            "aliases": ["monte carlo", "simulation modeling", "probabilistic modeling"]
        },
        "sensitivity analysis": {
            "definition": "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions",
            "core": True,
            "aliases": ["what-if analysis", "parameter analysis", "impact analysis"]
        },
        "expected value": {
            "definition": "A calculation that combines possible outcomes and their probabilities to determine the average result of uncertain scenarios",
            "core": True,
            "aliases": ["ev", "expected outcome", "probability-weighted outcome"]
        },
        "bounded rationality": {
            "definition": "The recognition that good decisions don't require perfect information",
            "core": True,
            "aliases": ["limited rationality", "satisficing", "cognitive limits"]
        },
        "cognitive behaviors": {
            "definition": "Patterns of thinking and perception that influence decision-making, often studied to improve judgment and reduce bias",
            "core": True,
            "aliases": ["cognitive patterns", "thinking patterns", "mental models"]
        },
        "judgment intuitive bias": {
            "definition": "Systematic errors in thinking that affect decisions and judgments, often unconsciously",
            "core": True,
            "aliases": ["cognitive bias", "judgment bias", "intuitive errors"]
        },
        "negotiation strategy": {
            "definition": "A systematic approach to achieving favorable outcomes in discussions and agreements",
            "core": True,
            "aliases": ["negotiation planning", "deal strategy", "bargaining approach"]
        },
        "batna": {
            "definition": "Best Alternative To a Negotiated Agreement - your fallback option if negotiations fail",
            "core": True,
            "aliases": ["best alternative", "fallback option", "walk-away point"]
        },
        "reservation point": {
            "definition": "The minimum acceptable outcome in a negotiation",
            "core": True,
            "aliases": ["walk-away point", "minimum acceptable", "bottom line"]
        },
        "zopa": {
            "definition": "Zone of Possible Agreement - the range where both parties can reach a mutually acceptable deal",
            "core": True,
            "aliases": ["zone of agreement", "mutual agreement range", "overlapping interests"]
        },
        "competitive advantage analysis": {
            "definition": "A strategic evaluation of factors that allow an organization to outperform its competitors",
            "core": True,
            "aliases": ["competitive advantage", "competitive analysis", "advantage analysis"]
        },
        "value chain analysis": {
            "definition": "A process of analyzing the activities that add value to a product or service from conception to delivery",
            "core": True,
            "aliases": ["value chain", "chain analysis", "value analysis", "activity-based analysis", "value creation activities", "value activities", "chain of activities"]
        },
        "investigative negotiation": {
            "definition": "A negotiation approach that focuses on uncovering underlying interests and information to create mutually beneficial outcomes",
            "core": True,
            "aliases": ["investigative", "interest-based negotiation", "information gathering", "uncover interests", "underlying interests", "investigative negotiation"]
        },
        "seasonal analysis": {
            "definition": "A forecasting method that identifies and models repeating patterns or cycles in time series data",
            "core": False,
            "aliases": ["seasonal patterns", "seasonality", "cyclical analysis", "seasonality modeling", "repeating patterns", "cycles", "seasonal forecasting", "cyclical patterns", "seasonal"]
        },
        "regression": {
            "definition": "A statistical technique for estimating relationships among variables and predicting future values based on historical data",
            "core": True,
            "aliases": ["regression analysis", "statistical regression", "prediction model", "forecast", "historical", "trends", "future values", "predict based on history", "statistical prediction", "forecasting"]
        },
        "moving average": {
            "definition": "A method that smooths time series data by averaging values over a specified number of periods to identify trends",
            "core": False,
            "aliases": ["moving averages", "trend smoothing", "time series smoothing"]
        },
        "semi-quantitative forecast": {
            "definition": "A forecasting approach that combines qualitative judgment with quantitative data for more robust predictions",
            "core": False,
            "aliases": ["semi quantitative", "mixed forecasting", "qualitative quantitative"]
        },
        "profitability analysis": {
            "definition": "An assessment of the ability of a project or business to generate earnings compared to its costs and expenses",
            "core": True,
            "aliases": ["profitability", "earnings analysis", "financial performance"]
        },
        "prospect theory": {
            "definition": "Shows how people often value avoiding losses more than achieving gains",
            "core": True,
            "aliases": ["prospect", "loss aversion", "gain loss"]
        },
        "solver-based simulation": {
            "definition": "A computational approach that uses algorithms to find optimal or feasible solutions under constraints and uncertainty",
            "core": True,
            "aliases": ["solver simulation", "algorithmic optimization", "computational optimization"]
        },
        "confirmation bias": {
            "definition": "Favoring evidence that supports existing beliefs",
            "core": True,
            "aliases": ["selective evidence bias", "favor confirming information", "seek confirming evidence", "ignore contradicting", "favor existing beliefs", "confirm beliefs", "favor confirming"]
        },
        "anchoring bias": {
            "definition": "Relying too heavily on initial information",
            "core": True,
            "aliases": ["initial value bias", "rely on first information", "first piece of information", "anchor on initial", "stick to first impression", "initial reference point", "first information"]
        },
        "framing bias": {
            "definition": "Decisions shaped by how options are presented",
            "core": True,
            "aliases": ["context framing"]
        },
        "representative heuristic": {
            "definition": "Judging probability based on similarity",
            "core": True,
            "aliases": ["representativeness bias", "judge by similarity", "similar to past", "based on similarity", "judge probability by similarity"]
        },
        "endowment effect": {
            "definition": "Valuing owned items higher than market value",
            "core": True,
            "aliases": ["ownership bias", "value own work higher", "overvalue own", "my work is worth more", "value my creation higher", "own work more valuable", "personal attachment", "value own"]
        },
        "status quo bias": {
            "definition": "Preference for maintaining the current state",
            "core": True,
            "aliases": ["resistance to change", "status quo", "maintaining current", "not want to give up", "reluctant to change", "prefer current", "refuse to change", "stick with current", "keep current", "don't want to change", "prefer existing", "stick to current"]
        },
        "escalation of commitment": {
            "definition": "Continuing investment in failing endeavors",
            "core": True,
            "aliases": ["sunk cost fallacy", "legacy project", "continuing investment", "failing project", "persistent investment", "keep investing", "already spent", "time investment", "continue despite failure", "invest more in failing", "keep going despite problems", "legacy"]
        },
        "mental accounting": {
            "definition": "Treating money differently depending on its source",
            "core": True,
            "aliases": ["psychological budgeting"]
        },
        "game theory": {
            "definition": "Strategic analysis of competitive interactions",
            "core": True,
            "aliases": ["strategic games", "payoff analysis", "competitive interactions", "strategic analysis", "competitive strategy", "strategic thinking", "competitive analysis", "strategic interactions", "game theory"]
        },
        "winner's curse": {
            "definition": "Overpaying or overcommitting in competitive bidding",
            "core": True,
            "aliases": ["overpaying", "competitive bidding", "overcommitting", "bidding war", "auction", "competitive situation", "overbid", "competitive overpayment", "winner's curse"]
        },
        "integrative negotiation": {
            "definition": "Win-win bargaining through value creation",
            "core": True,
            "aliases": ["collaborative negotiation", "win-win bargaining", "value creation", "mutual benefits", "win-win solutions", "create value", "collaborative approach", "mutual gains", "win-win"]
        },
        "distributive negotiation": {
            "definition": "Zero-sum bargaining where one's gain is another's loss",
            "core": False,
            "aliases": []
        },
        "porter's five forces": {
            "definition": "Framework for analyzing industry competitiveness",
            "core": True,
            "aliases": ["five forces analysis", "competitive", "industry", "competitiveness", "industry analysis", "competitive forces", "industry structure", "competitive analysis", "five forces"]
        },
        "cost leadership": {
            "definition": "Achieving competitive edge by offering the lowest cost",
            "core": True,
            "aliases": ["low-cost strategy", "competitive edge", "lowest cost", "cost advantage", "price leadership", "low cost advantage", "cost competitive", "lowest price strategy", "low cost"]
        },
        "differentiation strategy": {
            "definition": "Gaining advantage by offering unique features valued by customers",
            "core": True,
            "aliases": ["uniqueness strategy", "unique features", "differentiate", "product differentiation", "competitive advantage", "unique value", "stand out", "distinctive features", "differentiation"]
        },
        "portfolio management": {
            "definition": "Balancing business units and investments",
            "core": True,
            "aliases": ["strategic portfolio management", "business units", "balance portfolio", "investment portfolio", "manage portfolio", "portfolio balance", "business unit management", "portfolio"]
        },
        "qualitative forecasting": {
            "definition": "Judgment-based prediction methods",
            "core": True,
            "aliases": []
        },
        "regression forecasting": {
            "definition": "Using statistical models for long-term predictions",
            "core": True,
            "aliases": ["regression analysis"]
        },
        "seasonal forecasting": {
            "definition": "Accounting for repeating seasonal patterns",
            "core": True,
            "aliases": ["seasonality modeling"]
        },
        "integer optimization": {
            "definition": "Solving LP problems with discrete choices",
            "core": True,
            "aliases": ["discrete optimization", "integer programming", "discrete choices", "whole number optimization", "discrete variables", "integer variables", "discrete decision making", "discrete"]
        },
        "aggregate planning": {
            "definition": "Balancing supply and demand through optimization",
            "core": True,
            "aliases": ["demand-driven optimization", "balance supply demand", "supply demand", "aggregate planning", "demand planning", "supply planning"]
        },
        "analytical solver": {
            "definition": "Tool for implementing optimization models",
            "core": True,
            "aliases": ["solver add-on", "optimization tool", "solver tool", "analytical solver"]
        },
        "integrated optimization & simulation": {
            "definition": "Combining LP and simulation for robust planning",
            "core": False,
            "aliases": []
        },
        "automated simulation models": {
            "definition": "Tools that streamline repetitive decision simulations",
            "core": False,
            "aliases": []
        },
        "supply chain risk management": {
            "definition": "Identifying and mitigating risks in supply chain operations",
            "core": True,
            "aliases": ["supply chain risk", "risk management", "supply chain"]
        },
        "utility functions": {
            "definition": "Mathematical representations of preferences used to evaluate and compare uncertain outcomes in decision analysis",
            "core": True,
            "aliases": ["utility", "preference functions", "value functions"]
        },
        "linear optimization": {
            "definition": "A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints",
            "core": True,
            "aliases": ["linear programming", "optimization", "mathematical programming"]
        },
        "value creation": {
            "definition": "The process of generating benefits that exceed the costs for stakeholders in a decision or transaction",
            "core": True,
            "aliases": ["value generation", "benefit creation", "stakeholder value"]
        },
        "risk tolerance assessment": {
            "definition": "An evaluation of an individual's or organization's willingness to accept risk in pursuit of objectives",
            "core": True,
            "aliases": ["risk appetite", "risk preference", "risk capacity"]
        },
        "leadership assessment": {
            "definition": "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts",
            "core": True,
            "aliases": ["leadership evaluation", "management assessment", "leadership style"]
        },
        "human-computer integration": {
            "definition": "The collaboration between humans and computer systems to enhance decision-making and problem-solving capabilities",
            "core": True,
            "aliases": ["human-ai collaboration", "augmented decision-making", "human-machine partnership"]
        },
        "negotiation term sheet": {
            "definition": "A document outlining the key terms and conditions of a negotiation or agreement before final contracts are drafted",
            "core": True,
            "aliases": ["term sheet", "agreement outline", "deal terms"]
        }
    }
    
    # Save the complete aligned glossary
    output_file = 'courses/decision/glossary.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aligned_glossary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Complete aligned glossary saved to: {output_file}")
    print(f"   Total concepts: {len(aligned_glossary)}")
    
    return aligned_glossary

if __name__ == "__main__":
    create_aligned_glossary() 