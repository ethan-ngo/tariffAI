<template>
  <aside class="sidebar" :class="{ 'mobile-hidden': !props.showSidebar }">
    <header class="sidebar-header">
      <h2>Shopping Cart</h2>
      <button class="close-btn" @click="emit('toggleSidebar')">×</button>
    </header>

    <section class="sidebar-content">
      <div v-if="items.length === 0" class="empty-cart">
        <p>Your cart is empty.</p>
      </div>
      <ul v-else class="cart-list">
        <li v-for="item in items" :key="item.id" class="cart-item">
          <button class="remove-btn" @click="removeItem(item.id)">
            <svg xmlns="http://www.w3.org/2000/svg" class="trash-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div class="item-info">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-code">{{ item.htsus }}</div>
            <div class="item-price">${{ item.price.toFixed(2) }}</div>
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
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  showSidebar: Boolean
})

const emit = defineEmits(['toggleSidebar'])

const items = ref([
  { id: 1, name: "Premium Wireless Headphones", htsus: "8518.30.2000", price: 199.99, quantity: 1 },
  { id: 2, name: "Smart Watch", htsus: "9102.12.8000", price: 299.99, quantity: 2 },
  { id: 3, name: "Bluetooth Speaker", htsus: "8518.22.0000", price: 79.99, quantity: 1 },
  { id: 4, name: "Laptop Stand", htsus: "7615.19.5000", price: 49.99, quantity: 1 },
  { id: 5, name: "USB-C Cable", htsus: "8544.42.2000", price: 14.99, quantity: 3 },
  { id: 6, name: "Wireless Mouse", htsus: "8471.60.9050", price: 39.99, quantity: 1 },
  { id: 7, name: "External SSD", htsus: "8471.70.6000", price: 129.99, quantity: 1 }
])

const total = computed(() =>
  items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
)

function updateQuantity(id, change) {
  items.value = items.value.map(item =>
    item.id === id
      ? { ...item, quantity: Math.max(1, item.quantity + change) }
      : item
  )
}

function removeItem(id) {
  items.value = items.value.filter(item => item.id !== id)
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
