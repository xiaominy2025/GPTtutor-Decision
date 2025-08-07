# GPTTutor - Web UI Development Roadmap

## 🎯 Overview

This roadmap outlines the development of a React-based web interface for GPTTutor, leveraging the production-ready Flask API backend. The UI will provide an intuitive, responsive interface for students to interact with the decision-making tutor.

## 🏗️ Technical Stack

### **Frontend**
- **React 18** - Modern UI framework
- **TypeScript** - Type safety and better development experience
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **React Query** - Server state management
- **Framer Motion** - Smooth animations

### **Backend Integration**
- **Flask API** - Already implemented and ready
- **CORS** - Cross-origin request handling
- **JSON Responses** - Structured data format
- **Error Handling** - Proper HTTP status codes

## 📋 Phase 1: Foundation (Week 1-2)

### **🎯 Goals**
- Set up React development environment
- Create basic UI components
- Integrate with Flask API
- Implement core query functionality

### **📁 Project Structure**
```
gpttutor-frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── QueryForm.tsx
│   │   ├── AnswerDisplay.tsx
│   │   ├── TooltipSystem.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── QueryPage.tsx
│   │   └── ProfilePage.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── hooks/
│   │   ├── useQuery.ts
│   │   └── useProfile.ts
│   ├── utils/
│   │   ├── markdown.ts
│   │   └── validation.ts
│   ├── styles/
│   │   └── globals.css
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── README.md
```

### **🔧 Implementation Steps**

#### **Step 1: Project Setup**
```bash
# Create React app with TypeScript
npx create-react-app gpttutor-frontend --template typescript

# Install dependencies
npm install axios react-query react-router-dom framer-motion
npm install -D tailwindcss @types/node

# Configure Tailwind CSS
npx tailwindcss init
```

#### **Step 2: API Integration**
```typescript
// services/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const queryService = {
  submitQuery: async (query: string, userId?: string) => {
    const response = await api.post('/query', { query, user_id: userId });
    return response.data;
  },
  
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/profile');
    return response.data;
  },
  
  updateProfile: async (profile: any) => {
    const response = await api.put('/profile', profile);
    return response.data;
  },
};
```

#### **Step 3: Core Components**

**QueryForm Component:**
```typescript
// components/QueryForm.tsx
import React, { useState } from 'react';
import { useQuery } from '../hooks/useQuery';

export const QueryForm: React.FC = () => {
  const [query, setQuery] = useState('');
  const { submitQuery, isLoading, error } = useQuery();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await submitQuery(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="query" className="block text-sm font-medium">
          Ask your decision-making question:
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          rows={4}
          placeholder="How do I make a decision under uncertainty?"
        />
      </div>
      <button
        type="submit"
        disabled={isLoading || !query.trim()}
        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Processing...' : 'Ask Question'}
      </button>
    </form>
  );
};
```

