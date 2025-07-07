<template>
  <div id="app">
    <ItemCart />
    <div class="main-content">
      <div class="center-row">
        <div class="left-panel">
          <TariffForm msg="Tariff Calculator"/>
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
  }
}
</script>

<style>
html, body {
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  display: flex;
  height: 100vh;
  margin: 0;
  text-align: center;
  overflow: hidden;
}

.main-content {
  margin-left: 325px; /* match sidebar width */
  width: calc(100vw - 325px);
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.center-row {
  display: flex;
  gap: 64px;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.left-panel,
.right-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  overflow: hidden;
}

.left-panel {
  max-width: 420px;
  width: 100%;
  height: 100%;
}

.right-panel {
  max-width: 1000px;
  width: 100%;
  height: 100%;
}
</style>
