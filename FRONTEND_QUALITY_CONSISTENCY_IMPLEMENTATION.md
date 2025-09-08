# Frontend Implementation Guide: Lambda Quality Consistency

## Overview

The deployed v1666 backend experiences quality variations between first-run (cold start) and subsequent runs (warm start) due to **concept embeddings cache** behavior. This document provides frontend implementation strategies to handle this gracefully and improve user experience.

## Problem Analysis

### Root Cause
- **First Run (Cold Start)**: Lambda container starts fresh, `_concept_embeddings_cache = None`, embeddings generated from scratch
- **Subsequent Runs (Warm Start)**: Container warm, cache populated, high-quality responses
- **Result**: Inconsistent response quality (first: ~1500 chars, subsequent: ~4000+ chars)

### Technical Details
```python
# From query_engine.py - The caching mechanism causing the issue
_concept_embeddings_cache = None

if _concept_embeddings_cache is None:
    # Expensive operation - generates embeddings for all concepts
    _concept_embeddings_cache = get_openai_embeddings(concept_texts)
```

## Frontend Implementation Strategy

### 1. Smart Query Caching & Warm-up Strategy

#### QueryService Class
```typescript
// services/QueryService.ts
class QueryService {
  private static instance: QueryService;
  private isWarmedUp = false;
  private queryCache = new Map<string, QueryResponse>();
  private warmUpPromise: Promise<void> | null = null;

  static getInstance(): QueryService {
    if (!QueryService.instance) {
      QueryService.instance = new QueryService();
    }
    return QueryService.instance;
  }

  async query(query: string, courseId: string): Promise<QueryResponse> {
    // Ensure Lambda is warmed up
    if (!this.isWarmedUp) {
      await this.warmUpLambda();
    }

    // Check cache first
    const cacheKey = `${query}-${courseId}`;
    if (this.queryCache.has(cacheKey)) {
      return this.queryCache.get(cacheKey)!;
    }

    // Make actual query
    const response = await this.makeQuery(query, courseId);
    this.queryCache.set(cacheKey, response);
    return response;
  }

  private async warmUpLambda(): Promise<void> {
    // Prevent multiple simultaneous warm-up attempts
    if (this.warmUpPromise) {
      await this.warmUpPromise;
      return;
    }

    this.warmUpPromise = this.performWarmUp();
    await this.warmUpPromise;
  }

  private async performWarmUp(): Promise<void> {
    try {
      console.log("🔥 Warming up Lambda function...");
      
      // Send a simple warm-up query
      await this.makeQuery("What is strategic planning?", "decision");
      
      this.isWarmedUp = true;
      console.log("✅ Lambda warmed up successfully");
    } catch (error) {
      console.warn("⚠️ Lambda warm-up failed, proceeding anyway:", error);
      // Don't block user queries if warm-up fails
    } finally {
      this.warmUpPromise = null;
    }
  }

  private async makeQuery(query: string, courseId: string): Promise<QueryResponse> {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        course_id: courseId,
        user_id: 'default'
      })
    });

    if (!response.ok) {
      throw new Error(`Query failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // Clear cache when needed (e.g., after deployment)
  clearCache(): void {
    this.queryCache.clear();
    this.isWarmedUp = false;
  }
}

export default QueryService;
```

### 2. Progressive Loading with Quality Indicators

#### Quality Status Types
```typescript
// types/QualityTypes.ts
export type QualityStatus = 'loading' | 'low' | 'high' | 'consistent';

export interface QueryResponse {
  data: {
    answer: string;
    strategicThinkingLens: string;
    followUpPrompts: string[];
    conceptsToolsPractice: string;
  };
  status: string;
  version: string;
  timestamp: string;
}
```

#### Main Query Component
```tsx
// components/QueryComponent.tsx
import React, { useState, useCallback } from 'react';
import QueryInput from './QueryInput';
import QualityIndicator from './QualityIndicator';
import ResponseDisplay from './ResponseDisplay';
import { QueryResponse, QualityStatus } from '../types/QualityTypes';
import QueryService from '../services/QueryService';

