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

        // Reset the input
        input.value = '';

        // Simulate error message
        setTimeout(function() {
            var botMessage = document.createElement('div');
            botMessage.className = 'message message-bot';
            botMessage.textContent = 'Sorry an error occurred';
            chatArea.appendChild(botMessage);

            // Enable the input and button
            input.disabled = false;
            sendBtn.disabled = false;
            input.style.backgroundColor = '';

        }, 1000);

        // Scroll to bottom of chat area
        chatArea.scrollTop = chatArea.scrollHeight;
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
