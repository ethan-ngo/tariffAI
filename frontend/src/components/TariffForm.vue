<template>
  <div class="tariff-form-container">
    <h1>{{ msg }}</h1>

    <form class="tariff-form">
      <h2>Product Classification & Landing Cost</h2>
      <p class="description-text">
        To get the estimated landing cost of a product (including duties, tariffs, 
        and VAT), please fill in all required fields and click "Submit Calculation."
 
        If the HTSUS code is unknown, you may instead provide the Product Description, 
        Origin Country, Weight, and Quantity, and click "Submit Classification" 
        to let the system determine the appropriate HTSUS code.

        All results will be displayed in the chatbot, where you can also ask 
        follow-up questions.
      </p>

      <div class="form-grid">
        <!-- HTSUS Code -->
        <div class="form-row">
          <label for="code">HTSUS Code (for calculation):</label>
          <input type="text" id="code" v-model="code">
          <p v-if="errors.code" class="error-message">{{ errors.code }}</p>
        </div>

        <!-- Product Description -->
        <div class="form-row form-row-wide">
          <label for="productDesc">Product Description:</label>
          <textarea id="productDesc" v-model="productDesc" rows="2" placeholder="Enter product description..."></textarea>
          <p v-if="errors.productDesc" class="error-message">{{ errors.productDesc }}</p>
        </div>

        <!-- Origin Country -->
        <div class="form-row">
          <label for="country">Origin Country:</label>
          <input type="text" id="country" v-model="country" required>
          <p v-if="errors.country" class="error-message">{{ errors.country }}</p>
        </div>

        <!-- Weight -->
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
          <p v-if="errors.weight" class="error-message">{{ errors.weight }}</p>
        </div>

        <!-- Quantity -->
        <div class="form-row">
          <label for="quantity">Quantity:</label>
          <input type="number" id="quantity" v-model="quantity" min="1" required>
          <p v-if="errors.quantity" class="error-message">{{ errors.quantity }}</p>
        </div>

        <!-- Product Value -->
        <div class="form-row">
          <label for="productValue">Product Value:</label>
          <input type="number" id="productValue" v-model="productValue" min="0" step="0.01" placeholder="Enter product value">
          <p v-if="errors.productValue" class="error-message">{{ errors.productValue }}</p>
        </div>

        <!-- Shipping Cost -->
        <div class="form-row">
          <label for="shippingCost">Shipping Cost:</label>
          <input type="number" id="shippingCost" v-model="shippingCost" min="0" step="0.01" placeholder="Enter shipping cost">
          <p v-if="errors.shippingCost" class="error-message">{{ errors.shippingCost }}</p>
        </div>

        <!-- Insurance Cost -->
        <div class="form-row">
          <label for="insuranceCost">Insurance Cost:</label>
          <input type="number" id="insuranceCost" v-model="insuranceCost" min="0" step="0.01" placeholder="Enter insurance cost">
          <p v-if="errors.insuranceCost" class="error-message">{{ errors.insuranceCost }}</p>
        </div>
      </div>

      <!-- Buttons aligned side by side -->
      <div class="form-actions">
        <button type="button" @click="submitClassification">Submit Classification</button>
        <button type="button" @click="submitCalculation">Submit Calculation</button>
      </div>
    </form>

    <div v-if="result" class="result">
      <h3>Result:</h3>
      <pre>{{ formattedResult }}</pre>
    </div>
  </div>
</template>

<script>
import emitter from '../eventBus'