const QueryComponent: React.FC = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [qualityIndicator, setQualityIndicator] = useState<QualityStatus>('loading');
  const [retryCount, setRetryCount] = useState(0);

  const queryService = QueryService.getInstance();

  const handleQuery = useCallback(async (queryText?: string) => {
    const queryToProcess = queryText || query;
    if (!queryToProcess.trim()) return;

    setIsLoading(true);
    setQualityIndicator('loading');
    
    try {
      const result = await queryService.query(queryToProcess, "decision");
      setResponse(result);
      
      // Analyze response quality
      const quality = analyzeResponseQuality(result);
      setQualityIndicator(quality);
      
      // If quality is low and this is the first attempt, show retry option
      if (quality === 'low' && retryCount === 0) {
        showQualityWarning();
      }
    } catch (error) {
      console.error('Query failed:', error);
      setQualityIndicator('low');
    } finally {
      setIsLoading(false);
    }
  }, [query, retryCount]);

  const handleRetry = useCallback(async () => {
    setRetryCount(prev => prev + 1);
    await handleQuery();
  }, [handleQuery]);

  const handleQuerySubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    handleQuery();
  }, [handleQuery]);

  return (
    <div className="query-container">
      {/* Query Input */}
      <QueryInput 
        value={query} 
        onChange={setQuery} 
        onSubmit={handleQuerySubmit}
        disabled={isLoading}
        placeholder="Ask about strategic decision-making..."
      />
      
      {/* Quality Indicator */}
      <QualityIndicator 
        status={qualityIndicator} 
        retryCount={retryCount}
      />
      
      {/* Response Display */}
      {response && (
        <ResponseDisplay 
          response={response}
          quality={qualityIndicator}
          retryCount={retryCount}
          onRetry={handleRetry}
        />
      )}
    </div>
  );
};

export default QueryComponent;
```

### 3. Quality Indicator Component

#### Quality Indicator with Helpful Messaging
```tsx
// components/QualityIndicator.tsx
import React from 'react';
import { QualityStatus } from '../types/QualityTypes';

interface QualityIndicatorProps {
  status: QualityStatus;
  retryCount: number;
}

const QualityIndicator: React.FC<QualityIndicatorProps> = ({ status, retryCount }) => {
  const getQualityMessage = () => {
    switch (status) {
      case 'loading':
        return { 
          text: 'Analyzing your query...', 
          color: 'blue', 
          icon: '🔄',
          className: 'quality-loading'
        };
      case 'low':
        return { 
          text: retryCount === 0 ? 'First response - warming up AI model' : 'Response quality improving...', 
          color: 'yellow', 
          icon: '⚠️',
          tip: retryCount === 0 ? 'Subsequent queries will be more detailed' : 'Keep trying for better quality',
          className: 'quality-warning'
        };
      case 'high':
        return { 
          text: 'High quality response', 
          color: 'green', 
          icon: '✅',
          className: 'quality-success'
        };
      case 'consistent':
        return { 
          text: 'Consistent quality achieved', 
          color: 'green', 
          icon: '🎯',
          className: 'quality-consistent'
        };
    }
  };

  const { text, color, icon, tip, className } = getQualityMessage();

  return (
    <div className={`quality-indicator ${className}`}>
      <div className="quality-header">
        <span className="icon">{icon}</span>
        <span className="text">{text}</span>
      </div>
      {tip && (
        <div className="quality-tip">
          <span className="tip-icon">💡</span>
          <span className="tip-text">{tip}</span>
        </div>
      )}
    </div>
  );
};

export default QualityIndicator;
```

### 4. Response Quality Analysis

#### Quality Analyzer Utility
```typescript
// utils/qualityAnalyzer.ts
import { QueryResponse, QualityStatus } from '../types/QualityTypes';

