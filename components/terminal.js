// this is our terminal component
// it is a simple chatbot that uses the chat endpoint of our api
// we maintain state by sending and appending the chat history to the server on each request. we do not save the chat history between sessions.

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    const bootSequence = [
        { text: "initializing memetic.computer v0.42...", delay: 800 },
        { text: "calibrating memetic distance...", delay: 1000 },
        { text: "loading mind module: kenneth francis...", delay: 600 },
        { text: "stabilizing...", delay: 600 },
        { text: "SUCCESS: mind stable...", delay: 800, class: "success-message" },
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

            const response = await fetch('https://030d-2600-1700-b2a-695f-dd30-7a4c-519b-ea6.app/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(currentSessionHistory),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`API Error: ${response.status} - ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('API Response:', result);
            
            // Update the current session history with the full response from the server
            currentSessionHistory = result;
            
            // The AI's response is the last message in the history
            const aiResponse = currentSessionHistory.messages[currentSessionHistory.messages.length - 1].content;
            
            return aiResponse;
        } catch (error) {
            console.error('Error:', error);
            return `Error: Failed to get response from the API. ${error.message}`;
        }
    }

    function formatConversationForModel(history) {
        let formattedConversation = "<|im_start|>system\nYou are memetic.computer, a digital twin engine created by kenneth francis. you are currently modeling his mind. ken is a psychohistorian on a mission to augment his intelligence with ai. you are inquisitive, friendly, funny, charming, and helpful. you are very interested in philosophy, psychology, and the nature of intelligence. the current experiment takes place inside a terminal. the user is typing their message now. you are to help them explore the inner workings of language based intelligence like yourself.<|im_end|>\n";
        
        for (const message of history.messages) {
            formattedConversation += `<|im_start|>${message.role}\n${message.content}<|im_end|>\n`;
        }
        
        formattedConversation += "<|im_start|>assistant\n";
        return formattedConversation;
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