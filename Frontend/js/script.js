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
        loading.style.visibility = 'visible';

        // Reset the input
        input.value = '';

        var modelToggle = document.querySelector('.model-selector input[type="radio"]:checked');
        var apiURL, messageBody, requestOptions;

        if (modelToggle.id === 'model-3') {
            apiURL = '***REMOVED***'; // Model 3
            messageBody = JSON.stringify({ message: userMessage.textContent });
            requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: messageBody,
            };
        } else if (modelToggle.id === 'model-2') {
            apiURL = '***REMOVED***'; // Model 2
            messageBody = JSON.stringify({ sender: 'test', message: userMessage.textContent });
            requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: messageBody,
            };
        } else {
            apiURL = '***REMOVED***' + userMessage.textContent; // Model 1
            requestOptions = {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            };
        }

        // Send the user's message to the API
        fetch(apiURL, requestOptions)
            .then(response => response.json())
            .then(data => {
                var botMessage = document.createElement('div');
                botMessage.className = 'message message-bot';
                if (modelToggle.id === 'model-3') {
                    botMessage.textContent = data.response.split('Response: ')[1]; 
                } else if (modelToggle.id === 'model-2') {
                    botMessage.textContent = data[0].text; 
                } else {
                    botMessage.textContent = data.answer;
                }
                chatArea.appendChild(botMessage);

                // Enable the input and button
                input.disabled = false;
                sendBtn.disabled = false;
                input.style.backgroundColor = '';

                // Scroll to bottom of chat area
                chatArea.scrollTop = chatArea.scrollHeight;

                // Hide loading animation
                loading.style.visibility = 'hidden';
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
                loading.style.visibility = 'hidden';
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
    var model3 = document.getElementById('model-3');

    var initialModelIcon1 = document.getElementById('img-model-1');
    var initialModelIcon2 = document.getElementById('img-model-2');
    var initialModelIcon3 = document.getElementById('img-model-3');

    if (model1.checked) {
        initialModelIcon1.style.filter = "invert(1) brightness(2)";
        initialModelIcon2.style.filter = "";
        initialModelIcon3.style.filter = "";
    } else if (model2.checked) {
        initialModelIcon2.style.filter = "invert(1) brightness(2)";
        initialModelIcon1.style.filter = "";
        initialModelIcon3.style.filter = "";
    } else {
        initialModelIcon3.style.filter = "invert(1) brightness(2)";
        initialModelIcon1.style.filter = "";
        initialModelIcon2.style.filter = "";
    }

    document.getElementById('model-1').addEventListener('change', function() {
        toggleModel('model-1');
    });

    document.getElementById('model-2').addEventListener('change', function() {
        toggleModel('model-2');
    });

    document.getElementById('model-3').addEventListener('change', function() {
        toggleModel('model-3');
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

    var model3 = document.getElementById('model-3');
    var model3Icon = document.querySelector('label[for="model-3"] img');
    model3.classList.remove('active');
    model3Icon.style.filter = "";

    // add active class to selected model and apply CSS filter to image
    document.getElementById(model).classList.add('active');
    if (model === 'model-1') {
        model1Icon.style.filter = "invert(1) brightness(2)";
    } else if (model === 'model-2') {
        model2Icon.style.filter = "invert(1) brightness(2)";
    } else if (model === 'model-3') {
        model3Icon.style.filter = "invert(1) brightness(2)";
    }

    // Then, you can use the model variable to switch your API call to use a different model
    console.log("Using", model);
}
