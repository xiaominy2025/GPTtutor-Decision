# V1.6.6 Step 2 Testing Framework

## Overview

This testing framework validates the Step 2 refinements for V1.6.6, focusing on adaptive word count compliance, connector variety, and smooth flow in the new 3-section answer format.

## 🎯 Testing Goals

### Primary Objectives
1. **Adaptive Word Count Compliance**
   - ~100 words for 1 domain
   - ~125 words for 2 domains  
   - ~140-150 words for 3 domains

2. **Connector Variety Validation**
   - At least 2 different connectors across test suite
   - No single connector exceeds 60% of total use
   - Smooth transitions between reasoning and examples

3. **Smooth Flow Validation**
   - Reasoning + example in new paragraph with proper connector
   - No duplication between reasoning and story
   - Multiple paragraphs in Strategic Thinking Lens

4. **Performance Monitoring**
   - Average response time < 8 seconds
   - Token usage tracking
   - Fallback frequency < 5%

5. **Regression Testing**
   - Follow-up Prompts and Concepts/Tools sections remain accurate
   - No breaking changes from Step 1

## 🔧 Test Categories

### 1. Functional Tests
- **18 queries minimum**: 6 each for 1, 2, and 3 domains
- **Lens merging validation**: Strategic Thinking Lens includes reasoning + example
- **Section structure**: All 3 sections present (Lens, Prompts, Concepts)
- **Story integration**: Story begins in new paragraph with connector

### 2. Length Compliance Tests
- **Word count measurement**: Accurate counting excluding markdown
- **Domain-based targets**: 
  - 1 domain: 90-120 words
  - 2 domains: 115-135 words
  - 3 domains: 135-150 words
- **Compliance tracking**: Percentage of responses meeting targets

### 3. Connector Variety Tests
- **Connector detection**: 10+ connector types monitored
- **Variety validation**: At least 2 different connectors used
- **Usage distribution**: No single connector > 60%
- **Flow assessment**: Natural transitions between sections

### 4. Quality Checks
- **Duplication detection**: Similarity analysis between reasoning and story
- **Flow assessment**: Smooth progression from reasoning to example
- **Paragraph structure**: Multiple paragraphs in Lens section
- **Content relevance**: Domain-appropriate examples and concepts

### 5. Fallback Simulation
- **GPT-3.5 failure simulation**: Tests fallback join functionality
- **Fallback validation**: 
  - New paragraph story creation
  - Connector addition if missing
  - Content within length tolerance
- **Error handling**: Graceful degradation under failure conditions

### 6. Performance Monitoring
- **Response time tracking**: Target < 8 seconds average
- **Token usage monitoring**: Per-query token consumption
- **Fallback rate tracking**: Target < 5% fallback frequency
- **Throughput analysis**: Words per second metrics

## 📦 Test Files

### Core Test Suite
- `tests/test_v166_step2_refinements.py`: Main test suite with comprehensive validation
- `run_v166_step2_tests.py`: Test runner with reporting and analysis

### Test Data
- **1 Domain Queries**: 6 test cases for single-domain decisions
- **2 Domain Queries**: 6 test cases for dual-domain decisions  
- **3 Domain Queries**: 6 test cases for multi-domain decisions

### Sample Test Queries

#### 1 Domain Examples
```
"I need to decide between two job offers with different salaries"
"How do I choose the best investment option?"
"What should I consider when buying a house?"
```

#### 2 Domain Examples
```
"I need to decide between a high-paying job in finance and a lower-paying job in tech that I enjoy more"
"How do I balance financial security with personal fulfillment in my career choice?"
"Should I invest in stocks or real estate given my current financial situation?"
```

#### 3 Domain Examples
```
"I need to decide between a high-paying finance job, a tech startup with equity, or starting my own business"
"How do I balance financial security, personal fulfillment, and family responsibilities in my career?"
"Should I invest in stocks, real estate, or cryptocurrency given market uncertainty and my risk tolerance?"
```

## 🚀 Running the Tests

### Quick Start
```bash
# Run the complete test suite
python run_v166_step2_tests.py
```

### Individual Test Categories
```bash
# Run specific test categories
python -m pytest tests/test_v166_step2_refinements.py::TestV166Step2Refinements::test_adaptive_word_count_compliance -v
python -m pytest tests/test_v166_step2_refinements.py::TestV166Step2Refinements::test_connector_variety -v
python -m pytest tests/test_v166_step2_refinements.py::TestV166Step2Refinements::test_smooth_flow_and_structure -v
```

### Direct Test Suite Execution
```bash
# Run the test suite directly
python tests/test_v166_step2_refinements.py
```

## 📊 Test Results and Reports

### Generated Reports
1. **Detailed Test Report**: `v166_step2_test_report_YYYYMMDD_HHMMSS.json`
   - Raw test data and metrics
   - Individual query results
   - Performance measurements

2. **Summary Report**: `v166_step2_summary_YYYYMMDD_HHMMSS.json`
   - Aggregated metrics and scores
   - Pass/fail status for each category
   - Overall quality score

### Key Metrics Tracked

#### Word Count Compliance
- **1 Domain**: Target 90-120 words, 60%+ compliance required
- **2 Domains**: Target 115-135 words, 60%+ compliance required  
- **3 Domains**: Target 135-150 words, 60%+ compliance required

