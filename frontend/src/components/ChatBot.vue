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
        <div class="bubble" @mouseenter="hoverIndex = idx" @mouseleave="hoverIndex = null">
          <span v-html="msg.text"></span>
          <button
            v-if="hoverIndex === idx"
            class="copy-btn"
            @click="copyMessage(msg.text)"
            title="Copy message"
            aria-label="Copy message"
          >
            📋
          </button>
        </div>
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

import { ref, nextTick, onMounted  } from 'vue'
import emitter from '../eventBus' 

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([
  { from: 'bot', text: 'Hello! I can classify products by HTSUS. If you want to know the HTSUS code of a product, please give me the product description and origin country of the product.' }
])

const hoverIndex = ref(null)

function copyMessage(text) {
  // Strip HTML tags if you want pure text
  const el = document.createElement('div')
  el.innerHTML = text
  const plainText = el.textContent || el.innerText || ''

  navigator.clipboard.writeText(plainText).then(() => {
    console.log("copied to clipboard") // You can replace this with nicer UI if you want
  })
}

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

async function scrollToBottom() {
  await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

const classificationBlocks = ref([]); // changed to ref for reactivity
const currentIndex = ref(0);

// const hasMoreBlocks = computed(() => {
//   return classificationBlocks.value.length > currentIndex.value;
// });

// Listen for emitted results
onMounted(async () => {
    emitter.on('sentUserPostRequest', async (data) => {
    messages.value.push({ from: 'user', text: data });
    await scrollToBottom();
  });

  emitter.on('sentPostRequest', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })

  emitter.on('htsusResult', async ({ data, linksHtml }) => {
    console.log('Received in chatbot:', data);
    
    console.log("links: ", linksHtml);

    classificationBlocks.value = parseClassification(data.classification);
    currentIndex.value = 0;

    const firstBatch = getNextBlocks(3, linksHtml);
    const textToShow = firstBatch
      ? firstBatch : "No classification data found.";

    console.log("text to show is ", textToShow)

    messages.value.push({ from: 'bot', text: textToShow });

    await scrollToBottom();
  })

  emitter.on('sentUserCalculationRequest', async (data) => {
    messages.value.push({ from: 'user', text: data });
    await scrollToBottom();
  })
  
  emitter.on('sentCalculationRequest', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })

  emitter.on('landedCostResult', async (data) => {
    console.log("Received landing data: ", data) 
    const formatted2 = formatLandingBreakdown(data)
    messages.value.push({ from: 'bot', text: formatted2 });
    await scrollToBottom();
  })

  emitter.on('botError', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })
})

// get blocks from chatbot htsus output
function parseClassification(rawText) {
  if (!rawText) return [];

  const matches = rawText.match(/\d+\.\s+HTSUS Code:.*?(?=(?:\n\d+\.|$))/gs);
  return matches || [];
}

