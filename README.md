# Engent Labs Backend V1.6.4

## 🚀 Overview

Engent Labs is a modular, maintainable decision-making tutor that synthesizes answers from course materials and supplements with GPT knowledge. Version 1.6.4 introduces **multi-course support** with dynamic configuration loading, enabling the platform to serve multiple academic disciplines with course-specific content and prompts.

## 🆕 V1.6.4 Features

### ✅ Multi-Course Support
- **Dynamic Course Loading**: Automatically loads course-specific configurations from `/courses/{course_id}/`
- **Fallback Mechanism**: Gracefully falls back to "decision" course if course_id is missing or invalid
- **Course-Specific Content**: Each course has its own glossary, prompt templates, and section configurations

### ✅ Enhanced API Endpoints
- **Course Management**: New endpoints for listing courses and retrieving course configurations
- **Error Handling**: Robust error handling with informative fallback messages
- **Version Information**: Health check now includes version information

### ✅ Modular Architecture
- **Course Configuration**: Centralized course management with JSON-based configuration
- **Dynamic Prompt Templates**: Course-specific prompts that adapt to different academic disciplines
- **Flexible Glossary System**: Each course maintains its own concept definitions and aliases

## 📁 Folder Structure

```
GPTTutor-Decision/
├── api_server.py                    # Flask API server with multi-course support
├── query_engine.py                  # Main query engine with course configuration
├── config.py                        # Configuration management
├── courses/                         # Multi-course directory
│   ├── decision/                    # Decision-making course
│   │   ├── glossary.json           # Course-specific concept definitions
│   │   ├── prompt_template.txt     # Course-specific prompt template
│   │   └── sections_config.json    # Course-specific section requirements
│   └── marketing/                   # Marketing course (example)
│       ├── glossary.json           # Marketing concept definitions
│       ├── prompt_template.txt     # Marketing-specific prompts
│       └── sections_config.json    # Marketing section requirements
├── services/                        # Service modules
├── tests/                          # Test suites
└── docs/                           # Documentation
```

## 🔧 How to Add a New Course

### 1. Create Course Directory
```bash
mkdir courses/your_course_name
```

### 2. Create Course Configuration Files

#### `glossary.json` - Course-Specific Concepts
```json
{
  "concept_name": {
    "definition": "Clear definition of the concept",
    "core": true,
    "aliases": ["synonym1", "synonym2", "alternative_name"]
  }
}
```

#### `prompt_template.txt` - Course-Specific Prompts
Create a prompt template that:
- Defines the AI's role for your course
- Specifies the required answer structure
- Includes course-specific guidance and examples

#### `sections_config.json` - Section Requirements
```json
{
  "sections": {
    "section_name": {
      "title": "Section Title",
      "required": true,
      "max_words": 300,
      "description": "Section description"
    }
  },
  "fallback_concepts": ["Concept1", "Concept2", "Concept3"]
}
```

### 3. Test Your Course
```bash
# Test with course_id parameter
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question", "course_id": "your_course_name"}'
```

## 📋 API Endpoints

### Core Endpoints
- `GET /health` - Health check with version information
- `POST /query` - Process queries with course support
- `GET /courses` - List available courses
- `GET /courses/{course_id}/config` - Get course configuration

### Query Processing
```json
POST /query
{
  "query": "Your question here",
  "course_id": "decision",  // Optional, defaults to "decision"
  "user_id": "optional_user_id"
}
```

### Response Format
```json
{
  "status": "success",
  "data": {
    "answer": "Structured response with tooltips",
    "query": "Original query",
    "course_id": "decision",
    "timestamp": "2024-01-01T12:00:00Z",
    "model": "gpt-3.5-turbo",
    "processing_time": 2.3,
    "conceptsToolsPractice": [
      {
        "term": "Concept Name",
        "definition": "Concept definition"
      }
    ]
  }
}
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Set Environment Variables
Create `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.3
```

### 3. Run the API Server
```bash
python api_server.py
```

### 4. Test Multi-Course Support
```bash
# Test decision course
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I make a decision under uncertainty?", "course_id": "decision"}'

# Test marketing course
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I segment my target market?", "course_id": "marketing"}'

