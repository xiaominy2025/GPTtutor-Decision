# GPTTutor Frontend

A modern, responsive web interface for the GPTTutor Decision Making Assistant, built with vanilla JavaScript and Tailwind CSS.

## 🎯 Features

### ✅ Core Functionality
- **Interactive Query Interface**: Clean, modern form for submitting decision-making questions
- **Real-time API Communication**: Seamless integration with the V1666 backend
- **Structured Answer Display**: Beautiful formatting of Strategic Thinking Lens, Story in Action, and Concepts/Tools sections
- **Clickable Follow-up Prompts**: The key feature - follow-up questions are clickable buttons that auto-populate and submit

### 🎨 Design & UX
- **Modern Blue/Yellow Color Scheme**: Professional and engaging design
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Hover effects, transitions, and loading states
- **Accessibility**: Proper ARIA labels, keyboard navigation, and screen reader support

### 🔧 Technical Features
- **Auto-resizing Textarea**: Dynamic height adjustment as user types
- **Keyboard Shortcuts**: Ctrl+Enter to submit questions quickly
- **Error Handling**: Graceful error display and recovery
- **Loading States**: Visual feedback during API calls
- **Health Checks**: Automatic API connectivity verification

## 📁 File Structure

```
frontend/
├── index.html          # Main HTML file with Tailwind CSS
├── app.js             # Core JavaScript application logic
└── FRONTEND_README.md # This documentation file
```

## 🚀 Quick Start

### Local Development
1. **Serve the files**: Use any local server (Python, Node.js, or VS Code Live Server)
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Node.js (if you have http-server installed)
   npx http-server
   
   # VS Code
   # Install "Live Server" extension and right-click index.html
   ```

2. **Configure API URL**: The app automatically detects localhost and uses `http://localhost:5000` for the backend

3. **Test the interface**: Open `http://localhost:8000` in your browser

### Production Deployment
The frontend is designed to work with the production backend at `https://api.engentlab.com`

## 🔗 Backend Integration

### API Endpoints Used
- `GET /health` - Health check for API connectivity
- `POST /query` - Submit decision-making questions

### Request Format
```json
{
  "query": "How do I make a decision under uncertainty?",
  "course_id": "decision"
}
```

### Response Format
```json
{
  "status": "success",
  "data": {
    "answer": "**Strategic Thinking Lens**\n\n[content]...\n\n**Story in Action**\n\n[content]...\n\n**Concepts/Tools**\n\n[content]...",
    "followUpPrompts": [
      "What specific factors should I consider?",
      "How do I evaluate the risks involved?",
      "What frameworks would be most helpful?"
    ],
    "processing_time": 2.5,
    "model": "gpt-3.5-turbo"
  }
}
```

## 🎯 Key Features Explained

### Clickable Follow-up Prompts
The most important feature - when the backend returns follow-up prompts, they are displayed as interactive buttons:

1. **Visual Design**: Each prompt is a card with hover effects
2. **Click Behavior**: Clicking a prompt:
   - Populates the input field with the question text
   - Auto-resizes the textarea
   - Automatically submits the new question
3. **User Experience**: Seamless conversation flow without manual typing

### Answer Section Parsing
The frontend intelligently parses the backend response into structured sections:
- **Strategic Thinking Lens**: Blue-themed section with brain icon
- **Story in Action**: Yellow-themed section with book icon  
- **Concepts/Tools**: Green-themed section with toolbox icon

### Error Handling
- Network connectivity issues
- API response errors
- Invalid input validation
- Graceful fallbacks with user-friendly messages

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#3b82f6` - Main brand color
- **Accent Yellow**: `#eab308` - Highlight color
- **Success Green**: `#10b981` - Positive actions
- **Error Red**: `#ef4444` - Error states
- **Neutral Grays**: Various shades for text and backgrounds

### Typography
- **Headings**: Bold, clear hierarchy
- **Body Text**: Readable, well-spaced
- **Interactive Elements**: Clear hover states

