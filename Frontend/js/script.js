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

        var modelToggle = document.querySelector('.model-selector input[type="radio"]:checked');
        var apiURL;

        if (modelToggle.id === 'model-2') {
            apiURL = '***REMOVED***'; // Model 2
        } else {
            apiURL = '***REMOVED***'; // Model 1
        }

        // Send the user's message to the API
        fetch(apiURL + encodedMessage)
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
    
    // Hide loading animation after 1 second
    setTimeout(function() {
        loading.style.display = 'none';
    }, 1000);

    var model1 = document.getElementById('model-1');
    var model2 = document.getElementById('model-2');

    var initialModelIcon1 = document.getElementById('img-model-1');
    var initialModelIcon2 = document.getElementById('img-model-2');

    if (model1.checked) {
        initialModelIcon1.style.filter = "invert(1) brightness(2)";
        initialModelIcon2.style.filter = "";
    } else {
        initialModelIcon2.style.filter = "invert(1) brightness(2)";
        initialModelIcon1.style.filter = "";
    }

    document.getElementById('model-1').addEventListener('change', function() {
        toggleModel('model-1');
    });

    document.getElementById('model-2').addEventListener('change', function() {
        toggleModel('model-2');
    });
}


function toggleModel(model) {
    // remove active class from both models and remove CSS filter from images
    var model1 = document.getElementById('model-1');
    var model1Icon = document.querySelector('label[for="model-1"] img');
    model1.classList.remove('active');
    model1Icon.style.filter = "";

    var model2 = document.getElementById('model-2');
    var model2Icon = document.querySelector('label[for="model-2"] img');
    model2.classList.remove('active');
    model2Icon.style.filter = "";

    // add active class to selected model and apply CSS filter to image
    document.getElementById(model).classList.add('active');
    if (model === 'model-1') {
        model1Icon.style.filter = "invert(1) brightness(2)";
    } else if (model === 'model-2') {
        model2Icon.style.filter = "invert(1) brightness(2)";
    }

    // Then, you can use the model variable to switch your API call to use a different model
    console.log("Using", model);
}