// format individual blocks
function formatBlock(block, linkHtml) {
  const subtitles = [
    'HTSUS Code:',
    // 'General Duty Tax Rate:',
    // 'Special Duty Tax Rate:',
    // 'Column 2 Rate (for countries without normal trade relations with US):',
    // 'Additional Duties:',
    'Official Product Description:',
    'Confidence Score:',
    'Reason:',
    // 'Country of Origin:',
    'Total HTS Duty Tax Rate:'
  ];

  let escaped = block
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  subtitles.forEach(sub => {
    const re = new RegExp(sub.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    escaped = escaped.replace(re, `<b>${sub}</b>`);
  });

  escaped = escaped.replace(/\n/g, '<br>').trim();

  // Append the corresponding link HTML (assumed to be safe and already escaped)
  
  console.log("linkHtml in formatBlock is ", linkHtml)
  if (linkHtml) {
    const cleanUrl = linkHtml.replace(/^"+|"+$/g, ''); // remove leading/trailing quotes if any
    escaped += `<br><a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">View HTSUS Details</a>`;
  }

  return escaped;
}

function getNextBlocks(count = 3, links) {
  console.log("LINKS ARE: ", links)
  const next = classificationBlocks.value.slice(currentIndex.value, currentIndex.value + count);
  const linksForNext = links.slice(currentIndex.value, currentIndex.value + count);
  currentIndex.value += count;

  if (next.length === 0) return null;

  return next.map((block, i) => formatBlock(block, linksForNext[i])).join('<hr style="border:none;border-top:1px solid #ccc;margin:12px 0;">');
}

// Show more button handler
// async function showMoreCodes() {
//   const nextBlocks = getNextBlocks(3);
//   if (!nextBlocks) {  // check for null
//     messages.value.push({ from: 'bot', text: "All possible HTSUS codes have been shown." });
//   } else {
//     messages.value.push({ from: 'bot', text: nextBlocks });
//   }
//   await nextTick();
//   if (messagesContainer.value) {
//     messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
//   }
// }


// // Format the JSON result into readable chat text
// function formatClassification(rawText) {
//   if (!rawText) return "No classification data found.";

//   // Match each numbered classification block (e.g., "1. HTSUS Code:...")
//   const parts = rawText.match(/\d+\.\s+HTSUS Code:.*?(?=(?:\n\d+\.|$))/gs);
//   if (!parts) return "No classification blocks found.";

//   const subtitles = [
//     'HTSUS Code:',
//     'General Duty Tax Rate:',
//     'Special Duty Tax Rate:',
//     'Column 2 Rate (for countries without normal trade relations with US):',
//     'Additional Duties:',
//     'Official Product Description:',
//     'Confidence Score:',
//     'Reason:',
//     'Country of Origin:',
//     'Total HTS Duty Tax Rate:'
//   ];

//   const formattedParts = parts.map(block => {
//     // Escape HTML
//     let escaped = block
//       .replace(/&/g, "&amp;")
//       .replace(/</g, "&lt;")
//       .replace(/>/g, "&gt;");

//     // Bold each subtitle
//     subtitles.forEach(sub => {
//       const re = new RegExp(sub.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
//       escaped = escaped.replace(re, `<b>${sub}</b>`);
//     });

//     // Add line breaks
//     escaped = escaped.replace(/\n/g, '<br>');

//     return escaped.trim();
//   });

//   return formattedParts.join('<hr style="border:none;border-top:1px solid #ccc;margin:12px 0;">');
// }

function formatLandingBreakdown(data) {
  if (!data) return "No landing cost data available.";

  const landingCost = data.landing_cost;
  const dutyTotal = data.duty_total;
  const mrnDuty = data.mrn_duty;
  const mrnRate = data.mrn_rate;
  const subtotal = data.subtotal;
  const tax301Duty = data.tax301_duty;
  const tax301Rate = data.tax301_rate;
  const vatRate = data.vat_rate;
  const vatTotal = data.vat_total;
  const regular = data.regular;

  function fmtMoney(value) {
    return `$${Number(value).toFixed(2)}`;
  }

  const mrnRateDisplay = regular ? `${mrnRate}%` : mrnRate;

  return `
    <table style="width: 100%; border-collapse: collapse; color: #ececf1;">
      <tbody>
        <tr>
          <td style="padding: 6px; border-bottom: 1px solid #444;">Subtotal</td>
          <td style="padding: 6px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(subtotal)}</td>
        </tr>
        <tr>
          <td style="padding: 6px; border-bottom: 1px solid #444;">MRN Duty (${mrnRateDisplay})</td>
          <td style="padding: 6px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(mrnDuty)}</td>
        </tr>
        <tr>
          <td style="padding: 6px; border-bottom: 1px solid #444;">301 Duty (${tax301Rate}%)</td>
          <td style="padding: 6px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(tax301Duty)}</td>
        </tr>
        <tr>
          <td style="padding: 6px; border-bottom: 1px solid #444;">Total Duties</td>
          <td style="padding: 6px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(dutyTotal)}</td>
        </tr>
        <tr>
          <td style="padding: 6px; border-bottom: 1px solid #444;">VAT (${vatRate}%)</td>
          <td style="padding: 6px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(vatTotal)}</td>
        </tr>
        <tr>
          <td style="padding: 6px; font-weight: bold;">Total Landed Cost</td>
          <td style="padding: 6px; font-weight: bold; text-align: right;">${fmtMoney(landingCost)}</td>
        </tr>
      </tbody>
    </table>
  `;
  
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
  position: relative;
}
.copy-btn {
  position: absolute;
  bottom: -25px;    /* 6px from bottom */
  right: 6px;      /* 6px from right */
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
  color: #999;
  padding: 2px;
  border-radius: 4px;
}

.copy-btn:hover {
  opacity: 1;
  color: #4f46e5; /* or your accent color */
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

.show-more-btn {
  margin: 12px 16px;
  padding: 8px 16px;
  border-radius: 10px;
  border: none;
  background-color: #4f46e5;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.18s ease;
}

.show-more-btn:hover {
  background-color: #6366f1;
}

.bubble a {
  color: #4ea9ff;             /* Light blue default */
  text-decoration: underline; /* Underlined by default */
}

.bubble a:visited {
  color: #c084fc;             /* Light purple when visited */
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