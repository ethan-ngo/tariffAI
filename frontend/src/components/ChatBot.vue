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
          :src="botAvatar"
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
            <img src="../assets/copy.png" alt="Copy" class="copy-icon" />
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
<script>
import botAvatar from '@/assets/robot.jpg'

export default {
  data() {
    return {
      botAvatar
    }
  }
}
</script>

<script setup>

import { ref, nextTick, onMounted  } from 'vue'
import emitter from '../eventBus' 
import { create_table_PDF } from '@/utils/report'

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([
  { from: 'bot', text: 'Hello! I can classify products by HTSUS. If you want to know the HTSUS code of a product, please give me the product description and origin country of the product.' }
])

const hoverIndex = ref(null)

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

async function scrollToTop() {
  await nextTick();

  if (!messagesContainer.value) return;

  const container = messagesContainer.value;
  const botMessages = container.querySelectorAll('.chat-row.bot');
  if (botMessages.length === 0) return;

  const lastBotMessage = botMessages[botMessages.length - 1];

  const containerRect = container.getBoundingClientRect();
  const messageRect = lastBotMessage.getBoundingClientRect();

  // How far is the message top from container top
  const offset = messageRect.top - containerRect.top;

  // Adjust scrollTop by current scroll and the offset
  container.scrollTop += offset;
}

// allows user to copy messages from the chatbot
function copyMessage(text) {
  // Strip HTML tags if you want pure text
  const el = document.createElement('div')
  el.innerHTML = text
  const plainText = el.textContent || el.innerText || ''

  navigator.clipboard.writeText(plainText).then(() => {
    console.log("copied to clipboard") // You can replace this with nicer UI if you want
  })
}


const classificationBlocks = ref([]); // changed to ref for reactivity
const currentIndex = ref(0);

