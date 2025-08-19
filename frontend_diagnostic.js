// GPTTutor Frontend Diagnostic & Recovery Script
// Add this to your existing frontend to diagnose and fix clickable prompts issues

(function() {
    'use strict';
    
    console.log('🔍 GPTTutor Frontend Diagnostic Starting...');
    
    // Diagnostic results
    const diagnostics = {
        jsLoaded: false,
        apiUrl: null,
        backendReachable: false,
        followUpContainerExists: false,
        clickHandlersAttached: false,
        issues: []
    };
    
    // Test 1: Check if main JavaScript is loaded
    function checkJavaScriptLoading() {
        console.log('📋 Test 1: Checking JavaScript loading...');
        
        // Check if key functions exist
        const requiredFunctions = ['getApiBaseUrl', 'submitQuery', 'displayFollowUpPrompts'];
        const missingFunctions = requiredFunctions.filter(fn => typeof window[fn] === 'undefined');
        
        if (missingFunctions.length > 0) {
            diagnostics.issues.push(`Missing functions: ${missingFunctions.join(', ')}`);
            console.error('❌ Missing required functions:', missingFunctions);
        } else {
            diagnostics.jsLoaded = true;
            console.log('✅ All required functions found');
        }
        
        // Check API URL
        if (typeof window.getApiBaseUrl === 'function') {
            try {
                diagnostics.apiUrl = window.getApiBaseUrl();
                console.log('🔗 API URL:', diagnostics.apiUrl);
            } catch (e) {
                diagnostics.issues.push('getApiBaseUrl function error: ' + e.message);
            }
        }
    }
    
    // Test 2: Check backend connectivity
    async function checkBackendConnectivity() {
        console.log('📋 Test 2: Checking backend connectivity...');
        
        if (!diagnostics.apiUrl) {
            diagnostics.issues.push('No API URL available');
            return;
        }
        
        try {
            const response = await fetch(`${diagnostics.apiUrl}/health`);
            const data = await response.json();
            
            if (response.ok) {
                diagnostics.backendReachable = true;
                console.log('✅ Backend is reachable:', data);
            } else {
                diagnostics.issues.push(`Backend health check failed: ${response.status}`);
                console.warn('⚠️ Backend health check failed:', response.status);
            }
        } catch (error) {
            diagnostics.issues.push(`Backend connection error: ${error.message}`);
            console.error('❌ Backend connection failed:', error);
        }
    }
    
    // Test 3: Check DOM elements
    function checkDOMElements() {
        console.log('📋 Test 3: Checking DOM elements...');
        
        const requiredElements = [
            'queryForm',
            'queryInput', 
            'answerContainer',
            'followUpContainer',
            'followUpPrompts'
        ];
        
        const missingElements = requiredElements.filter(id => !document.getElementById(id));
        
        if (missingElements.length > 0) {
            diagnostics.issues.push(`Missing DOM elements: ${missingElements.join(', ')}`);
            console.error('❌ Missing DOM elements:', missingElements);
        } else {
            diagnostics.followUpContainerExists = true;
            console.log('✅ All required DOM elements found');
        }
    }
    
    // Test 4: Check click handlers
    function checkClickHandlers() {
        console.log('📋 Test 4: Checking click handlers...');
        
        const followUpContainer = document.getElementById('followUpPrompts');
        if (followUpContainer) {
            const buttons = followUpContainer.querySelectorAll('button');
            if (buttons.length > 0) {
                const hasClickHandlers = Array.from(buttons).some(btn => 
                    btn.onclick || btn.getAttribute('onclick')
                );
                
                if (hasClickHandlers) {
                    diagnostics.clickHandlersAttached = true;
                    console.log('✅ Click handlers found on follow-up buttons');
                } else {
                    diagnostics.issues.push('No click handlers on follow-up buttons');
                    console.warn('⚠️ No click handlers found on follow-up buttons');
                }
            } else {
                console.log('ℹ️ No follow-up buttons found (normal if no prompts displayed)');
            }
        }
    }
    
    // Emergency fix for clickable prompts
    function applyEmergencyFix() {
        console.log('🚨 Applying emergency fix for clickable prompts...');
        
        // Override displayFollowUpPrompts if it doesn't exist or is broken
        if (typeof window.displayFollowUpPrompts === 'undefined' || diagnostics.issues.length > 0) {
            window.displayFollowUpPrompts = function(prompts) {
                console.log('🔧 Using emergency displayFollowUpPrompts');
                
                const container = document.getElementById('followUpPrompts');
                const followUpContainer = document.getElementById('followUpContainer');
                
                if (!container) {
                    console.error('❌ Follow-up prompts container not found');
                    return;
                }
                
                if (!prompts || prompts.length === 0) {
                    console.log('ℹ️ No follow-up prompts to display');
                    followUpContainer.classList.add('hidden');
                    return;
                }
                
                const promptsHtml = prompts.map((prompt, index) => {
                    const cleanPrompt = prompt.replace(/^[-•*○\s]+/, '').trim();
                    return `
                        <button 
                            class="follow-up-prompt bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg p-4 text-left transition-all duration-200 cursor-pointer group"
                            onclick="window.handleFollowUpClick('${cleanPrompt.replace(/'/g, "\\'")}')"
                        >
                            <div class="flex items-start space-x-3">
                                <div class="flex-shrink-0 w-6 h-6 bg-blue-100 group-hover:bg-blue-200 rounded-full flex items-center justify-center mt-0.5">
                                    <span class="text-blue-600 text-sm font-medium">${index + 1}</span>
                                </div>
                                <div class="flex-1">
                                    <p class="text-gray-700 group-hover:text-blue-700 font-medium">${cleanPrompt}</p>
                                    <p class="text-gray-500 text-sm mt-1">Click to ask this follow-up question</p>
                                </div>
                                <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                                    </svg>
                                </div>
                            </div>
                        </button>
                    `;
                }).join('');
                
                container.innerHTML = promptsHtml;
                followUpContainer.classList.remove('hidden');
                
                console.log('✅ Emergency follow-up prompts displayed');
            };
        }
        
        // Override handleFollowUpClick if it doesn't exist
        if (typeof window.handleFollowUpClick === 'undefined') {
            window.handleFollowUpClick = function(prompt) {
                console.log('🖱️ Emergency handleFollowUpClick called with:', prompt);
                
                const queryInput = document.getElementById('queryInput');
                const form = document.getElementById('queryForm');
                
                if (queryInput && form) {
                    queryInput.value = prompt;
                    
                    // Auto-resize textarea if function exists
                    if (typeof window.autoResizeTextarea === 'function') {
                        window.autoResizeTextarea(queryInput);
                    }
                    
                    // Submit the form
                    if (typeof window.submitQuery === 'function') {
                        window.submitQuery();
                    } else {
                        form.dispatchEvent(new Event('submit'));
                    }
                    
                    console.log('✅ Follow-up prompt submitted');
                } else {
                    console.error('❌ Required elements not found for follow-up submission');
                }
            };
        }
        
        console.log('✅ Emergency fix applied');
    }
    
    // Run diagnostics
    async function runDiagnostics() {
        console.log('🔍 Running GPTTutor Frontend Diagnostics...');
        
        checkJavaScriptLoading();
        await checkBackendConnectivity();
        checkDOMElements();
        checkClickHandlers();
        
        // Apply emergency fix if needed
        if (diagnostics.issues.length > 0) {
            console.log('⚠️ Issues detected, applying emergency fix...');
            applyEmergencyFix();
        }
        
        // Display results
        console.log('📊 Diagnostic Results:', diagnostics);
        
        if (diagnostics.issues.length === 0) {
            console.log('✅ All diagnostics passed!');
        } else {
            console.log('❌ Issues found:', diagnostics.issues);
        }
        
        return diagnostics;
    }
    
    // Auto-run diagnostics when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runDiagnostics);
    } else {
        runDiagnostics();
    }
    
    // Make diagnostics available globally
    window.gptTutorDiagnostics = {
        run: runDiagnostics,
        results: diagnostics,
        applyEmergencyFix: applyEmergencyFix
    };
    
    console.log('🔍 GPTTutor Frontend Diagnostic Ready');
    console.log('💡 Run window.gptTutorDiagnostics.run() to re-run diagnostics');
    
})();