export const analyzeResponseQuality = (response: QueryResponse): QualityStatus => {
  const { answer, strategicThinkingLens, followUpPrompts } = response.data;
  
  // Calculate quality score based on multiple factors
  const answerLength = answer.length;
  const strategicLength = strategicThinkingLens.length;
  const promptCount = followUpPrompts.length;
  
  // Quality thresholds based on observed behavior
  const isHighQuality = answerLength > 2000 && strategicLength > 1000 && promptCount >= 3;
  const isLowQuality = answerLength < 1500 || strategicLength < 500;
  
  if (isHighQuality) return 'high';
  if (isLowQuality) return 'low';
  return 'consistent';
};

export const getQualityScore = (response: QueryResponse): number => {
  const { answer, strategicThinkingLens, followUpPrompts } = response.data;
  
  // Normalize scores to 0-100
  const answerScore = Math.min((answer.length / 3000) * 100, 100);
  const strategicScore = Math.min((strategicThinkingLens.length / 1500) * 100, 100);
  const promptScore = Math.min((followUpPrompts.length / 5) * 100, 100);
  
  // Weighted average
  return Math.round((answerScore * 0.4) + (strategicScore * 0.4) + (promptScore * 0.2));
};
```

### 5. Response Display with Retry Mechanism

#### Enhanced Response Display
```tsx
// components/ResponseDisplay.tsx
import React from 'react';
import { QueryResponse, QualityStatus } from '../types/QualityTypes';
import { getQualityScore } from '../utils/qualityAnalyzer';

interface ResponseDisplayProps {
  response: QueryResponse;
  quality: QualityStatus;
  retryCount: number;
  onRetry: () => void;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ 
  response, 
  quality, 
  retryCount, 
  onRetry 
}) => {
  const qualityScore = getQualityScore(response);
  const showRetryOption = quality === 'low' && retryCount < 2;

  return (
    <div className="response-container">
      {/* Quality warning for low-quality responses */}
      {showRetryOption && (
        <div className="quality-warning-banner">
          <div className="warning-header">
            <span className="icon">⚠️</span>
            <span className="title">Response Quality Notice</span>
          </div>
          <div className="warning-body">
            <p>This response was generated while the AI model was warming up.</p>
            <p><strong>Quality Score:</strong> {qualityScore}/100</p>
            <p><strong>Tip:</strong> Subsequent queries will provide more detailed and consistent answers.</p>
            <button 
              className="retry-button primary"
              onClick={onRetry}
              disabled={retryCount >= 2}
            >
              🔄 Retry Query for Better Quality
            </button>
            {retryCount >= 1 && (
              <p className="retry-note">
                <small>Retry attempts: {retryCount}/2</small>
              </p>
            )}
          </div>
        </div>
      )}
      
      {/* Quality score indicator */}
      <div className="quality-score">
        <div className="score-bar">
          <div 
            className="score-fill" 
            style={{ width: `${qualityScore}%` }}
          ></div>
        </div>
        <span className="score-text">Quality: {qualityScore}/100</span>
      </div>
      
      {/* Response content */}
      <div className="response-content">
        <div className="strategic-lens">
          <h3>Strategic Thinking Lens</h3>
          <div 
            className="content-text"
            dangerouslySetInnerHTML={{ __html: response.data.strategicThinkingLens }} 
          />
        </div>
        
        <div className="follow-up-prompts">
          <h3>Follow-up Prompts</h3>
          <ul className="prompts-list">
            {response.data.followUpPrompts.map((prompt, index) => (
              <li key={index} className="prompt-item">
                {prompt}
              </li>
            ))}
          </ul>
        </div>

        {response.data.conceptsToolsPractice && (
          <div className="concepts-tools">
            <h3>Concepts & Tools</h3>
            <div 
              className="content-text"
              dangerouslySetInnerHTML={{ __html: response.data.conceptsToolsPractice }} 
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponseDisplay;
```

### 6. Session-Based Warm-up Management

#### Session Manager
```typescript
// services/SessionManager.ts
class SessionManager {
  private static instance: SessionManager;
  private sessionId = crypto.randomUUID();
  private warmUpTimestamp: number | null = null;
  private warmUpInterval = 15 * 60 * 1000; // 15 minutes
  private isWarmingUp = false;

  static getInstance(): SessionManager {
    if (!SessionManager.instance) {
      SessionManager.instance = new SessionManager();
    }
    return SessionManager.instance;
  }

  async ensureWarmUp(): Promise<void> {
    const now = Date.now();
    
    // Check if we need to warm up
    if (!this.warmUpTimestamp || (now - this.warmUpTimestamp) > this.warmUpInterval) {
      await this.warmUpLambda();
      this.warmUpTimestamp = now;
    }
  }

  private async warmUpLambda(): Promise<void> {
    if (this.isWarmingUp) return; // Prevent multiple simultaneous warm-ups
    
    this.isWarmingUp = true;
    
    try {
      console.log("🔥 Warming up Lambda function...");
      
      // Send warm-up query
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: "What is strategic planning?",
          course_id: "decision",
          user_id: this.sessionId
        })
      });
      
      if (response.ok) {
        console.log("✅ Lambda warmed up for session");
      } else {
        throw new Error(`Warm-up failed: ${response.statusText}`);
      }
    } catch (error) {
      console.warn("⚠️ Lambda warm-up failed:", error);
    } finally {
      this.isWarmingUp = false;
    }
  }

  // Get session info for debugging
  getSessionInfo() {
    return {
      sessionId: this.sessionId,
      lastWarmUp: this.warmUpTimestamp,
      isWarmingUp: this.isWarmingUp
    };
  }
}

