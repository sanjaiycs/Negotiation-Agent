let sessionId = null;
const productInput = document.getElementById("product");
const budgetInput = document.getElementById("budget");
const sellerMsgInput = document.getElementById("sellerMsg");
const chatWindow = document.getElementById("chat");

// Allow sending messages with the Enter key
sellerMsgInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const product = productInput.value.trim();
    const budgetStr = budgetInput.value.trim();
    const sellerMsg = sellerMsgInput.value.trim();

    // --- Input Validation ---
    if (!product || !budgetStr) {
        addMessage("System", "Please set a Product and your Budget before starting.", "error");
        return;
    }
    if (!sellerMsg) {
        addMessage("System", "Please enter the seller's offer price.", "error");
        return;
    }

    const budget = parseInt(budgetStr);
    const offer = parseInt(sellerMsg);

    if (isNaN(budget) || isNaN(offer) || budget <= 0 || offer <= 0) {
        addMessage("System", "Budget and Offer must be positive numbers.", "error");
        return;
    }

    // --- UI Updates ---
    addMessage("You (Seller)", `Offer: ₹${offer.toLocaleString('en-IN')}`, "seller");
    sellerMsgInput.value = "";
    productInput.disabled = true; // Lock product/budget during negotiation
    budgetInput.disabled = true;

    const loadingElem = addMessage("Buyer Agent", '🤔 Thinking...', "loading");

    try {
        // --- API Call ---
        const apiUrl = `${window.location.origin}/api/negotiate`;
        const res = await fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product,
                budget,
                seller_message: sellerMsg,
                session_id: sessionId
            })
        });

        loadingElem.remove();

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "An unknown server error occurred.");
        }

        const data = await res.json();
        sessionId = data.session_id;

        const r = data.response;
        addMessage("Buyer Agent", r.message, "buyer");

    } catch (error) {
        if (loadingElem.parentNode) {
            loadingElem.remove();
        }
        addMessage("System", `Error: ${error.message}`, "error");
    }
}

function addMessage(sender, text, cls) {
    const div = document.createElement("div");
    div.className = `message ${cls}`;
    const strong = document.createElement("strong");
    strong.textContent = `${sender}:`;
    div.appendChild(strong);
    div.append(document.createTextNode(text));

    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return div;
}

async function resetSession() {
    if (sessionId) {
        try {
            const apiUrl = `${window.location.origin}/api/reset`;
            await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId })
            });
        } catch (error) {
            console.error("Session reset failed:", error);
        }
    }

    sessionId = null;
    chatWindow.innerHTML = "";
    productInput.value = "";
    budgetInput.value = "";
    sellerMsgInput.value = "";

    // Unlock inputs
    productInput.disabled = false;
    budgetInput.disabled = false;

    addMessage("System", "New negotiation session started. Please set your product and budget.", "system");
    productInput.focus();
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    resetSession();
});
