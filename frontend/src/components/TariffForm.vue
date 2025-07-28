<template>
  <div class="tariff-form-container">

    <form class="tariff-form">
      <p class="description-text">
        Enter all details and click Submit Calculation to estimate landed 
        cost. If you don’t know the HTSUS code, use Submit Classification.
        Use Compare Countries to get the estimated duties for multiple countries.
      </p>

      <div class="form-grid">
        <!-- HTSUS Code -->
        <div class="form-row form-row">
          <label for="code">HTSUS Code (for calculation):</label>
          <input type="text" id="code" v-model="code" placeholder="ex) 0000.00.0000">
          <p v-if="errors.code" class="error-message">{{ errors.code }}</p>
        </div>

        <!-- HTSUS Code -->
        <div class="form-row form-row">
          <label for="code">HTSUS Chapter (optional but improves classification):</label>
          <input type="text" id="code" v-model="code" placeholder="ex) 05">
          <p v-if="errors.code" class="error-message">{{ errors.code }}</p>
        </div>

        <!-- Product Description -->
        <div class="form-row form-row-wide">
          <label for="productDesc">Product Description:</label>
          <div class="desc-with-upload">
            <textarea
              id="productDesc"
              v-model="productDesc"
              rows="2"
              placeholder="Enter product description or upload image..."
            ></textarea>
            <label class="upload-icon-btn">
              <input type="file" accept="image/*" @change="handleImageUpload" hidden />
              <img
                src="@/assets/image_upload.png"
                alt="Upload"
                class="upload-icon-img"
              />
            </label>
          </div>
          <p v-if="errors.productDesc" class="error-message">{{ errors.productDesc }}</p>
        </div>

        <!-- Origin Country -->
        <div class="form-row">
          <label for="countries">Origin Country (at least 1):</label>
            <input
              type="text"
              id="countries"
              v-model="countryInput"
              placeholder="Type and press enter to add"
              @keyup.enter.prevent="addCountry"
            />
            <div class="country-tags">
              <span v-for="(c, index) in countries" :key="index" class="tag">
                {{ c }}
                <button type="button" class="remove-btn" @click="removeCountry(index)">×</button>
              </span>
            </div>
            <p v-if="errors.countries" class="error-message">{{ errors.countries }}</p>
        </div>

        <!-- Weight -->
        <div class="form-row">
          <label for="weight">Weight (per unit):</label>
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
          <label for="quantity">Quantity (number of units):</label>
          <input type="number" id="quantity" v-model="quantity" min="0" required>
          <p v-if="errors.quantity" class="error-message">{{ errors.quantity }}</p>
        </div>

        <!-- Product Value -->
        <div class="form-row">
          <label for="productValue">Product Value (per unit):</label>
          <input type="number" id="productValue" v-model="productValue" min="0" step="0.01">
          <p v-if="errors.productValue" class="error-message">{{ errors.productValue }}</p>
        </div>

        <!-- Shipping Cost -->
        <div class="form-row">
          <label for="shippingCost">Shipping Cost (total cost):</label>
          <input type="number" id="shippingCost" v-model="shippingCost" min="0" step="0.01">
          <p v-if="errors.shippingCost" class="error-message">{{ errors.shippingCost }}</p>
        </div>

        <!-- Insurance Cost -->
        <div class="form-row">
          <label for="insuranceCost">Insurance Cost (total cost):</label>
          <input type="number" id="insuranceCost" v-model="insuranceCost" min="0" step="0.01">
          <p v-if="errors.insuranceCost" class="error-message">{{ errors.insuranceCost }}</p>
        </div>
      </div>

      <!-- Buttons for processing -->
      <div class="form-actions">
        <button type="button" @click="submitClassification">Submit Classification</button>
        <button type="button" @click="submitCalculation">Submit Calculation</button>
        <button type="button" @click="compareCountries">Compare Countries</button>
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

// get links to the official HTSUS website using the HTSUS codes
function buildHTSUSLinksFromDutyRates(dutyRates) {
  return dutyRates
    .map(([code, ]) => {
      return `"https://hts.usitc.gov/search?query=${encodeURIComponent(code)}"`;
    });
}

