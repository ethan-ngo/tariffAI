<template>
  <div class="chatbot-container">
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['chat-row', msg.from === 'bot' ? 'bot' : 'user']"
      >
        <img
          v-if="msg.from === 'bot'"
          class="avatar"
          src="https://randomuser.me/api/portraits/men/32.jpg"
          alt="Bot"
        />
        <div class="bubble" v-html="msg.text"></div>
        <div v-if="msg.from === 'user'" class="spacer"></div>
      </div>
    </div>
    <form class="chat-input-row" @submit.prevent="sendMessage">
      <input
        v-model="input"
        type="text"
        placeholder="Type your message..."
        class="chat-input"
        @keydown.enter.exact.prevent="sendMessage"
      />
      <button type="submit" class="send-btn">Send</button>
    </form>
  </div>
</template>

<script setup>

import { ref, nextTick, onMounted } from 'vue'
import emitter from '../eventBus' 

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([
  { from: 'bot', text: 'Hello! I can classify products by HTSUS. If you want to know the HTSUS code of a product, please give me the product description and origin country of the product.' }
])

async function sendMessage() {
  if (!input.value.trim()) return
  messages.value.push({ from: 'user', text: input.value })
  
  // Auto-scroll to bottom
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
  const query = input.value
  input.value = ''
  // Call your backend API
  try {
    const response = await fetch('http://127.0.0.1:5000/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query })
    })
    const data = await response.json()
    messages.value.push({ from: 'bot', text: data.message })
  } catch (e) {
    messages.value.push({ from: 'bot', text: "Sorry, I couldn't process your request." })
  }

  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Listen for emitted HTSUS result
onMounted(() => {
  emitter.on('sentPostRequest', (data) => {
    messages.value.push({ from: 'bot', text: data });
  })

  emitter.on('htsusResult', (data) => {
    console.log('Received in chatbot:', data)
    const formatted = formatClassification(data.classification);
    messages.value.push({ from: 'bot', text: formatted });
  })
})

// Format the JSON result into readable chat text
function formatClassification(rawText) {
  if (!rawText) return "No classification data found.";

  // Match each numbered classification block (e.g., "1. HTSUS Code:...")
  const parts = rawText.match(/\d+\.\s+HTSUS Code:.*?(?=(?:\n\d+\.|$))/gs);
  if (!parts) return "No classification blocks found.";

  const subtitles = [
    'HTSUS Code:',
    'General Duty Tax Rate:',
    'Special Duty Tax Rate:',
    'Column 2 Rate (for countries without normal trade relations with US):',
    'Additional Duties:',
    'Official Product Description:',
    'Confidence Score:',
    'Reason:',
    'Country of Origin:',
    'Total HTS Duty Tax Rate:'
  ];

  const formattedParts = parts.map(block => {
    // Escape HTML
    let escaped = block
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold each subtitle
    subtitles.forEach(sub => {
      const re = new RegExp(sub.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
      escaped = escaped.replace(re, `<b>${sub}</b>`);
    });

    // Add line breaks
    escaped = escaped.replace(/\n/g, '<br>');

    return escaped.trim();
  });

  return formattedParts.join('<hr style="border:none;border-top:1px solid #ccc;margin:12px 0;">');
}

</script>

<style scoped>
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 550px;
  width: 80%;
  background: #23232a;
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 rgba(0,0,0,0.18);
  overflow: hidden;
  border: 1.5px solid #292933;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 16px 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
}

.chat-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.chat-row.bot {
  flex-direction: row;
}

.chat-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
  background: #18181b;
  border: 2px solid #353545;
  flex-shrink: 0;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 1.04rem;
  line-height: 1.5;
  background: #343541;
  color: #ececf1;
  box-shadow: 0 2px 8px 0 rgba(20,20,20,0.10);
  word-break: break-word;
  word-wrap: break-word;
}

