// PDF Upload Function
async function uploadPDFs() {
    const fileInput = document.getElementById('pdfUpload');
    const statusText = document.getElementById('uploadStatus');

    if (fileInput.files.length === 0) {
        alert("Atleast one PDF file select!");
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append("files", fileInput.files[i]);
    }

    statusText.innerText = "PDFs upload and processing ...";

    try {
        const response = await fetch('/upload-pdfs/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            statusText.innerText = "Success! Files processed.";
            statusText.style.color = "#34d399";
        } else {
            statusText.innerText = "Error: " + (data.detail || "Upload failed.");
            statusText.style.color = "#f87171";
        }
    } catch (error) {
        statusText.innerText = "Server error!";
        statusText.style.color = "#f87171";
        console.error("Error:", error);
    }
}

// Chat Send Function
async function handleSendMessage(event) {
    event.preventDefault();

    const questionInput = document.getElementById('questionInput');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');

    const question = questionInput.value.trim();
    if (!question) return;

    // User message screen par add karein
    chatMessages.innerHTML += `
        <div class="message user-message" style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
            <div class="message-content" style="background: #4f46e5; color: white; padding: 10px 15px; border-radius: 8px; max-width: 70%;">
                <p>${question}</p>
            </div>
        </div>
    `;

    questionInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Typing indicator shows
    typingIndicator.style.display = 'flex';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        typingIndicator.style.display = 'none';

        let botAnswer = data.answer || "No answer found.";

        // AI message screen par add karein
        chatMessages.innerHTML += `
            <div class="message ai-message" style="display: flex; margin-bottom: 10px;">
                <div class="message-icon" style="margin-right: 10px;"><i class="fa-solid fa-robot"></i></div>
                <div class="message-content" style="background: #1e293b; color: #f1f5f9; padding: 10px 15px; border-radius: 8px; max-width: 70%;">
                    <p>${botAnswer.replace(/\n/g, '<br>')}</p>
                </div>
            </div>
        `;
    } catch (error) {
        typingIndicator.style.display = 'none';
        chatMessages.innerHTML += `
            <div class="message ai-message">
                <div class="message-content" style="background: #7f1d1d; color: white; padding: 10px; border-radius: 8px;">
                    <p>Error: Server se rabta nahi ho saka.</p>
                </div>
            </div>
        `;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}