# 🧠📊 Tariff AI

---

## 🗂️ Overview

**Landifly** is a tool for helping international sellers using SellingPilot better understand their total import costs to the United States by:

- Classifying products into the correct HTS/HS codes from text or image input.
- Determining applicable base duty rates and additional tariffs (e.g., Section 301).
- Automatically calculating total duties based on declared value.
- Presenting results clearly, with policy references and cost breakdown.
---

## 🖥️ Technology Stack
<div align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" height="40" alt="javascript logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg" height="40" alt="nodejs logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg" height="40" alt="vuejs logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" height="40" alt="flask logo"  />
</div>

---

## 🛠️ Setup

### 1. Clone the Repository

```
git clone https://github.com/ethan-ngo/tariffAI.git
```
### 2. Install Dependencies

#### Front-End:
```
cd frontend
npm install
```

#### Back-End:
```
cd backend
pip install -r requirements.txt
```

### 3. Create the local database.
1. Go to https://www.usitc.gov/harmonized_tariff_information/hts/archive/list and download the most recent CSV file.
2. Rename the CSV file to "htsus.csv"
3. Upload "htsus.csv" to the backend/htsus_classification/python_process_db directory
4. Run flatten_htsus.py
5. Run add_hts_chapter.py
6. Run fill_db.py (note that this step may take a while due to the large CSV file)
7. At the end, there should be a new directory called crhoma_db under the htsus_classification directory

### 4. Start the Application

Open two separate terminal windows:

**Terminal 1 (Back-end):**
Navigate to the back-end directory and run:
```
flask --app app run
```

**Terminal 2 (Front-end):**

Navigate to the front-end directory and run the following command:
```bash
npm run serve
```

### 5. Access the Application

Visit [http://localhost:8080](http://localhost:8080) in your browser.
---