.chat-row.user .bubble {
  background: #4f46e5;
  color: #fff;
  border-bottom-right-radius: 6px;
  border-bottom-left-radius: 16px;
  border-top-right-radius: 16px;
  border-top-left-radius: 16px;
}

.chat-row.bot .bubble {
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 16px;
  border-top-right-radius: 16px;
  border-top-left-radius: 16px;
  text-align: left !important;
}

.spacer {
  width: 38px;
  flex-shrink: 0;
}

.chat-input-row {
  display: flex;
  padding: 12px 16px;
  background: #202123;
  border-top: 1px solid #292933;
  gap: 8px;
}

.chat-input {
  flex: 1 1 0;
  min-width: 0;
  padding: 10px 24px;
  border-radius: 12px;
  border: none;
  background: #343541;
  color: #ececf1;
  font-size: 1rem;
  outline: none;
}

.chat-input::placeholder {
  color: #8e8ea0;
}

.send-btn {
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0 28px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s;
  flex-shrink: 0;
}

.send-btn:hover {
  background: #6366f1;
}

/* Tablet styles */
@media (max-width: 1024px) {
  .chatbot-container {
    height: 600px;
    max-width: 100%;
    margin: 0 auto;
  }
  
  .chat-messages {
    padding: 20px 12px 10px 12px;
  }
  
  .bubble {
    font-size: 1rem;
    padding: 10px 14px;
  }
  
  .chat-input {
    padding: 8px 20px;
    font-size: 0.95rem;
  }
  
  .send-btn {
    padding: 0 24px;
    font-size: 0.95rem;
  }
}

/* Mobile landscape */
@media (max-width: 768px) {
  .chatbot-container {
    height: 500px;
    border-radius: 12px;
  }
  
  .chat-messages {
    padding: 16px 10px 8px 10px;
    gap: 10px;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
  }
  
  .bubble {
    max-width: 85%;
    font-size: 0.95rem;
    padding: 8px 12px;
  }
  
  .spacer {
    width: 32px;
  }
  
  .chat-input-row {
    padding: 10px 12px;
    gap: 6px;
  }
  
  .chat-input {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
  
  .send-btn {
    padding: 0 20px;
    font-size: 0.9rem;
  }
}

/* Mobile portrait */
@media (max-width: 480px) {
  .chatbot-container {
    height: 450px;
    border-radius: 10px;
  }
  
  .chat-messages {
    padding: 12px 8px 6px 8px;
    gap: 8px;
  }
  
  .avatar {
    width: 28px;
    height: 28px;
  }
  
  .bubble {
    max-width: 90%;
    font-size: 0.9rem;
    padding: 6px 10px;
    border-radius: 12px;
    white-space: normal; /* normal so <br> works */
    line-height: 1.4;
  }
  
  .chat-row.user .bubble {
    border-bottom-right-radius: 4px;
    border-bottom-left-radius: 12px;
    border-top-right-radius: 12px;
    border-top-left-radius: 12px;
  }
  
  .chat-row.bot .bubble {
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 12px;
    border-top-right-radius: 12px;
    border-top-left-radius: 12px;
    text-align: left !important; /* align chat's msgs to the left */
  }
  
  .spacer {
    width: 28px;
  }
  
  .chat-input-row {
    padding: 8px 10px;
  }
  
  .chat-input {
    padding: 6px 12px;
    font-size: 0.85rem;
    border-radius: 10px;
  }
  
  .send-btn {
    padding: 0 16px;
    font-size: 0.85rem;
    border-radius: 8px;
  }
}

/* Very small screens */
@media (max-width: 320px) {
  .chatbot-container {
    height: 400px;
  }
  
  .bubble {
    font-size: 0.85rem;
    padding: 5px 8px;
  }
  
  .chat-input {
    padding: 5px 10px;
    font-size: 0.8rem;
  }
  
  .send-btn {
    padding: 0 12px;
    font-size: 0.8rem;
  }
}
</style>