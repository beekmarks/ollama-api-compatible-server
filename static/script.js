document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat');
    const chatMessages = document.getElementById('chat-messages');
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const generationResult = document.getElementById('generation-result');
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    const maxTokensInput = document.getElementById('max-tokens');
    const modelName = document.getElementById('model-name');
    const modelSize = document.getElementById('model-size');
    const loadingOverlay = document.getElementById('loading-overlay');

    // API Base URL
    const API_BASE_URL = 'http://localhost:11435/api';

    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });

    // Temperature slider
    temperatureSlider.addEventListener('input', () => {
        temperatureValue.textContent = temperatureSlider.value;
    });

    // Load model information
    async function loadModelInfo() {
        try {
            const response = await fetch(`${API_BASE_URL}/tags`);
            const data = await response.json();
            
            if (data.models && data.models.length > 0) {
                const model = data.models[0];
                modelName.textContent = model.name;
                
                // Format size in GB
                const sizeInGB = (model.size / (1024 * 1024 * 1024)).toFixed(2);
                modelSize.textContent = `(${sizeInGB} GB)`;
            } else {
                modelName.textContent = 'No models available';
            }
        } catch (error) {
            console.error('Error loading model info:', error);
            modelName.textContent = 'Error loading model info';
        }
    }

    // Send chat message
    async function sendChatMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessageToChat('user', message);
        chatInput.value = '';

        // Show loading overlay
        loadingOverlay.classList.add('active');

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: modelName.textContent,
                    messages: [
                        { role: 'user', content: message }
                    ],
                    stream: false
                })
            });

            const data = await response.json();
            
            // Add assistant response to chat
            if (data.message && data.message.content) {
                addMessageToChat('assistant', data.message.content);
            } else {
                addMessageToChat('system', 'Error: Received an invalid response from the server.');
            }
        } catch (error) {
            console.error('Error sending chat message:', error);
            addMessageToChat('system', `Error: ${error.message}`);
        } finally {
            // Hide loading overlay
            loadingOverlay.classList.remove('active');
        }
    }

    // Generate text
    async function generateText() {
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        // Show loading overlay
        loadingOverlay.classList.add('active');
        
        // Clear previous result
        generationResult.innerHTML = '';

        try {
            const response = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: modelName.textContent,
                    prompt: prompt,
                    stream: false,
                    options: {
                        temperature: parseFloat(temperatureSlider.value),
                        num_predict: parseInt(maxTokensInput.value)
                    }
                })
            });

            const data = await response.json();
            
            if (data.response) {
                generationResult.textContent = data.response;
            } else {
                generationResult.innerHTML = '<p class="placeholder">Error: Received an invalid response from the server.</p>';
            }
        } catch (error) {
            console.error('Error generating text:', error);
            generationResult.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        } finally {
            // Hide loading overlay
            loadingOverlay.classList.remove('active');
        }
    }

    // Add message to chat
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        
        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners
    sendChatBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    generateBtn.addEventListener('click', generateText);

    // Initialize
    loadModelInfo();
});
