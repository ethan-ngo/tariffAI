<template>
  <div id="app">
    <div v-if="!showSidebar" class="open-cart-btn-wrapper">
      <button class="open-cart-btn" @click="showSidebar = true">Open Cart</button>
    </div>
    <ItemCart :showSidebar="showSidebar" @toggleSidebar="showSidebar = !showSidebar" />
    <div class="main-content" :class="{ 'cart-open': showSidebar }">
      <div class="center-row">
        <div class="left-panel">
          <TariffForm msg="Product Classification & Landing Cost"/>
        </div>
        <div class="right-panel">
          <ChatBot />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TariffForm from './components/TariffForm.vue'
import ItemCart from './components/ItemCart.vue'
import ChatBot from './components/ChatBot.vue'

export default {
  name: 'App',
  components: {
    TariffForm,
    ItemCart,
    ChatBot
  },
  data() {
    return {
      showSidebar: false // <-- Add this line
    }
  }
}
</script>

<style>
html, body {
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  display: flex;
  min-height: 100vh;
  margin: 0;
  text-align: center;
}

.main-content {
  margin-left: 325px;
  width: calc(100vw - 325px);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-sizing: border-box;
  transition: margin-left 0.3s, width 0.3s;
}

.main-content:not(.cart-open) {
  margin-left: 0;
  width: 100vw;
}

.center-row {
  display: flex;
  gap: 30px;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.left-panel,
.right-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}

.left-panel {
  max-width: 420px;
  width: 100%;
  flex: 1;
}

.right-panel {
  max-width: 1000px;
  width: 100%;
  flex: 2;
}
.open-cart-btn {
  top: 20px;
  left: 20px;
  z-index: 1100;
  padding: 8px 12px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.open-cart-btn:hover {
  background: #6366f1;
}

/* Ensure components fill the panel and center content vertically */
.tariff-form-container,
.chatbot-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Tablet styles */
@media (max-width: 1200px) {
  .center-row {
    gap: 32px;
  }
  
  .left-panel {
    max-width: 380px;
  }
  
  .right-panel {
    max-width: 800px;
  }
}

/* Mobile landscape and small tablet */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 0;
  }
  .open-cart-btn {
    top: 12px;
    left: 12px;
    padding: 7px 10px;
    font-size: 0.95rem;
  }
}

/* Mobile portrait */
@media (max-width: 768px) {
  .main-content {
    padding: 10px 5px;
  }
  
  .center-row {
    gap: 15px;
    padding-top: 10px;
  }
}

/* Small mobile */
@media (max-width: 480px) {
  .main-content {
    padding: 5px;
  }
  
  .center-row {
    gap: 10px;
  }
}
</style>