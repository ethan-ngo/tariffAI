<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <form @submit.prevent="submitForm" class="tariff-form">
      <div class="form-row">
        <label for="code">HTSUS Code (optional):</label>
        <input type="text" id="code" v-model="code">
      </div>
      
      <div class="form-row">
        <label for="country">Importing Country:</label>
        <input type="text" id="country" v-model="country" required>
      </div>
      
      <div class="form-row">
        <label for="productDesc">Product Description:</label>
        <textarea id="productDesc" v-model="productDesc" rows="3" placeholder="Enter product description..."></textarea>
      </div>
      
      <div class="form-row">
        <label for="productValue">Product Value:</label>
        <input type="number" id="productValue" v-model="productValue" min="0" step="0.01" placeholder="Enter product value">
      </div>

      <div class="form-row">
        <label for="quantity">Quantity:</label>
        <input type="number" id="quantity" v-model="quantity" min="1" required>
      </div>

      <div class="form-row">
        <label for="shippingCost">Shipping Cost:</label>
        <input type="number" id="shippingCost" v-model="shippingCost" min="0" step="0.01" placeholder="Enter shipping cost">
      </div>

      <div class="form-row">
        <label for="insuranceCost">Insurance Cost:</label>
        <input type="number" id="insuranceCost" v-model="insuranceCost" min="0" step="0.01" placeholder="Enter insurance cost">
      </div>
      
      <div class="form-row">
        <label for="weight">Weight:</label>
        <div class="weight-input">
          <input type="number" id="weight" v-model="weight" step="0.01" min="0" required>
          <select id="weightUnit" v-model="weightUnit" required>
            <option value="kg">kg</option>
            <option value="lb">lb</option>
            <option value="g">g</option>
            <option value="oz">oz</option>
            <option value="ton">ton</option>
          </select>
        </div>
      </div>
      
      <button type="submit">Submit</button>
    </form>
    <div v-if="result" class="result">
      <h3>Result:</h3>
      <pre>{{ formattedResult }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TariffForm',
  props: {
    msg: String
  },
  data() {
    return {
      code: '',
      country: '',
      productDesc: '',
      quantity: 1,
      weight: 0,
      weightUnit: 'kg',
      productValue: '',
      shippingCost: '',
      insuranceCost: '',
      result: null
    }
  },
  computed: {
    formattedResult() {
      return this.result ? JSON.stringify(this.result, null, 2) : '';
    }
  },
  methods: {
    async submitForm() {
      // Remove code required validation, keep others as needed
      if (!this.country) {
        this.result = { error: "Please select a country." };
        return;
      }
      if (!this.quantity || this.quantity < 1) {
        this.result = { error: "Please enter a valid quantity." };
        return;
      }
      if (!this.weight || this.weight < 0) {
        this.result = { error: "Please enter a valid weight." };
        return;
      }
      
      try {
        // Include the new form data in the request
        
        const response = await fetch(`http://127.0.0.1:5000/scraper/301/${this.code}`);
        const data = await response.json();
        this.result = data;
      } catch (error) {
        this.result = { error: error.message };
      }
    }
  }
}
</script>

<style scoped>
h1 {
  font-size: 50px;
}
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.tariff-form {
  margin: 20px auto;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-row label {
  font-weight: bold;
  text-align: left;
}
.form-row input,
.form-row select,
.form-row textarea {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}
.form-row textarea {
  resize: none;
}
.weight-input {
  display: flex;
  gap: 10px;
}
.weight-input input {
  flex: 2;
}
.weight-input select {
  flex: 1;
}
button {
  padding: 10px 20px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
button:hover {
  background-color: #6366f1;
}
.result {
  margin: 20px auto;
  text-align: left;
  max-width: 500px;
  background: #f6f8fa;
  border: 1px solid #e1e1e1;
  padding: 15px;
  border-radius: 5px;
}
</style>