export default {
  name: 'TariffForm',
  props: {
    msg: String
  },
  data() {
    return {
      countryInput: '',
      countries: [], // store multiple countries
      chapter: '',
      productDesc: '',
      image: null,
      imagePreviewUrl: '',
      isProcessingImage: false,
      quantity: 0,
      weight: 0,
      productValue: 0,
      shippingCost: 0,
      insuranceCost: 0,
      weightUnit: 'kg',
      result: null,
      errors: {
        code: '',
        productDesc: '',
        countries: '',
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
    async handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      this.isProcessingImage = true;
      
      const reader = new FileReader()
      reader.onload = async () => {
        this.image = reader.result
        
        try {
          // Call your image-to-text API
          const response = await fetch('http://127.0.0.1:5000/image-to-description', {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              image: reader.result
            })
          });

          if (!response.ok) {
            throw new Error('Failed to process image');
          }

          const data = await response.json();
          this.productDesc = data.description; // Adjust based on your API response structure
          emitter.emit("image_upload", `<i>🖼️ Image upload proccessed!</i><br><img src="${reader.result}" style="max-width: 200px; height: auto; border-radius: 4px;">`);

        } catch (error) {
          console.error('Image processing error:', error);
          
          // Set error message
          this.errors.productDesc = 'Failed to process image. Please enter description manually.';
          
        } finally {
          this.isProcessingImage = false;
        }
      }
      reader.readAsDataURL(file)
    },

    // from the tariff form country input, add the country to the countries list to be used later
    addCountry() {
      const trimmed = this.countryInput.trim();
      const formatted = trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
      if (formatted && !this.countries.includes(formatted)) {
        this.countries.push(formatted);
      }
      this.countryInput = '';
    }, // remove country from countries list
    removeCountry(index) {
      this.countries.splice(index, 1);
    },
    
    // classifies by htsus code by using the product description, origin country, weight
    async submitClassification() {
      // Clear previous errors
      this.errors.productDesc = '';
      this.errors.countries = '';
      this.errors.quantity = '';
      this.errors.weight = '';
      this.result = null;

      let hasError = false;

      if (!this.productDesc || this.productDesc.trim() === '') {
        this.errors.productDesc = "Please enter a product description.";
        hasError = true;
      }

      if (this.countries.length === 0) {
        this.errors.countries = "Please enter at least one country.";
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

      const userMsg = `I want to classify "${this.productDesc}," from "${this.countries[0]}" with quantity: ${this.quantity} and weight: ${this.weight} ${this.weightUnit}`;
      emitter.emit('sentUserPostRequest', userMsg);
  
      // gets the top htsus codes and outputs it in the chatbot
      try {
        // Emit progress to chatbot
        const progress = `Please wait a  moment, classifying "${this.productDesc}"...`
        emitter.emit('sentPostRequest', progress); // Send data to chatbot

        const country = this.countries[0]
        const formatted_country = country.charAt(0).toUpperCase() + country.slice(1).toLowerCase();

        const response = await fetch('http://127.0.0.1:5000/classifier/htsus', {
              method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_description: this.productDesc,
            origin_country: formatted_country,
            weight: this.weight,
            weight_unit: this.weightUnit,
            quantity: this.quantity,
            chapter: this.chapter || null
          })
        });
        const data = await response.json();

        const linksHtml = buildHTSUSLinksFromDutyRates(data.duty_rates);

        // Emit htsus result to chatbot
        emitter.emit('htsusResult', { data, linksHtml }); // Send data to chatbot
      } catch (error) {
        this.result = { error: error.message };
        console.log('HTSUS Classification error:', error);
      }
    },
    
    // calculate the landing cost for one country 
    async submitCalculation() {
      // Clear previous errors
      this.errors = {
        code: '',
        productDesc: '',
        countries: '',
        quantity: '',
        weight: '',
        weight_unit: '',
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

      if (this.countries.length === 0) {
        this.errors.countries = "Please enter at least one country.";
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

      const userMsg = `I want the final landing cost for HTSUS code "${this.code}," product "${this.productDesc}, " country "${this.country}," quantity ${this.quantity}, weight ${this.weight} ${this.weightUnit}, product value $${this.productValue}, shipping $${this.shippingCost}, insurance $${this.insuranceCost}`;
      emitter.emit('sentUserCalculationRequest', userMsg);

      try {
        // Emit progress to chatbot
        const progress = `Please wait a  moment, calculating the total landed cost for "${this.code}"...`
        emitter.emit('sentCalculationRequest', progress); // Send data to chatbot

        const country = this.countries[0]
        const formatted_country = country.charAt(0).toUpperCase() + country.slice(1).toLowerCase();

        const response = await fetch('http://127.0.0.1:5000/landing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            hts_code: this.code,
            prod_desc: this.productDesc,
            country: formatted_country,
            prod_value: this.productValue,
            weight: this.weight,
            weight_unit: this.weightUnit,
            quantity: this.quantity,
            shipping: this.shippingCost,
            insurance: this.insuranceCost,
          })
        });

        if (!response.ok) {
          emitter.emit('botError', "An error has occured, please try again");
          return;
        }

        const data = await response.json();
        data.htsus_code = this.code

        const data2 = {
          ...data, 
          origin_country: formatted_country
        }

        // Emit htsus result to chatbot
        emitter.emit('landedCostResult', data2); // Send data to chatbot

        const combinedData = {
          ...data2,       
          prod_desc: this.productDesc,
          quantity: this.quantity,
          productValue: this.productValue,
          weight: this.weight,
          shipping: this.shippingCost,
          insurance: this.insuranceCost,
          weightUnit: this.weightUnit,
          htsus_code: this.code,
        };

        emitter.emit('landedCostResult2', combinedData);

      } catch (error) {
        this.result = { error: error.message };
        console.log('Landing API error:', error);
      }
    },

    // get a pdf comparing the duty rates for multiple countries
    async compareCountries() {
      // Clear previous errors
      this.errors = {
        code: '',
        productDesc: '',
        countries: '',
        quantity: '',
        weight: '',
        weight_unit: '',
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

      if (this.countries.length === 0) {
        this.errors.countries = "Please enter at least one country.";
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

      const countryList = this.countries.join(', ');
      emitter.emit('wantCompareCountriesRequest', `I to compare tariff rates for HTSUS ${this.code} across: ${countryList}`);
      emitter.emit('sentCompareCountriesRequest', `Processing tariff rates for HTSUS ${this.code} across: ${countryList}, please wait...`);

      const compareResults = [];

      for (const country of this.countries) {
        try {
          const formatted_country = country.charAt(0).toUpperCase() + country.slice(1).toLowerCase();

          const response = await fetch('http://127.0.0.1:5000/landing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              hts_code: this.code,
              prod_desc: this.productDesc,
              country: formatted_country,
              prod_value: this.productValue,
              weight: this.weight,
              weight_unit: this.weightUnit,
              quantity: this.quantity,
              shipping: this.shippingCost,
              insurance: this.insuranceCost,
            })
          });

          
          const data = await response.json();
          data.htsus_code = this.code

          const combinedData = {
            ...data,     
            prod_desc: this.productDesc,
            quantity: this.quantity,
            productValue: this.productValue,
            weight: this.weight,
            shipping: this.shippingCost,
            insurance: this.insuranceCost,
            weightUnit: this.weightUnit,
            origin_country: formatted_country   
          };

          compareResults.push(combinedData);
          console.log("combinedData is ", combinedData);

        } catch (error) {
          this.result = { error: error.message };
          console.error(`Error for country ${country}:`, error);
        }
      }

      // emit final array of all results to generate and output the pdf
      console.log("compare results final is ", compareResults)
      emitter.emit('compareCountriesRes', compareResults);
    }
  }
}
</script>