**AnswerDisplay Component:**
```typescript
// components/AnswerDisplay.tsx
import React from 'react';
import { AnswerData } from '../services/types';

interface Props {
  answer: AnswerData | null;
}

export const AnswerDisplay: React.FC<Props> = ({ answer }) => {
  if (!answer) return null;

  return (
    <div className="space-y-6">
      {/* Strategic Thinking Lens */}
      {answer.sections.strategic_thinking && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">
            🧠 Strategic Thinking Lens
          </h3>
          <div className="prose max-w-none">
            {answer.sections.strategic_thinking.content}
          </div>
        </div>
      )}

      {/* Story in Action */}
      {answer.sections.story_action && (
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">
            📘 Story in Action
          </h3>
          <div className="prose max-w-none">
            {answer.sections.story_action.content}
          </div>
        </div>
      )}

      {/* Want to Go Deeper */}
      {answer.sections.deeper_questions && (
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">
            💬 Want to Go Deeper?
          </h3>
          <div className="prose max-w-none">
            {answer.sections.deeper_questions.content}
          </div>
        </div>
      )}

      {/* Tooltips */}
      {Object.keys(answer.tooltips).length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">🔧 Concepts & Tools</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(answer.tooltips).map(([name, tooltip]) => (
              <div key={name} className="bg-white p-3 rounded border">
                <h4 className="font-medium text-blue-600">{name}</h4>
                <p className="text-sm text-gray-600 mt-1">{tooltip}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

### **🎨 Design System**

**Color Palette:**
- **Primary**: Blue (#3B82F6) - Trust, intelligence
- **Success**: Green (#10B981) - Growth, learning
- **Warning**: Yellow (#F59E0B) - Attention, caution
- **Error**: Red (#EF4444) - Errors, alerts
- **Neutral**: Gray (#6B7280) - Text, borders

**Typography:**
- **Headings**: Inter font family
- **Body**: System font stack
- **Code**: JetBrains Mono

**Components:**
- **Cards**: Rounded corners, subtle shadows
- **Buttons**: Consistent padding, hover states
- **Forms**: Clear labels, validation states
- **Loading**: Skeleton screens, spinners

## 📋 Phase 2: Enhanced Features (Week 3-4)

### **🎯 Goals**
- Add user profile management
- Implement tooltip system
- Create analytics dashboard
- Improve responsive design

### **🔧 New Components**

**Profile Management:**
```typescript
// components/ProfileManager.tsx
export const ProfileManager: React.FC = () => {
  const [profile, setProfile] = useState({
    role: 'helpful tutor',
    tone: 'encouraging and clear',
    thinking_style: 'step-by-step reasoning',
    preferred_frameworks: ['decision tree', 'swot analysis']
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Profile Settings</h2>
      
      {/* Role Selection */}
      <div>
        <label className="block text-sm font-medium">Teaching Role</label>
        <select
          value={profile.role}
          onChange={(e) => setProfile({...profile, role: e.target.value})}
          className="mt-1 block w-full rounded-md border-gray-300"
        >
          <option value="helpful tutor">Helpful Tutor</option>
          <option value="expert consultant">Expert Consultant</option>
          <option value="mentor">Mentor</option>
        </select>
      </div>

      {/* Tone Selection */}
      <div>
        <label className="block text-sm font-medium">Communication Tone</label>
        <select
          value={profile.tone}
          onChange={(e) => setProfile({...profile, tone: e.target.value})}
          className="mt-1 block w-full rounded-md border-gray-300"
        >
          <option value="encouraging and clear">Encouraging & Clear</option>
          <option value="concise and direct">Concise & Direct</option>
          <option value="patient and thorough">Patient & Thorough</option>
        </select>
      </div>

      {/* Framework Preferences */}
      <div>
        <label className="block text-sm font-medium">Preferred Frameworks</label>
        <div className="mt-2 space-y-2">
          {['decision tree', 'swot analysis', 'cost-benefit analysis', 'expected utility'].map(framework => (
            <label key={framework} className="flex items-center">
              <input
                type="checkbox"
                checked={profile.preferred_frameworks.includes(framework)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setProfile({
                      ...profile,
                      preferred_frameworks: [...profile.preferred_frameworks, framework]
                    });
                  } else {
                    setProfile({
                      ...profile,
                      preferred_frameworks: profile.preferred_frameworks.filter(f => f !== framework)
                    });
                  }
                }}
                className="rounded border-gray-300"
              />
              <span className="ml-2 text-sm">{framework}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};
```

**Analytics Dashboard:**
```typescript
// components/AnalyticsDashboard.tsx
export const AnalyticsDashboard: React.FC = () => {
  const { data: stats } = useQuery(['stats'], queryService.getStats);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Queries */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Queries</h3>
        <p className="text-2xl font-bold text-gray-900">{stats?.total_queries || 0}</p>
      </div>

      {/* Average Response Time */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Avg Response Time</h3>
        <p className="text-2xl font-bold text-gray-900">
          {stats?.avg_response_time ? `${stats.avg_response_time.toFixed(1)}s` : '0s'}
        </p>
      </div>

      {/* Token Efficiency */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Token Efficiency</h3>
        <p className="text-2xl font-bold text-green-600">
          {stats?.tooltip_stats?.efficiency || '0%'}
        </p>
      </div>

      {/* Estimated Cost */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Estimated Cost</h3>
        <p className="text-2xl font-bold text-blue-600">
          {stats?.estimated_cost || '$0.00'}
        </p>
      </div>
    </div>
  );
};
```

## 📋 Phase 3: Advanced Features (Week 5-6)

### **🎯 Goals**
- Add real-time updates
- Implement advanced analytics
- Create export features
- Add multi-language support

### **🔧 Advanced Features**

**Real-time Updates:**
```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef } from 'react';

export const useWebSocket = (url: string) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle real-time updates
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return ws.current;
};
```

**Export Features:**
```typescript
// utils/export.ts
export const exportAnswer = (answer: AnswerData, format: 'pdf' | 'markdown' | 'json') => {
  switch (format) {
    case 'pdf':
      // Generate PDF using jsPDF
      break;
    case 'markdown':
      // Convert to markdown
      break;
    case 'json':
      // Export as JSON
      break;
  }
};
```

## 🚀 Deployment Strategy

### **Development Environment**
- **Local**: React dev server + Flask API
- **Testing**: Jest + React Testing Library
- **Linting**: ESLint + Prettier
- **Type Checking**: TypeScript compiler

### **Production Deployment**
- **Frontend**: Vercel/Netlify (React app)
- **Backend**: Heroku/AWS (Flask API)
- **Database**: PostgreSQL (future enhancement)
- **Monitoring**: Sentry for error tracking

## 📊 Success Metrics

### **User Experience**
- **Response Time**: < 3 seconds for queries
- **Error Rate**: < 1% of requests
- **User Satisfaction**: > 4.5/5 rating
- **Engagement**: > 5 queries per session

### **Technical Performance**
- **Bundle Size**: < 500KB gzipped
- **First Contentful Paint**: < 2 seconds
- **Lighthouse Score**: > 90 for all metrics
- **Mobile Responsiveness**: 100% compatibility

## 🎯 Timeline

### **Week 1-2: Foundation**
- [ ] React project setup
- [ ] Basic components (QueryForm, AnswerDisplay)
- [ ] API integration
- [ ] Error handling
- [ ] Basic styling

### **Week 3-4: Enhanced Features**
- [ ] User profile management
- [ ] Tooltip system
- [ ] Analytics dashboard
- [ ] Responsive design
- [ ] Loading states

### **Week 5-6: Advanced Features**
- [ ] Real-time updates
- [ ] Export functionality
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Performance optimization

### **Week 7: Testing & Deployment**
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Production deployment
- [ ] Documentation
- [ ] User feedback collection

## 🎉 Expected Outcomes

By the end of this roadmap, GPTTutor will have:

- **Modern Web Interface**: Intuitive, responsive React application
- **Enhanced User Experience**: Smooth interactions and helpful features
- **Production Deployment**: Scalable, monitored application
- **Comprehensive Analytics**: Usage tracking and performance monitoring
- **Future-Ready Architecture**: Easy to extend and maintain

---

**📅 Created: January 2025**
**🎯 Status: Ready for Implementation**
**🚀 Next: React Development Setup** 