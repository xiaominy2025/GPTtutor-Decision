# Cost Control Guide

## Environment Variables for Model Configuration

Your GPTTutor now uses environment variables for model configuration, making it easy to control costs and experiment with different settings.

### Setup

1. **Create a `.env` file** in your project root:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_actual_api_key_here

# Model Configuration (for cost control)
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.3
```

2. **Copy the template** and replace `your_actual_api_key_here` with your real API key.

### Cost Control Options

#### **Ultra-Low Cost** (Recommended)
```bash
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.2
```
**Estimated cost**: ~$0.05-0.10 per month

#### **Balanced Cost/Quality**
```bash
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.3
```
**Estimated cost**: ~$0.10-0.20 per month

#### **Higher Quality** (More Expensive)
```bash
OPENAI_MODEL=gpt-4-turbo
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.4
```
**Estimated cost**: ~$2-5 per month

### Cost Comparison

| Model | Input Cost/1K tokens | Output Cost/1K tokens | Monthly Estimate |
|-------|---------------------|----------------------|------------------|
| gpt-3.5-turbo | $0.0015 | $0.002 | $0.05-0.20 |
| gpt-4-turbo | $0.01 | $0.03 | $2-5 |
| gpt-4 | $0.03 | $0.06 | $5-15 |

### Tips for Cost Optimization

1. **Start with gpt-3.5-turbo** - It's 10x cheaper and often sufficient
2. **Lower max_tokens** - Reduces output cost
3. **Use hybrid tooltips** - Prebuilt tooltips cost 0 tokens
4. **Monitor usage** - Check your OpenAI dashboard regularly
5. **Set billing alerts** - Configure spending limits in OpenAI dashboard

### Quick Model Switch

To temporarily try a different model, just change your `.env` file:
```bash
# For testing GPT-4
OPENAI_MODEL=gpt-4-turbo

# For ultra-fast responses
OPENAI_MODEL=gpt-3.5-turbo-0125

# For maximum cost savings
OPENAI_MAX_TOKENS=300
```

### Monitoring

The script now shows your model configuration on startup:
```
🤖 Using model: gpt-3.5-turbo
📊 Max tokens: 1000
🌡️ Temperature: 0.3
```

This helps you verify you're using the intended cost-effective settings. 