<style scoped>
.desc-with-upload {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

.desc-with-upload textarea {
  flex: 1;
}

.upload-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e5e7eb;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 20px;
  width: 40px;
  min-width: 40px;
  transition: background-color 0.2s ease;
}

.upload-icon-img {
  display: block;
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.upload-icon-btn:hover {
  background-color: #d1d5db;
}
.tariff-form-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
h1 {
  font-size: 1.50rem;
  margin-bottom: 20px;
}
.tariff-form {
  width: 100%;
  max-width: 500px;
  background: #fff;
  border-radius: 3%;
  box-shadow: 0 2px 16px rgba(0,0,0,0.5);
  padding: 8px 24px 16px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.tariff-form h2 {
  margin-top: 1%;
  margin-bottom: 1%;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 1%;
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
  margin-top: 0%;
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
  padding: 0px;
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

.remove-btn {
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;       /* smaller font */
  line-height: 1;
  padding: 0 6px;        /* smaller horizontal padding */
  cursor: pointer;
  border-radius: 50%;
  width: 18px;           /* set fixed width and height */
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.remove-btn:hover {
  color: #f44336;        /* red on hover */
}

.country-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* Adds space between country tags */
  justify-content: center;
  margin-top: 6px;
}


@media (max-width: 900px) {
  .tariff-form {
    max-width: 98vw;
    padding: 2% 4vw;
  }
  .form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .form-row-wide {
    grid-column: 1 / 2;
  }
}
@media (max-width: 500px) {
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