export default SessionManager;
```

### 7. Enhanced Query Experience Components

#### Query Suggestions
```tsx
// components/QuerySuggestions.tsx
import React from 'react';

const QuerySuggestions: React.FC = () => {
  const suggestedQueries = [
    {
      query: "Under tariff uncertainty, how do I plan my production?",
      category: "Strategic Planning",
      description: "Test the improved domain detection and response quality"
    },
    {
      query: "How should I approach team resistance to change?",
      category: "Behavioral Management",
      description: "See how the system handles human behavior concepts"
    },
    {
      query: "What strategic framework helps with market entry decisions?",
      category: "Strategic Analysis",
      description: "Experience the enhanced strategic thinking capabilities"
    }
  ];

  const handleSuggestionClick = (query: string) => {
    // Emit event or use callback to set query
    window.dispatchEvent(new CustomEvent('setQuery', { detail: { query } }));
  };

  return (
    <div className="query-suggestions">
      <h4>Try these queries to experience the improved quality:</h4>
      <div className="suggestion-grid">
        {suggestedQueries.map((suggestion, index) => (
          <div key={index} className="suggestion-card">
            <div className="suggestion-header">
              <span className="category">{suggestion.category}</span>
            </div>
            <div className="suggestion-content">
              <p className="query-text">{suggestion.query}</p>
              <p className="description">{suggestion.description}</p>
            </div>
            <button
              className="suggestion-button"
              onClick={() => handleSuggestionClick(suggestion.query)}
            >
              Try This Query
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuerySuggestions;
```

#### Query History
```tsx
// components/QueryHistory.tsx
import React, { useState, useEffect } from 'react';

const QueryHistory: React.FC = () => {
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const maxHistoryItems = 10;

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem('queryHistory');
    if (saved) {
      try {
        setQueryHistory(JSON.parse(saved));
      } catch (e) {
        console.warn('Failed to parse query history');
      }
    }
  }, []);

  const addToHistory = (query: string) => {
    setQueryHistory(prev => {
      const newHistory = [query, ...prev.filter(q => q !== query)].slice(0, maxHistoryItems);
      localStorage.setItem('queryHistory', JSON.stringify(newHistory));
      return newHistory;
    });
  };

  const clearHistory = () => {
    setQueryHistory([]);
    localStorage.removeItem('queryHistory');
  };

  const handleHistoryClick = (query: string) => {
    window.dispatchEvent(new CustomEvent('setQuery', { detail: { query } }));
  };

  if (queryHistory.length === 0) return null;

  return (
    <div className="query-history">
      <div className="history-header">
        <h4>Recent Queries</h4>
        <button className="clear-history" onClick={clearHistory}>
          Clear History
        </button>
      </div>
      <div className="history-list">
        {queryHistory.map((query, index) => (
          <button
            key={index}
            className="history-item"
            onClick={() => handleHistoryClick(query)}
            title={query}
          >
            <span className="query-text">{query}</span>
            <span className="timestamp">{index === 0 ? 'Just now' : `${index} ago`}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QueryHistory;
```

## CSS Styling Recommendations

### Quality Indicator Styles
```css
/* styles/QualityIndicator.css */
.quality-indicator {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 16px 0;
  border-left: 4px solid;
}

.quality-loading {
  background-color: #e3f2fd;
  border-left-color: #2196f3;
  color: #1565c0;
}

.quality-warning {
  background-color: #fff3e0;
  border-left-color: #ff9800;
  color: #e65100;
}

.quality-success {
  background-color: #e8f5e8;
  border-left-color: #4caf50;
  color: #2e7d32;
}

.quality-consistent {
  background-color: #e8f5e8;
  border-left-color: #4caf50;
  color: #2e7d32;
}

.quality-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.quality-tip {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  opacity: 0.8;
}
```

### Response Display Styles
```css
/* styles/ResponseDisplay.css */
.response-container {
  margin-top: 24px;
}

.quality-warning-banner {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border: 1px solid #ffb74d;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1);
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.warning-header .icon {
  font-size: 24px;
}

.warning-header .title {
  font-size: 18px;
  font-weight: 600;
  color: #e65100;
}

.retry-button {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 16px;
}

.retry-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.retry-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quality-score {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.score-bar {
  flex: 1;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff9800 0%, #4caf50 100%);
  transition: width 0.3s ease;
}
```

## Implementation Priority

### Phase 1: Core Quality Management (Week 1)
- [ ] Quality indicator component
- [ ] Response quality analysis
- [ ] Basic retry mechanism
- [ ] Quality warning banners

### Phase 2: Enhanced User Experience (Week 2)
- [ ] Query suggestions component
- [ ] Query history management
- [ ] Session-based warm-up
- [ ] Advanced caching

### Phase 3: Optimization & Polish (Week 3)
- [ ] Performance monitoring
- [ ] User feedback collection
- [ ] Quality metrics dashboard
- [ ] A/B testing setup

## Testing Recommendations

### Quality Consistency Tests
1. **Cold Start Test**: Deploy new version, test first query
2. **Warm Start Test**: Test subsequent queries for quality improvement
3. **Cache Persistence Test**: Verify cache survives multiple requests
4. **Retry Mechanism Test**: Ensure retry improves quality

### User Experience Tests
1. **Quality Indicator Visibility**: Users understand quality status
2. **Retry Button Functionality**: Retry actually improves quality
3. **Suggestion Relevance**: Suggested queries are helpful
4. **History Persistence**: Query history works across sessions

## Monitoring & Analytics

### Key Metrics to Track
- Response quality scores over time
- Retry button usage rates
- User satisfaction with quality improvements
- Cache warm-up success rates
- Query response times

### Error Handling
- Graceful degradation when warm-up fails
- Clear error messages for failed queries
- Fallback responses for low-quality results

## Conclusion

This implementation strategy addresses the Lambda quality consistency issue by:

1. **Transparent Quality Management**: Users understand when quality might be lower
2. **Automatic Warm-up**: Lambda stays warm during active sessions
3. **Smart Caching**: Reduces redundant API calls
4. **Progressive Enhancement**: Quality improves over time
5. **User Education**: Clear messaging about what to expect
6. **Retry Options**: Users can get better quality when needed

The approach ensures users have a consistent, high-quality experience while being transparent about the technical realities of Lambda cold starts and caching behavior.





