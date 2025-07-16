<template>
  <aside class="sidebar" :class="{ 'mobile-hidden': !props.showSidebar }">
    <header class="sidebar-header">
      <div class="header-left">
        <h2>Inventory</h2>
        <button class="download-btn" @click="downloadItems" title="Download Report">
          <img src="..\assets\download-file-svgrepo-com.png" class="download-icon" />
        </button>
      </div>
      <button class="close-btn" @click="emit('toggleSidebar')">×</button>
    </header>

    <section class="sidebar-content">
      <div v-if="items.length === 0" class="empty-cart">
        <p>Submit calculations to get started.</p>
      </div>
      <ul v-else class="cart-list">
        <li v-for="item in items" :key="item.id" class="cart-item">
          <button class="remove-btn" @click="removeItem(item.id)">
            <svg xmlns="http://www.w3.org/2000/svg" class="trash-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div class="item-info">
            <div class="item-name">{{ item.prod_desc }}</div>
            <div class="item-code">{{ item.htsus }}</div>
            <div class="item-price">${{ item.landing_cost.toFixed(2) }}</div>
          </div>
          <div class="item-qty">
            <button @click="updateQuantity(item.id, -1)" :disabled="item.quantity <= 1">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, 1)">+</button>
          </div>
        </li>
      </ul>
    </section>

    <footer class="sidebar-footer">
      <div class="total-label">Total</div>
      <div class="total-value">${{ total.toFixed(2) }}</div>
    </footer>
  </aside>

  <div v-if="props.showSidebar" class="sidebar-overlay" @click="emit('toggleSidebar')"></div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue'
import emitter from '../eventBus' 
import { createPDF } from '@/utils/report'
const props = defineProps({
  showSidebar: Boolean
})

const emit = defineEmits(['toggleSidebar'])

const items = ref([])
onMounted(async () => {
  emitter.on('landedCostResult2', (data) => {
    console.log("Received landedCostResult data in item cart:", data); 

    try {
      const newId = items.value.length > 0
        ? Math.max(...items.value.map(item => item.id || 0)) + 1
        : 1;

      items.value.push({
        id: newId,
        ...data
      });

      // Put log inside try block
      console.log("Plain items data: ", JSON.parse(JSON.stringify(items.value)));
    } catch (err) {
      console.error("Error after pushing item:", err);
    }
  });
})

const total = computed(() =>
  items.value.reduce((sum, item) => sum + item.landing_cost, 0)
)

function calcLanding(prod_value, quantity, shipping, insurance, MRN, tax301, VAT) {
  const subtotal = prod_value * quantity + shipping + insurance
  const mrn_duty = MRN / 100 * subtotal
  const tax301_duty = tax301 / 100 * subtotal
  const vat_duty = VAT / 100 * (mrn_duty + tax301_duty + subtotal)
  
  const landing = subtotal + mrn_duty + tax301_duty + vat_duty
  return {
    "landing": landing,
    "mrn_duty": mrn_duty,
    "tax301_duty": tax301_duty, 
    "vat_total": vat_duty
  }
}
function updateQuantity(id, change) {
  items.value = items.value.map(item => {
    if (item.id === id) {
      const newQuantity = Math.max(1, item.quantity + change);
      const landing = calcLanding(
        item.prod_value || 0,
        newQuantity,
        item.shipping || 0,
        item.insurance || 0,
        item.mrn_rate || 0,
        item.tax301_rate || 0,
        item.vat_rate || 0
      );
      return {
        ...item,
        quantity: newQuantity,
        landing_cost: landing.landing,
        mrn_duty: landing.mrn_duty,
        tax301_duty: landing.tax301_duty,
        vat_total: landing.vat_total,
      };
    }
    return item;
  });
}

function removeItem(id) {
  items.value = items.value.filter(item => item.id !== id)
}

function downloadItems(){
  createPDF(items.value)
}
</script>

<style scoped>
.sidebar {
  width: 325px;
  height: 100vh;
  background: #18181b;
  color: #ececf1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #23232a;
  box-shadow: 2px 0 16px 0 rgba(0, 0, 0, 0.25);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}

.sidebar.mobile-hidden {
  transform: translateX(-100%);
}

.sidebar-header {
  padding: 24px 20px 16px 20px;
  border-bottom: 1px solid #23232a;
  font-size: 1.3rem;
  font-weight: 700;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #18181b;
  color: #ececf1;
}

.close-btn {
  font-size: 1.5rem;
  background: transparent;
  border: none;
  color: #ececf1;
  cursor: pointer;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  background: #202123;
}

.empty-cart {
  text-align: center;
  color: #8e8ea0;
  margin-top: 40px;
}

.cart-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.cart-item {
  display: flex;
  align-items: center;
  position: relative;
  background: linear-gradient(135deg, #23232a 80%, #2d2d36 100%);
  border-radius: 20px;
  margin: 0 18px 22px 18px;
  padding: 22px;
  box-shadow: 0 6px 32px rgba(40, 40, 60, 0.25), 0 1.5px 6px rgba(0, 0, 0, 0.1);
  border: 1.5px solid #292933;
}

.remove-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  background: #2d232a;
  border: none;
  border-radius: 50%;
  padding: 6px;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transition: background 0.2s, opacity 0.2s;
}

.cart-item:hover .remove-btn {
  opacity: 1;
  pointer-events: auto;
}

.remove-btn:hover {
  background: #3a1a1a;
}

.trash-icon {
  width: 18px;
  height: 18px;
  color: #ff7b7b;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-weight: 600;
  font-size: 1.13rem;
  margin-bottom: 2px;
  color: #ececf1;
}

.item-code {
  font-size: 0.97rem;
  color: #b4bcd0;
  margin-bottom: 8px;
}

.item-price {
  font-size: 1rem;
  color: #ececf1;
  margin-top: 4px;
}

.item-qty {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-left: 18px;
  gap: 8px;
}

.item-qty button {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: #23232a;
  color: #ececf1;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
}

.item-qty button:disabled {
  color: #444;
  cursor: not-allowed;
}

.item-qty span {
  min-width: 22px;
  text-align: center;
  font-size: 1.08rem;
  color: #ececf1;
}

.sidebar-footer {
  padding: 18px 24px;
  border-top: 1px solid #23232a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #18181b;
  font-size: 1.1rem;
  font-weight: 600;
}

.total-label {
  color: #b4bcd0;
}

.total-value {
  color: #ececf1;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.download-btn {
  font-size: 1.2rem;
  background: transparent;
  border: none;
  color: #ececf1;
  cursor: pointer;
}
.download-btn:hover {
  color: #8ab4f8;
}
.download-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
}
</style>