# List available courses
curl http://localhost:5000/courses
```

## 🔄 Course Configuration Details

### Glossary Structure
Each course's `glossary.json` contains:
- **Concept definitions**: Clear, concise explanations
- **Core flags**: Mark essential concepts for priority selection
- **Aliases**: Synonyms and alternative terms for better matching

### Prompt Template Requirements
- **Role definition**: How the AI should behave for this course
- **Structure specification**: Required answer format
- **Course-specific guidance**: Examples and domain-specific instructions

### Section Configuration
- **Required sections**: Which parts of the answer are mandatory
- **Content limits**: Word counts, paragraph limits, etc.
- **Formatting rules**: Markdown requirements, tone guidelines

## 🛠️ Error Handling

### Course Loading
- **Missing course_id**: Falls back to "decision" course
- **Invalid course_id**: Logs warning and uses default
- **Missing files**: Gracefully handles missing configuration files

### API Responses
- **400 Bad Request**: Missing required fields
- **500 Internal Server Error**: Server-side processing errors
- **Informative messages**: Clear error descriptions for debugging

## 📊 Course Management

### Adding New Courses
1. Create course directory: `courses/new_course/`
2. Add required files: `glossary.json`, `prompt_template.txt`, `sections_config.json`
3. Test with API calls
4. Update documentation

### Course Validation
- **Glossary validation**: Ensures proper JSON structure
- **Prompt validation**: Checks for required sections
- **Configuration validation**: Verifies section requirements

## 🔍 Frontend Integration

### Course Selection
Frontend can:
- List available courses via `/courses` endpoint
- Allow users to select preferred course
- Pass `course_id` in query requests
- Display course-specific content and tooltips

### Dynamic Content
- **Course-specific tooltips**: Loaded from course glossary
- **Adaptive prompts**: Course-specific AI behavior
- **Structured responses**: Course-appropriate answer formats

## 🧪 Testing

### Test Course Functionality
```bash
# Test course loading
python -c "
import api_server
config = api_server.load_course_config('decision')
print(f'Loaded course: {config[\"course_id\"]}')
print(f'Glossary entries: {len(config[\"glossary\"])}')
"
```

### Validate Course Structure
```bash
# Check course files exist
ls -la courses/decision/
ls -la courses/marketing/
```

## 📈 Performance Considerations

### Caching
- **Glossary caching**: Course glossaries are loaded once per session
- **Prompt caching**: Templates are cached for efficiency
- **Configuration caching**: Section configs are cached

### Memory Management
- **Lazy loading**: Course configs loaded only when needed
- **Efficient fallbacks**: Quick fallback to default course
- **Resource cleanup**: Proper cleanup of loaded configurations

## 🔮 Future Enhancements

### Planned Features
- **Course versioning**: Support for multiple versions of courses
- **Dynamic course updates**: Hot-reloading of course configurations
- **Course analytics**: Usage statistics per course
- **Course templates**: Pre-built course templates for common subjects

### Integration Opportunities
- **LMS integration**: Connect with learning management systems
- **Course marketplace**: Share and discover course configurations
- **Automated testing**: Course-specific test suites
- **Performance monitoring**: Course-specific performance metrics

## 📝 Version History

### V1.6.4 (Current)
- ✅ Multi-course support with dynamic loading
- ✅ Course-specific glossaries and prompts
- ✅ Robust error handling and fallbacks
- ✅ Enhanced API endpoints for course management
- ✅ Comprehensive documentation and examples

### Previous Versions
- V1.6.3: Enhanced concept extraction and semantic matching
- V1.6.2: Improved response structure and tooltip system
- V1.6.1: Initial modular architecture and API server

## 🤝 Contributing

### Adding New Courses
1. Follow the course creation guide above
2. Test thoroughly with various query types
3. Update documentation with course details
4. Submit pull request with course files

### Improving Existing Courses
1. Identify areas for improvement
2. Update glossary, prompts, or configuration
3. Test changes with sample queries
4. Document improvements

## 📞 Support

For questions about:
- **Course creation**: Follow the guide above
- **API usage**: Check the endpoint documentation
- **Configuration**: Review the JSON schema examples
- **Integration**: See the frontend integration section

---

**Engent Labs Backend V1.6.4** - Empowering multi-course learning with intelligent decision support. 