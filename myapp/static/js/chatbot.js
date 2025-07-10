document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos del DOM ---
    const chatbotFab = document.getElementById('chatbot-fab');
    const chatbotContainer = document.getElementById('chatbot-container');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const messagesContainer = document.getElementById('chatbot-messages');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send-btn');
    const suggestionsContainer = document.getElementById('chatbot-suggestions');

    let isLoading = false;

    // --- Funciones de Ayuda ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // --- Lógica de la Interfaz ---
    function toggleChat() {
        const isActive = chatbotContainer.classList.toggle('active');
        chatbotFab.style.display = isActive ? 'none' : 'flex';
        if (isActive) {
            setTimeout(() => input.focus(), 300);
            if (messagesContainer.children.length === 0) {
                 displayWelcomeMessage();
            }
        }
    }

    function displayWelcomeMessage() {
        displayBotMessage('Hola, soy GenAssist. Estoy aquí para ayudarte. ¿Qué necesitas saber?');
        displaySuggestions(['¿Cuáles son mis pacientes con análisis pendientes?', 'Resúmeme el caso del paciente con ID 12345678', 'Información sobre el Síndrome de Marfan']);
        input.disabled = false;
        sendBtn.disabled = true;
    }

    // --- Lógica de Mensajes ---
    async function handleSendMessage(messageText) {
        if (!messageText || isLoading) return;

        isLoading = true;
        sendBtn.disabled = true;

        displayUserMessage(messageText);
        suggestionsContainer.innerHTML = '';
        const thinkingIndicator = displayBotMessage('<div class="typing-dots"><span></span><span></span><span></span></div>', true);

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken, // Clave para la seguridad de Django
                },
                body: JSON.stringify({ query: messageText }),
            });

            if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
            const data = await response.json();

            thinkingIndicator.querySelector('.message-content').innerHTML = data.response;
            thinkingIndicator.classList.remove('thinking');
            displaySuggestions(data.suggestions);

        } catch (error) {
            console.error('Error al contactar al chatbot:', error);
            thinkingIndicator.querySelector('.message-content').innerText = 'Lo siento, ocurrió un error de comunicación. Inténtalo de nuevo.';
            thinkingIndicator.classList.remove('thinking');
        } finally {
            isLoading = false;
            sendBtn.disabled = input.value.trim() === '';
        }
    }

    function displayUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function displayBotMessage(htmlContent, isThinking = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot';
        if (isThinking) messageDiv.classList.add('thinking');
        messageDiv.innerHTML = `<div class="message-content">${htmlContent}</div>`;
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    function displaySuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        if (suggestions && Array.isArray(suggestions) && suggestions.length > 0) {
            suggestions.forEach(text => {
                const btn = document.createElement('button');
                btn.className = 'suggestion-btn';
                btn.textContent = text;
                suggestionsContainer.appendChild(btn);
            });
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // --- Event Listeners ---
    chatbotFab.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSendMessage(input.value.trim());
        input.value = '';
        sendBtn.disabled = true;
    });

    input.addEventListener('input', () => {
        sendBtn.disabled = input.value.trim() === '' || isLoading;
    });

    suggestionsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-btn')) {
            const suggestionText = e.target.textContent;
            input.value = suggestionText;
            handleSendMessage(suggestionText);
            input.value = '';
            sendBtn.disabled = true;
        }
    });
});