export default {
  name: 'TariffForm',
  props: {
    msg: String
  },
  data() {
    return {
      country: '',
      productDesc: '',
      quantity: 1,
      weight: 0,
      weightUnit: 'kg',
      result: null,
      errors: {
        code: '',
        productDesc: '',
        country: '',
        quantity: '',
        weight: '',
        productValue: '',
        shippingCost: '',
        insuranceCost: '',
      }
    }
  },
  computed: {
    formattedResult() {
      return this.result ? JSON.stringify(this.result, null, 2) : '';
    }
  },
  methods: {
    async submitClassification() {
      // Clear previous errors
      this.errors.productDesc = '';
      this.errors.country = '';
      this.errors.quantity = '';
      this.errors.weight = '';
      this.result = null;

      let hasError = false;

      if (!this.productDesc || this.productDesc.trim() === '') {
        this.errors.productDesc = "Please enter a product description.";
        hasError = true;
      }

      if (!this.country || this.country.trim() === '') {
        this.errors.country = "Please select a country.";
        hasError = true;
      }

      if (!this.quantity || this.quantity < 1) {
        this.errors.quantity = "Please enter a valid quantity.";
        hasError = true;
      }

      if (!this.weight || this.weight <= 0) {
        this.errors.weight = "Please enter a valid weight.";
        hasError = true;
      }

      if (hasError) {
        // Prevent submission if errors
        return;
      }
    
      // gets the top htsus codes and outputs it in the chatbot
      try {
        // Emit progress to chatbot
        const progress = `Please wait a  moment, classifying "${this.productDesc}"...`
        emitter.emit('sentPostRequest', progress); // Send data to chatbot

        const response = await fetch('http://127.0.0.1:5000/classifier/htsus', {
              method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_description: this.productDesc,
            origin_country: this.country,
            weight: this.weight,
            weight_unit: this.weightUnit,
            quantity: this.quantity
          })
        });
        const data = await response.json();
        console.log('HTSUS Classification result:', data); // <-- Console log the result

        // Emit htsus result to chatbot
        emitter.emit('htsusResult', data); // Send data to chatbot
      } catch (error) {
        this.result = { error: error.message };
        console.log('HTSUS Classification error:', error);
      }
    },

    async submitCalculation() {
      // Clear previous errors
      this.errors = {
        code: '',
        productDesc: '',
        country: '',
        quantity: '',
        weight: '',
        productValue: '',
        shippingCost: '',
        insuranceCost: ''
      };
      this.result = null;

      let hasError = false;

      if (!this.code || this.code.trim() === '') {
        this.errors.code = "Please enter an HTSUS code.";
        hasError = true;
      }

      if (!this.productDesc || this.productDesc.trim() === '') {
        this.errors.productDesc = "Please enter a product description.";
        hasError = true;
      }

      if (!this.country || this.country.trim() === '') {
        this.errors.country = "Please select a country.";
        hasError = true;
      }

      if (!this.quantity || this.quantity < 1) {
        this.errors.quantity = "Please enter a valid quantity.";
        hasError = true;
      }

      if (!this.weight || this.weight <= 0) {
        this.errors.weight = "Please enter a valid weight.";
        hasError = true;
      }

      if (!this.productValue || this.productValue < 0) {
        this.errors.productValue = "Please enter a valid product value.";
        hasError = true;
      }

      if (hasError) {
        return;
      }

      try {
        // Call /landing API
         // Emit progress to chatbot
        const progress = `Please wait a  moment, calculating the total landing cost for "${this.code}"...`
        emitter.emit('sentCalculationRequest', progress); // Send data to chatbot

        const response = await fetch('http://127.0.0.1:5000/landing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            hts_code: this.code,
            prod_desc: this.productDesc,
            country: this.country,
            prod_value: this.productValue,
            quantity: this.quantity,
            shipping: this.shippingCost,
            insurance: this.insuranceCost,
          })
        });
        const data = await response.json();
        this.result = data.landing_cost;
        console.log('Landing API result:', data); // <-- Console log the result

        // Emit htsus result to chatbot
        emitter.emit('landedCostResult', data.landing_cost); // Send data to chatbot
      } catch (error) {
        this.result = { error: error.message };
        console.log('Landing API error:', error);
      }
    }
  }
}
</script>

<style scoped>
.tariff-form-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
h1 {
  font-size: 2.5rem;
  margin-bottom: 18px;
}
.tariff-form {
  width: 100%;
  max-width: 600px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.5);
  padding: 24px 24px 16px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-row-wide {
  grid-column: 1 / 3;
}
.form-row label {
  font-weight: bold;
  text-align: left;
  font-size: 1rem;
}
.form-row input,
.form-row select,
.form-row textarea {
  padding: 7px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 15px;
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
  margin-top: 18px;
  padding: 10px 20px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  align-self: flex-end;
}
button:hover {
  background-color: #6366f1;
}
.result {
  margin: 20px auto 0 auto;
  text-align: left;
  max-width: 500px;
  background: #f6f8fa;
  border: 1px solid #e1e1e1;
  padding: 15px;
  border-radius: 5px;
}
.form-section {
  margin-bottom: 28px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ddd;
}

.form-section h2 {
  font-size: 1.4rem;
  margin-bottom: 12px;
  color: #333;
}

.description-text {
  text-align: left;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 5%; /* ✅ this creates spacing between the buttons */
  margin-top: 20px;
}

.error-message {
  color: red;
  font-size: 0.9rem;
  margin-top: 4px;
  font-style: italic;
}

@media (max-width: 900px) {
  .tariff-form {
    max-width: 98vw;
    padding: 16px 4vw;
  }
  .form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .form-row-wide {
    grid-column: 1 / 2;
  }
}
@media (max-width: 600px) {
  h1 {
    font-size: 1.5rem;
  }
  .tariff-form {
    padding: 10px 2vw;
  }
  .result {
    padding: 8px;
    font-size: 13px;
  }
}
</style>