#### Connector Variety
- **Unique connectors**: Minimum 2 different types
- **Usage distribution**: No single connector > 60%
- **Flow quality**: Natural transitions validated

#### Flow Quality
- **Multiple paragraphs**: 80%+ responses should have multiple paragraphs
- **Connector presence**: 80%+ responses should have connectors
- **No duplication**: 70%+ responses should avoid duplication
- **All sections**: 90%+ responses should have all 3 sections

#### Performance
- **Response time**: Average < 8 seconds
- **Word count**: Average > 100 words
- **Fallback rate**: < 5% of queries

## 🎯 Success Criteria

### Excellent (80-100 points)
- All word count compliance targets met
- Connector variety requirements satisfied
- Flow quality metrics > 80%
- Performance targets achieved
- No regression issues

### Good (60-79 points)
- Most word count compliance targets met
- Connector variety mostly satisfied
- Flow quality metrics > 60%
- Performance mostly on target
- Minor regression issues

### Needs Improvement (< 60 points)
- Word count compliance below targets
- Connector variety issues
- Flow quality below thresholds
- Performance issues
- Significant regression problems

## 🔍 Test Methodology

### Adaptive Word Count Testing
1. **Domain Detection**: Analyze query complexity and domain count
2. **Target Calculation**: Apply domain-based word count targets
3. **Compliance Measurement**: Compare actual vs. target word counts
4. **Success Rate Calculation**: Percentage of compliant responses

### Connector Variety Testing
1. **Connector Detection**: Scan for 10+ connector types
2. **Usage Tracking**: Count frequency of each connector
3. **Distribution Analysis**: Calculate usage percentages
4. **Variety Validation**: Ensure minimum variety requirements

### Flow Quality Testing
1. **Structure Analysis**: Check for multiple paragraphs
2. **Connector Validation**: Verify connector presence
3. **Duplication Detection**: Analyze similarity between sections
4. **Section Completeness**: Ensure all required sections present

### Performance Testing
1. **Response Time Measurement**: Track API call duration
2. **Token Usage Monitoring**: Count tokens per query
3. **Fallback Rate Tracking**: Monitor fallback frequency
4. **Throughput Analysis**: Calculate words per second

## 🛠️ Customization

### Adding New Test Cases
```python
# Add to TEST_QUERIES_1_DOMAIN, TEST_QUERIES_2_DOMAINS, or TEST_QUERIES_3_DOMAINS
TEST_QUERIES_1_DOMAIN.append("Your new test query here")
```

### Modifying Test Criteria
```python
# Adjust word count targets
is_compliant = 85 <= word_count <= 125  # Custom range

# Modify connector variety requirements
assert unique_connectors >= 3, "Require 3+ connectors"
```

### Adding New Connectors
```python
# Add to detect_connectors method
connectors = [
    "For example,",
    "For instance,",
    "Consider,",
    "Your new connector,"  # Add here
    # ... existing connectors
]
```

## 📈 Monitoring and Maintenance

### Regular Testing Schedule
- **Daily**: Run quick validation tests
- **Weekly**: Full test suite execution
- **Monthly**: Comprehensive regression testing

### Performance Tracking
- Monitor response times over time
- Track token usage trends
- Analyze fallback frequency patterns

### Quality Metrics
- Word count compliance trends
- Connector variety evolution
- Flow quality improvements

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure dependencies are installed
pip install pytest openai sentence-transformers faiss spacy
```

#### API Key Issues
```bash
# Check environment variables
echo $OPENAI_API_KEY
```

#### Test Timeouts
```bash
# Increase timeout in run_v166_step2_tests.py
timeout=1200  # 20 minutes instead of 10
```

#### Memory Issues
```bash
# Reduce test batch size
for query in self.TEST_QUERIES_1_DOMAIN[:2]:  # Test fewer queries
```

### Debug Mode
```python
# Add debug output to test methods
print(f"DEBUG: Processing query: {query}")
print(f"DEBUG: Word count: {word_count}")
```

## 📋 Deliverables

### Required Outputs
1. **Test Report**: Comprehensive JSON report with all metrics
2. **Summary Report**: Aggregated analysis with pass/fail status
3. **Performance Metrics**: Response times, token usage, fallback rates
4. **Quality Scores**: Word count compliance, connector variety, flow quality
5. **Regression Analysis**: Comparison against V1.6.6 Step 1

### Success Metrics
- **Word Count Compliance**: 60%+ for each domain count
- **Connector Variety**: 2+ unique connectors, < 60% single usage
- **Flow Quality**: 80%+ multiple paragraphs, 80%+ connectors, 70%+ no duplication
- **Performance**: < 8s average response time, < 5% fallback rate
- **Regression**: All Step 1 functionality preserved

## 🎉 Conclusion

This testing framework provides comprehensive validation of V1.6.6 Step 2 refinements, ensuring that the adaptive word count, connector variety, and smooth flow requirements are met while maintaining performance and preventing regression issues.

The framework is designed to be:
- **Comprehensive**: Covers all key requirements
- **Automated**: Minimal manual intervention required
- **Scalable**: Easy to add new test cases
- **Maintainable**: Clear structure and documentation
- **Actionable**: Provides specific metrics and recommendations 