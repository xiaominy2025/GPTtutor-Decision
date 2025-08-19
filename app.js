// GPTTutor Frontend Application
class GPTTutorApp {
    constructor() {
        this.apiBaseUrl = this.getApiBaseUrl();
        this.isProcessing = false;
        this.init();
    }

    getApiBaseUrl() {
        // Try to detect the API URL based on the current environment
        const currentHost = window.location.hostname;
        const currentProtocol = window.location.protocol;
        
        // For local development
        if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        
        // For production - use the Lambda Function URL
        // This will be updated when we deploy with API Gateway
        return 'https://api.engentlab.com';
    }

    init() {
        this.bindEvents();
        this.checkApiHealth();
    }

    bindEvents() {
        const form = document.getElementById('queryForm');
        const queryInput = document.getElementById('queryInput');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitQuery();
        });

        // Auto-resize textarea
        queryInput.addEventListener('input', () => {
            this.autoResizeTextarea(queryInput);
        });

        // Handle Enter key in textarea
        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.submitQuery();
            }
        });
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                console.log('✅ API is healthy');
            } else {
                console.warn('⚠️ API health check failed');
            }
        } catch (error) {
            console.warn('⚠️ API health check failed:', error);
        }
    }

    async submitQuery() {
        if (this.isProcessing) return;

        const queryInput = document.getElementById('queryInput');
        const query = queryInput.value.trim();

        if (!query) {
            this.showError('Please enter a question');
            return;
        }

        this.setProcessingState(true);
        this.hideError();
        this.hideAnswer();

        try {
            const response = await fetch(`${this.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    course_id: 'decision'
                })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                this.displayAnswer(data.data);
            } else {
                this.showError(data.message || 'Failed to process your question');
            }
        } catch (error) {
            console.error('Query submission error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.setProcessingState(false);
        }
    }

    displayAnswer(data) {
        const answerContainer = document.getElementById('answerContainer');
        const answerContent = document.getElementById('answerContent');
        const followUpContainer = document.getElementById('followUpContainer');

        // Parse and display the answer
        const formattedAnswer = this.formatAnswer(data.answer);
        answerContent.innerHTML = formattedAnswer;

        // Display follow-up prompts if available
        if (data.followUpPrompts && data.followUpPrompts.length > 0) {
            this.displayFollowUpPrompts(data.followUpPrompts);
            followUpContainer.classList.remove('hidden');
        } else {
            followUpContainer.classList.add('hidden');
        }

        // Show the answer container
        answerContainer.classList.remove('hidden');

        // Scroll to the answer
        answerContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    formatAnswer(answer) {
        // Split the answer into sections
        const sections = this.parseAnswerSections(answer);
        let html = '';

        // Strategic Thinking Lens
        if (sections.strategicThinking) {
            html += `
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                        <svg class="w-5 h-5 text-primary-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"></path>
                        </svg>
                        Strategic Thinking Lens
                    </h3>
                    <div class="bg-primary-50 border-l-4 border-primary-500 p-4 rounded-r-lg">
                        <div class="prose prose-sm max-w-none text-gray-700">
                            ${this.markdownToHtml(sections.strategicThinking)}
                        </div>
                    </div>
                </div>
            `;
        }

        // Story in Action
        if (sections.storyInAction) {
            html += `
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                        <svg class="w-5 h-5 text-accent-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path>
                        </svg>
                        Story in Action
                    </h3>
                    <div class="bg-accent-50 border-l-4 border-accent-500 p-4 rounded-r-lg">
                        <div class="prose prose-sm max-w-none text-gray-700">
                            ${this.markdownToHtml(sections.storyInAction)}
                        </div>
                    </div>
                </div>
            `;
        }

        // Concepts/Tools
        if (sections.conceptsTools) {
            html += `
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                        <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                        </svg>
                        Concepts & Tools
                    </h3>
                    <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                        <div class="prose prose-sm max-w-none text-gray-700">
                            ${this.markdownToHtml(sections.conceptsTools)}
                        </div>
                    </div>
                </div>
            `;
        }

        // Processing time info
        if (data.processing_time) {
            html += `
                <div class="mt-6 pt-4 border-t border-gray-200">
                    <p class="text-sm text-gray-500">
                        Processed in ${data.processing_time}s using ${data.model || 'AI'}
                    </p>
                </div>
            `;
        }

        return html;
    }

    parseAnswerSections(answer) {
        const sections = {};

        // Extract Strategic Thinking Lens
        const strategicMatch = answer.match(/\*\*Strategic Thinking Lens\*\*\s*\n+(.*?)(?=\n\*\*|\Z)/s);
        if (strategicMatch) {
            sections.strategicThinking = strategicMatch[1].trim();
        }

        // Extract Story in Action
        const storyMatch = answer.match(/\*\*Story in Action\*\*\s*\n+(.*?)(?=\n\*\*|\Z)/s);
        if (storyMatch) {
            sections.storyInAction = storyMatch[1].trim();
        }

        // Extract Concepts/Tools
        const conceptsMatch = answer.match(/\*\*Concepts\/Tools\*\*\s*\n+(.*?)(?=\n\*\*|\Z)/s);
        if (conceptsMatch) {
            sections.conceptsTools = conceptsMatch[1].trim();
        }

        return sections;
    }

    markdownToHtml(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    displayFollowUpPrompts(prompts) {
        const container = document.getElementById('followUpPrompts');
        
        const promptsHtml = prompts.map((prompt, index) => {
            const cleanPrompt = this.cleanPromptText(prompt);
            return `
                <button 
                    class="follow-up-prompt bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg p-4 text-left transition-all duration-200 cursor-pointer group"
                    onclick="app.handleFollowUpClick('${this.escapeHtml(cleanPrompt)}')"
                >
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0 w-6 h-6 bg-primary-100 group-hover:bg-primary-200 rounded-full flex items-center justify-center mt-0.5">
                            <span class="text-primary-600 text-sm font-medium">${index + 1}</span>
                        </div>
                        <div class="flex-1">
                            <p class="text-gray-700 group-hover:text-primary-700 font-medium">${this.escapeHtml(cleanPrompt)}</p>
                            <p class="text-gray-500 text-sm mt-1">Click to ask this follow-up question</p>
                        </div>
                        <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                            </svg>
                        </div>
                    </div>
                </button>
            `;
        }).join('');

        container.innerHTML = promptsHtml;
    }

    cleanPromptText(prompt) {
        // Remove bullet points, numbers, and extra formatting
        return prompt
            .replace(/^[-•*○\s]+/, '') // Remove leading bullets/dashes
            .replace(/^[•○]\s*[-•*○\s]*/, '') // Remove nested formatting
            .replace(/^\d+\.\s*/, '') // Remove numbered lists
            .trim();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    handleFollowUpClick(prompt) {
        const queryInput = document.getElementById('queryInput');
        queryInput.value = prompt;
        this.autoResizeTextarea(queryInput);
        
        // Auto-submit the follow-up question
        this.submitQuery();
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        const submitBtn = document.getElementById('submitBtn');
        const submitText = document.getElementById('submitText');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const queryInput = document.getElementById('queryInput');

        if (processing) {
            submitBtn.disabled = true;
            submitText.textContent = 'Processing...';
            loadingIndicator.classList.remove('hidden');
            queryInput.disabled = true;
        } else {
            submitBtn.disabled = false;
            submitText.textContent = 'Ask Question';
            loadingIndicator.classList.add('hidden');
            queryInput.disabled = false;
        }
    }

    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorContainer.classList.remove('hidden');
        
        // Scroll to error
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    hideError() {
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.classList.add('hidden');
    }

    hideAnswer() {
        const answerContainer = document.getElementById('answerContainer');
        const followUpContainer = document.getElementById('followUpContainer');
        
        answerContainer.classList.add('hidden');
        followUpContainer.classList.add('hidden');
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GPTTutorApp();
});

// Add some helpful console messages
console.log('🚀 GPTTutor Frontend Loaded');
console.log('💡 Tip: Use Ctrl+Enter to submit your question quickly');
