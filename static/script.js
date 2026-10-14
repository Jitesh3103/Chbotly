
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-btn");

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(text, sender) {
    const messageElement = document.createElement("div");
    messageElement.className = sender === "user"
        ? "message user-message"
        : "message bot-message";

    const content = document.createElement("div");
    content.className = "message-content";

    if (sender === "user") {
        // User input is always plain text.
        content.textContent = text;
    } else {
        // Render bot text and convert URLs into safe clickable links.
        const urlPattern = /(https?:\/\/[^\s<]+)/g;
        const parts = String(text).split(urlPattern);

        parts.forEach((part) => {
            if (/^https?:\/\//i.test(part)) {
                const cleanUrl = part.replace(/[.,!?;:)]+$/, "");
                const trailingText = part.slice(cleanUrl.length);

                try {
                    const parsedUrl = new URL(cleanUrl);

                    if (parsedUrl.protocol === "http:" || parsedUrl.protocol === "https:") {
                        const link = document.createElement("a");
                        link.href = parsedUrl.href;
                        link.textContent = cleanUrl;
                        link.target = "_blank";
                        link.rel = "noopener noreferrer";
                        link.className = "chat-link";
                        content.appendChild(link);
                    } else {
                        content.appendChild(document.createTextNode(cleanUrl));
                    }
                } catch {
                    content.appendChild(document.createTextNode(cleanUrl));
                }

                if (trailingText) {
                    content.appendChild(document.createTextNode(trailingText));
                }
            } else {
                // Preserve new lines in the bot's response.
                content.appendChild(document.createTextNode(part));
            }
        });
    }

    messageElement.appendChild(content);
    chatBox.appendChild(messageElement);
    scrollToBottom();
    return messageElement;
}

function showTyping() {
    const typing = document.createElement("div");
    typing.className = "message bot-message typing-message";
    typing.id = "typing-indicator";
    typing.textContent = "Chbotly is typing...";
    chatBox.appendChild(typing);
    scrollToBottom();
}

function removeTyping() {
    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();
}

async function sendMessage(message) {
    const cleanMessage = message.trim();
    if (!cleanMessage) return;

    addMessage(cleanMessage, "user");
    messageInput.value = "";
    sendButton.disabled = true;
    showTyping();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: cleanMessage })
        });

        if (!response.ok) {
            throw new Error("Server returned an error.");
        }

        const data = await response.json();
        removeTyping();
        addMessage(data.reply || "Sorry, I couldn't find an answer.", "bot");
    } catch (error) {
        removeTyping();
        addMessage(
            "I couldn't connect to the server. Make sure Flask is running, then try again.",
            "bot"
        );
        console.error("Chat error:", error);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

chatForm.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(messageInput.value);
});

// Quick-question buttons already present in index.html.
document.querySelectorAll(".quick-btn, .quick-question").forEach((button) => {
    button.addEventListener("click", () => {
        const question = button.dataset.message || button.textContent.trim();
        sendMessage(question);
    });
});
