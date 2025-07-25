# Backend Consistency Guarantee & Next Steps

## ✅ Consistency Guarantee
- The backend **always** returns `conceptsToolsPractice` as an array of `{ term, definition }` objects for every query.
- If no concepts are found, the array is empty (`[]`).
- No strings, null, undefined, or malformed entries will ever be returned.
- Any invalid entries are filtered and logged on the backend for debugging.

## 🚦 Next Steps for Frontend
- You can now safely iterate and render `conceptsToolsPractice` for all queries, with no need for defensive checks against strings or missing fields.
- Proceed with UI testing and integration.
- Implement user-facing error handling for empty arrays (e.g., show "No concepts/tools for this query" if desired).
- If you encounter any edge cases, missing data, or integration issues, notify the backend team for rapid support and fixes.

---

# GPTTutor Frontend API Integration Guide

## API Endpoint

**POST** `http://localhost:5000/query`

### Request Body
```json
{
  "query": "How should I prioritize tasks when under tight deadlines?"
}
```

---

## API Response Structure

```json
{
  "status": "success",
  "data": {
    "answer": "...",  // markdown answer
    "query": "...",
    "timestamp": "...",
    "model": "gpt-3.5-turbo",
    "processing_time": 2.3,
    "conceptsToolsPractice": [
      { "term": "Decision Tree", "definition": "A visual tool that maps out different options and their potential outcomes." },
      { "term": "SWOT Analysis", "definition": "A framework that helps identify strengths, weaknesses, opportunities, and threats." }
    ]
  }
}
```

---

## TypeScript Interface

```typescript
export interface ConceptTool {
  term: string;
  definition: string;
}

export interface GPTutorApiResponse {
  status: string;
  data: {
    answer: string;
    query: string;
    timestamp: string;
    model: string;
    processing_time: number;
    conceptsToolsPractice: ConceptTool[];
  };
}
```

---

## Rendering Example (React)

```tsx
import React from 'react';
import { ConceptTool, GPTutorApiResponse } from './types';

interface Props {
  response: GPTutorApiResponse;
}

export const ConceptsToolsSection: React.FC<Props> = ({ response }) => {
  const concepts = response.data.conceptsToolsPractice;
  if (!concepts || concepts.length === 0) return null;
  return (
    <section>
      <h2>Concepts / Tools / Practice Reference</h2>
      <ul>
        {concepts.map((item, idx) => (
          <li key={idx}>
            <strong>{item.term}:</strong> {item.definition}
          </li>
        ))}
      </ul>
    </section>
  );
};
```

---

## Notes
- The `conceptsToolsPractice` field is always an array of objects with `term` and `definition`.
- No tooltip parsing or HTML extraction is needed—just render as shown above.
- The `answer` field contains the full markdown-formatted answer for the main response area.

---

For any questions or further integration help, contact the backend team or your AI assistant! 