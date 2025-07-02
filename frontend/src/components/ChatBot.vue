<template>
  <div class="chatbot-container">
    <div class="chat-messages">
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
        <div class="bubble">{{ msg.text }}</div>
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
import { ref } from 'vue'

const input = ref('')
const messages = ref([
  { from: 'bot', text: 'Hello! How can I help you today?' }
])

function sendMessage() {
  if (!input.value.trim()) return
  messages.value.push({ from: 'user', text: input.value })
  // Simulate bot reply
  setTimeout(() => {
    messages.value.push({
      from: 'bot',
      text: "I'm a helpful bot! (This is a demo reply.)"
    })
  }, 700)
  input.value = ''
}
</script>

<style scoped>
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 500px;
  width: 380px;
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
}
.spacer {
  width: 38px;
}
.chat-input-row {
  display: flex;
  padding: 12px 16px;
  background: #202123;
  border-top: 1px solid #292933;
  gap: 8px;
}
.chat-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 12px;
  border: none;
  background: #343541;
  color: #ececf1;
  font-size: 1rem;
  outline: none;
}
.send-btn {
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0 18px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s;
}
.send-btn:hover {
  background: #6366f1;
}
</style>