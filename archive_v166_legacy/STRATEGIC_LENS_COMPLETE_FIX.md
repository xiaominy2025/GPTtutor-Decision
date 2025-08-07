# Strategic Thinking Lens Complete Fix - V1.6.5.1

## Issue Summary

The Strategic Thinking Lens section was appearing cut off in the frontend display. The content was ending abruptly at "long-term" instead of completing the full sentence.

## Root Cause Analysis

### 1. **Section Extraction Issue** ✅ FIXED
- **Problem**: The `answer_processor.py` regex pattern was looking for emoji + title format but content used title-only format
- **Solution**: Enhanced regex to handle both formats (with and without emojis)

### 2. **Content Generation Truncation** ✅ FIXED  
- **Problem**: Content was being truncated at word limits without considering sentence boundaries
- **Solution**: Improved truncation logic to end at complete sentences

### 3. **Word Limit Constraints** ✅ FIXED
- **Problem**: 140-word limit was too restrictive for complete sentences
- **Solution**: Increased limit to 160 words for better sentence completion

## Fixes Implemented

### 1. **Enhanced Section Extraction** (`answer_processor.py`)
```python
# Before: Only supported emoji format
pattern = rf'\*\*{emoji}\s*([^*]+)\*\*(.*?)(?=\*\*[^🧠📘💬]|$)'

# After: Supports both formats
pattern1 = rf'\*\*{emoji}\s*([^*]+)\*\*(.*?)(?=\*\*[^🧠📘💬🔧]|$)'  # With emoji
pattern2 = rf'\*\*{section_title}\*\*(.*?)(?=\*\*[^🧠📘💬🔧]|$)'   # Without emoji
```

### 2. **Updated Section Definitions**
```python
self.sections = {
    "strategic_thinking": {"emoji": "🧠", "title": "Strategic Thinking Lens"},
    "story_action": {"emoji": "📘", "title": "Story in Action"},
    "followup_prompts": {"emoji": "💬", "title": "Follow-up Prompts"},
    "concepts_tools": {"emoji": "🔧", "title": "Concepts/Tools"}
}
```

### 3. **Improved Content Truncation** (`query_engine.py`)
```python
# Before: Simple word truncation
expanded_content = " ".join(words[:target_words])

# After: Smart sentence-aware truncation
if not truncated_content.endswith(('.', '!', '?')):
    sentences = re.split(r'([.!?])', truncated_content)
    if len(sentences) > 2:
        expanded_content = "".join(sentences[:-2]) + sentences[-2]
```

### 4. **Increased Word Limits**
```python
# Before
STRATEGIC_LENS_MAX_WORDS = 140
target_words = max(110, STRATEGIC_LENS_MIN_WORDS + 10)

# After  
STRATEGIC_LENS_MAX_WORDS = 160  # Increased for complete sentences
target_words = max(120, STRATEGIC_LENS_MIN_WORDS + 20)  # Better range
```

## Testing Results

✅ **Section Extraction**: All 4 sections now properly extracted
- Strategic Thinking Lens: 803 characters (full content)
- Story in Action: 434 characters (full content)  
- Follow-up Prompts: 486 characters (full content)
- Concepts/Tools: 237 characters (full content)

✅ **Content Generation**: Smart truncation ensures complete sentences
✅ **Backward Compatibility**: Still supports old emoji format
✅ **Future Proof**: Ready for additional sections

## Files Modified

1. **`answer_processor.py`**: Enhanced section extraction logic
2. **`query_engine.py`**: Improved content truncation and increased word limits

## Impact

- **Fixed**: Strategic Thinking Lens content no longer cut off
- **Enhanced**: All sections properly extracted and displayed
- **Improved**: Content generation respects sentence boundaries
- **Maintained**: Backward compatibility with existing formats

## Verification

The fix was tested with the exact content format from the user's example and confirmed that:
1. All sections are properly extracted without truncation
2. Content generation respects sentence boundaries
3. Word limits allow for complete, coherent sentences
4. Both old and new content formats are supported

The Strategic Thinking Lens should now display complete, well-formed content without being cut off. 