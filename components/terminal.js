// this is our terminal component
// it is a simple chatbot that uses the chat endpoint of our api
// we maintain state by sending and appending the chat history to the server on each request. we do not save the chat history between sessions.

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    const bootSequence = [
        { text: "initializing memetic.computer v0.42...", delay: 800 },
        { text: "loading mind: k3nneth francis...", delay: 600 },
        { text: "calibrating memetic distance...", delay: 1000 },
        { text: "SUCCESS: mind stable.", delay: 800, class: "success-message" },
        { text: "awaiting message...", delay: 400}
    ];

    const terminal = document.getElementById('terminal');
    const output = document.getElementById('output');
    const userInput = document.getElementById('user-input');

    // Initialize an empty chat history for the current session
    let currentSessionHistory = {
        messages: []
    };

    async function getChatResponse(message) {
        console.log(`Sending message to API: ${message}`);
        try {
            // Add user message to current session history
            currentSessionHistory.messages.push({ role: "user", content: message });

            const response = await fetch('http://0.0.0.0:1337/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentSessionHistory),
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const updatedHistory = await response.json();
            console.log(`Received response from API:`, updatedHistory);
            
            // Update current session history with the response from the server
            currentSessionHistory = updatedHistory;
            
            // Return only the last message (AI's response)
            return currentSessionHistory.messages[currentSessionHistory.messages.length - 1].content;
        } catch (error) {
            console.error('Error:', error);
            return "Error: Failed to get response from the server. Please check the console for more details.";
        }
    }

    function addMessage(sender, text, className = '') {
        console.log(`Adding message from ${sender}: ${text}`);
        const messageElement = document.createElement('div');
        messageElement.textContent = sender === 'user' ? `> ${text}` : text;
        messageElement.classList.add('message', `${sender}-message`);
        if (className) messageElement.classList.add(className);
        output.appendChild(messageElement);
        terminal.scrollTop = terminal.scrollHeight;
    }

    userInput.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            const message = this.value.trim();
            if (message !== '') {
                addMessage('user', message);
                this.value = '';
                
                // Disable input while waiting for response
                this.disabled = true;
                
                try {
                    const response = await getChatResponse(message);
                    addMessage('assistant', response);
                } catch (error) {
                    addMessage('system', 'Error: Failed to get response', 'error-message');
                }
                
                // Re-enable input and focus
                this.disabled = false;
                this.focus();
            }
        }
    });

    // Initial setup
    userInput.disabled = true;
    simulateBootSequence();

    function simulateBootSequence() {
        console.log('Starting boot sequence');
        let totalDelay = 0;
        bootSequence.forEach((message, index) => {
            totalDelay += message.delay;
            setTimeout(() => {
                console.log(`Displaying boot message: ${message.text}`);
                addMessage('system', message.text, message.class);
                if (index === bootSequence.length - 1) {
                    console.log('Boot sequence complete');
                    userInput.disabled = false;
                    userInput.focus();
                }
            }, totalDelay);
        });
    }
});