### Components
- **Cards**: Rounded corners, subtle shadows
- **Buttons**: Consistent padding, hover effects
- **Forms**: Clear labels, validation states
- **Loading**: Animated dots, skeleton screens

## 🔧 Configuration

### API URL Configuration
The app automatically detects the environment:

```javascript
getApiBaseUrl() {
    const currentHost = window.location.hostname;
    
    // Local development
    if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    
    // Production
    return 'https://api.engentlab.com';
}
```

### Customization Options
- **Colors**: Modify the Tailwind config in `index.html`
- **API Endpoints**: Update the `getApiBaseUrl()` method
- **Styling**: Edit CSS classes and Tailwind utilities

## 🚀 Deployment Options

### Option 1: S3 + CloudFront (Recommended)
1. **Create S3 Bucket**: `engentlab.com` (or your domain)
2. **Upload Files**: `index.html`, `app.js`
3. **Configure CloudFront**: 
   - Origin: S3 bucket
   - Custom domain: `engentlab.com`
   - SSL certificate from ACM
4. **Update DNS**: Point domain to CloudFront distribution

### Option 2: GitHub Pages
1. **Create Repository**: `gpttutor-frontend`
2. **Upload Files**: Push to main branch
3. **Enable Pages**: Settings → Pages → Source: main branch
4. **Custom Domain**: Configure in repository settings

### Option 3: Netlify/Vercel
1. **Connect Repository**: Link to GitHub/GitLab
2. **Auto-deploy**: Automatic deployments on push
3. **Custom Domain**: Configure in platform settings

## 🧪 Testing

### Manual Testing Checklist
- [ ] Form submission works
- [ ] Follow-up prompts are clickable
- [ ] Error handling displays properly
- [ ] Responsive design on mobile
- [ ] Keyboard shortcuts work (Ctrl+Enter)
- [ ] Loading states show correctly
- [ ] API health check works

### Browser Compatibility
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🔍 Troubleshooting

### Common Issues

**Follow-up prompts not clickable**
- Check browser console for JavaScript errors
- Verify `app.js` is loading correctly
- Ensure backend returns `followUpPrompts` array

**API connection fails**
- Verify backend is running on correct port
- Check CORS configuration on backend
- Test API endpoints directly with curl/Postman

**Styling issues**
- Ensure Tailwind CSS is loading
- Check for CSS conflicts
- Verify viewport meta tag is present

### Debug Mode
Open browser console to see:
- API health check results
- Request/response logs
- Error messages
- Performance metrics

## 📈 Performance

### Optimizations
- **Minimal Dependencies**: Only Tailwind CSS (CDN)
- **Efficient DOM Updates**: Minimal re-renders
- **Lazy Loading**: Content loads as needed
- **Caching**: Browser caching for static assets

### Metrics
- **First Load**: ~50KB (HTML + CSS + JS)
- **Subsequent Loads**: ~5KB (cached CSS)
- **API Response Time**: 2-5 seconds typical

## 🔮 Future Enhancements

### Planned Features
- **User Profiles**: Save preferences and history
- **Export Options**: PDF/Word document generation
- **Advanced Analytics**: Usage tracking and insights
- **Offline Mode**: Service worker for offline access
- **Dark Mode**: Toggle between light/dark themes

### Technical Improvements
- **Progressive Web App**: Installable app experience
- **Real-time Updates**: WebSocket for live responses
- **Advanced Caching**: Intelligent response caching
- **Performance Monitoring**: Real user metrics

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style
- **JavaScript**: ES6+ features, consistent naming
- **HTML**: Semantic markup, accessibility first
- **CSS**: Tailwind utilities, minimal custom CSS

## 📞 Support

For issues or questions:
1. Check this README
2. Review browser console for errors
3. Test API endpoints directly
4. Contact development team

---

**Built with ❤️ for better decision making**
