function sendMessage() {
    var input = document.getElementById('message-input');
    var chatArea = document.getElementById('chat-area');
    var sendBtn = document.getElementById('send-btn');

    // Validate input - do not send message if input is empty
    if(input.value.trim() !== '') {
        // Append user's message
        var userMessage = document.createElement('div');
        userMessage.className = 'message message-user';
        userMessage.textContent = input.value;
        chatArea.appendChild(userMessage);

        // Disable the input and button
        input.disabled = true;
        sendBtn.disabled = true;
        input.style.backgroundColor = '#ccc';

        // Show loading animation
        var loading = document.getElementById('loading');
        loading.style.display = 'flex';

        // Reset the input
        input.value = '';

        // Encode the user's message for use in a URL
        var encodedMessage = encodeURIComponent(userMessage.textContent);

        // Send the user's message to the API
        fetch('***REMOVED***' + encodedMessage)
        .then(response => response.json())
        .then(data => {
            var botMessage = document.createElement('div');
            botMessage.className = 'message message-bot';
            botMessage.textContent = data.answer;
            chatArea.appendChild(botMessage);

            // Enable the input and button
            input.disabled = false;
            sendBtn.disabled = false;
            input.style.backgroundColor = '';

            // Scroll to bottom of chat area
            chatArea.scrollTop = chatArea.scrollHeight;

            // Hide loading animation
            loading.style.display = 'none';
        })
        .catch((error) => {
            console.error('Error:', error);

            // Handle error - show an error message
            var botMessage = document.createElement('div');
            botMessage.className = 'message message-bot';
            botMessage.textContent = 'Sorry an error occurred';
            chatArea.appendChild(botMessage);

            // Enable the input and button
            input.disabled = false;
            sendBtn.disabled = false;
            input.style.backgroundColor = '';

            // Hide loading animation
            loading.style.display = 'none';
        });
    }
}

document.getElementById('message-input').addEventListener('keydown', function(event) {
    if(event.key === 'Enter') {
        event.preventDefault(); // Prevent form submission on Enter
        sendMessage();
    }
});

document.getElementById('send-btn').addEventListener('click', sendMessage);

window.onload = function() {
    var chatArea = document.getElementById('chat-area');
    
    // If chat area is empty, show the placeholder message
    if (!chatArea.hasChildNodes()) {
        var placeholderMessage = document.createElement('div');
        placeholderMessage.textContent = 'Send a message to learn about the concepts in SkillsBuild!';
        placeholderMessage.style.color = '#bfbfbf';
        placeholderMessage.style.textAlign = 'center';
        chatArea.appendChild(placeholderMessage);
    }
}

// Hide loading animation after 1 second
setTimeout(function() {
    loading.style.display = 'none';
}, 1000);