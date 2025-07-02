<template>
  <div id="app">
    <ItemCart />
    <div class="main-content">
      <div class="top-half">
        <TariffForm msg="Tariff Calculator"/>
      </div>
      <div class="bottom-half">
        <ChatBot />
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
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  display: flex;
  height: 100vh;
  margin: 0;
  text-align: center;
}

.main-content {
  margin-left: 320px;
  width: calc(100vw - 320px);
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-half, .bottom-half {
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.top-half {
  border-bottom: 1px solid #eee;
  background: #fafbfc;
  height: 50%;
}

.bottom-half {
  background: #f5f6fa;
  height: 50%;
}
</style>