// Listen for emitted results
onMounted(async () => {
  // listen if user sent request to classify a product
  emitter.on('sentUserPostRequest', async (data) => {
    messages.value.push({ from: 'user', text: data });
    await scrollToBottom();
  });

  // listen for if chatbot began classifying a product
  emitter.on('sentPostRequest', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })

  // listen for final classification output
  emitter.on('htsusResult', async ({ data, linksHtml }) => {
    // get the top 3 options and format each block properly
    classificationBlocks.value = parseClassification(data.classification);
    currentIndex.value = 0;
    const firstBatch = getNextBlocks(3, linksHtml);
    const textToShow = firstBatch
      ? firstBatch : "No classification data found.";

    messages.value.push({ from: 'bot', text: textToShow });

    await scrollToTop();
  })

  emitter.on('image_upload', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })
  // listen for if user wants the final landing cost
  emitter.on('sentUserCalculationRequest', async (data) => {
    messages.value.push({ from: 'user', text: data });
    await scrollToBottom();
  })
  
  // listen for if chatbot began the calculation
  emitter.on('sentCalculationRequest', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })

  // listen for final landing cost
  emitter.on('landedCostResult', async ( data ) => {
    const formatted2 = formatLandingBreakdown(data)
    messages.value.push({ from: 'bot', text: formatted2 });
    await scrollToTop();
  })

  // listen for if user wants to compare countries
  emitter.on('wantCompareCountriesRequest', async (data) => {
    messages.value.push({ from: 'user', text: data });
    await scrollToBottom();
  }) 

  // listen for if chatbot began processing countries
  emitter.on('sentCompareCountriesRequest', async (data) => {
    messages.value.push({ from: 'bot', text: data });
    await scrollToBottom();
  })

  // listen for final compare countries result
  emitter.on('compareCountriesRes', async (data) => {
    console.log("received compare results final: ", data)
    const pdfUrl = create_table_PDF(data);
    messages.value.push({ 
      from: 'bot', 
      text: `Download your country comparison report: <a href="${pdfUrl}" download="country_comparison.pdf" target="_blank">country_comparison.pdf</a>` 
    });

    await scrollToTop();
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
  const next = classificationBlocks.value.slice(currentIndex.value, currentIndex.value + count);
  const linksForNext = links.slice(currentIndex.value, currentIndex.value + count);
  currentIndex.value += count;

  if (next.length === 0) return null;

  return next.map((block, i) => formatBlock(block, linksForNext[i])).join('<hr style="border:none;border-top:1px solid #ccc;margin:12px 0;">');
}

function formatLandingBreakdown(data) {
  if (!data) return "No landing cost data available.";

  const landingCost = data.landing_cost;
  const dutyTotal = data.duty_total;
  const mrnDuty = data.mrn_duty;
  const mrnRate = data.mrn_rate;
  const subtotal = data.subtotal;
  const tax301Duty = data.tax301_duty;
  const tax301Rate = data.tax301_rate;
  const reciprocalDuty = data.reciprocal_duty;
  const reciprocalTaxes = data.reciprocal_rates;
  const reciprocalTotalRate = data.reciprocal_total_rate;
  const vatRate = data.vat_rate;
  const vatTotal = data.vat_total;
  const regular = data.regular;
  const breakdown = data.breakdown;
  const VATLink = data.VAT_link;
  const htsLink = `https://hts.usitc.gov/search?query=${data.htsus_code}`
  const country = data.origin_country

  // console.log("Vat Link", VATLink)
  // console.log("htsLink", htsLink)
  console.log("reciprocal rate is ", reciprocalTotalRate, " duty is ", reciprocalDuty, " and all is ", reciprocalTaxes)

  function fmtMoney(value) {
    return `$${Number(value).toFixed(2)}`;
  }

  const mrnRateDisplay = regular ? `${mrnRate}%` : mrnRate;

  return `
    <table style="width: 100%; border-collapse: collapse; color: #ececf1;">
      <tbody>
        <tr>
          <td style="padding: 4px; border-bottom: 1px solid #444;">Subtotal</td>
          <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(subtotal)}</td>
        </tr>
        <tr>
          <td style="padding: 4px; border-bottom: 1px solid #444;">
            <a href="${htsLink}" target="_blank" rel="noopener noreferrer">
              Base Duty (${mrnRateDisplay} base rate)
            </a>
          </td>
          <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(mrnDuty)}</td>
        </tr>
        <tr>
          <td style="padding: 4px; border-bottom: 1px solid #444;">
            <a href="https://ustr.gov/issue-areas/enforcement/section-301-investigations/search" target="_blank" rel="noopener noreferrer">
              301 Duty (${tax301Rate}% rate)
            </a>
          </td>
          <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(tax301Duty)}</td>
        </tr>
        <tr>
          <td>
            ${reciprocalTaxes.length > 0 ? `
              <tr>
                <td style="padding: 4px; border-bottom: 1px solid #444;">
                  <a href="https://www.tradecomplianceresourcehub.com/2025/07/16/trump-2-0-tariff-tracker/" target="_blank" rel="noopener noreferrer">
                    Reciprocal Duty (${reciprocalTotalRate}% rate)
                  </a>
                </td>
                <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(reciprocalDuty)}</td>
              </tr>
              ${reciprocalTaxes.map(([rate, date]) => `
                <tr>
                  <td colspan="2" style="padding: 4px; border-bottom: 1px solid #444; font-size: 0.85em;">
                    – ${rate}% ${date}
                  </td>
                  <td style="padding: 4px; border-bottom: 1px solid #444;"></td>
                </tr>
              `).join("")}
            ` : ""}
          </td>
        </tr>
        <tr>
          <td style="padding: 4px; border-bottom: 1px solid #444;">Total Duties</td>
          <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(dutyTotal)}</td>
        </tr>
        <tr>
          <td style="padding: 4px; border-bottom: 1px solid #444;">
            <a href="${VATLink}" target="_blank" rel="noopener noreferrer">
              VAT (${vatRate}% rate)
            </a>
          </td>
          <td style="padding: 4px; border-bottom: 1px solid #444; text-align: right;">${fmtMoney(vatTotal)}</td>
        </tr>
        <tr>
          <td style="padding: 4px; font-weight: bold;">Total Landed Cost</td>
          <td style="padding: 4px; font-weight: bold; text-align: right;">${fmtMoney(landingCost)}</td>
        </tr>
        <tr>
          <td colspan="2" style="padding: 12px 6px 6px 6px; border-top: 1px solid #666;">
            <div style="margin-bottom: 4px;">Calculation Breakdown for ${country}</div>
            <ul style="margin: 0; padding-left: 18px; color: white; font-size: 0.9em;">
              ${breakdown.map(step => `<li>${step}</li>`).join("")}
            </ul>
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
  margin: 0 auto;   /* centers horizontally */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 16px 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 32px;
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
  object-position: center center; /* Adjust these values */
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
  bottom: -30px;    /* 6px from bottom */
  right: 4px;      /* 6px from right */
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
  color: #999;
  padding: 2px;
  border-radius: 4px;
  z-index: 9999;         /* ensures it appears above all */
}

.copy-icon {
  width: 20px;
  height: 20px;
  object-fit: contain; /* Keeps aspect ratio clean */
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

.bubble ::v-deep a {
  color: #4ea9ff; /* light blue */
  text-decoration: underline;
}

.bubble ::v-deep a:visited {
  color: #c084fc; /* light purple */
}

.country-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.tag {
  background: #e0e7ff;
  border-radius: 4px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
}
.remove-btn {
  background: none;
  border: none;
  margin-left: 6px;
  cursor: pointer;
  font-weight: bold;
  color: #4f46e5;
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