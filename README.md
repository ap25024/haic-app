# MSc Thesis Project

## Automated Business Insight Generation Using Large Language Models with User-in-the-Loop Evaluation

The project investigates how Large Language Models can support the interpretation of structured business data by transforming statistical EDA outputs into readable analytical narratives.

The current prototype focuses on three main stages:

- Automated analysis of an uploaded CSV dataset
- LLM-based generation of Business Intelligence insights
- User evaluation of the generated insights

------------------------------

### Main Features and Steps that the app follows:

### 1. CSV Upload

Users can upload a structured CSV dataset directly through the Streamlit interface.

### 2. Analytical Context

Before generating insights, the user provides:

- Participant ID
- Business domain
- Target audience
- Primary analysis goal

This information is included in the LLM prompt so that the generated output is not based solely on statistical results.

### 3. Automated Exploratory Data Analysis

The EDA engine currently performs seven types of analysis.

- Dataset Overview (records basic information like number of rows, columns, possible duplicate entries)
- Column Classification (columns are classified as identifiers, numeric variables, categorical variables, datetime variables)
- Missing Data (system calculates numbers and percentage of missing observations)
- Descriptive Statistics (standard general descriptive statistics are calculated eg. count, mean, stdev, minumum etc)
- Categorical Analysis (summarized number of unique, most frequent values etc)
- Correlations (between numerical values)
- Detection of Outliers (treated as observations that may require further investigation)


### 4. LLM-Generated Insights

The EDA package is combined with the user's analytical context and sent to the configured Gemini model using the Google GenAI SDK.

The model is instructed to return exactly three insights:
1. KPI Performance
2. Anomaly / Risk
3. Data Quality/ Limitation

### 5. Human Evaluation

Generated insights are presented to the user for evaluation.

Each insight can currently receive one of three actions:

- Accept (The participant considers the insight sufficiently accurate, relevant, and clear)
- Reject (The participant rejects the generated insight)
- Edit (The participant can modify the generated narrative when the original insight is not fully satisfactory)


Evaluation results are stored in the local SQLite database and linked to the corresponding analytical session.

--------------------------

## Main Streamlit application --> app.py

Responsible for:

CSV upload
context collection
application state
execution of the analysis pipeline
presentation of generated insights
user evaluation
modules/eda_engine.py


-----------------------------

### Requirements

The project was developed and tested using:

- Python 3.12
- Streamlit
- pandas
- NumPy
- Google GenAI SDK
- python-dotenv
- SQLite

The complete Python dependency list is available in:

requirements.txt

------------------------------

### Installation
1. Clone the repository
```
git clone <repository-url>
cd <repository-folder>
```
2. Create a Python virtual environment

Linux/macOS:

```
python3 -m venv .venv
```
Activate it:

```
source .venv/bin/activate
```
Windows:

```
python -m venv .venv
```
Activate it:
```
.venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```

### API Configuration

The application requires access to the Google Gemini API.

Create a .env file in the root directory:

```

DISS/
├── .env
├── app.py
└── ...

```

### Running the Application

From the project directory, activate the virtual environment:

```
source .venv/bin/activate
```

Then start Streamlit:
```
streamlit run app.py
```
Alternatively:
```
python -m streamlit run app.py
```

Streamlit will normally make the application available locally 

### User Steps to Follow

1. Start the Streamlit application.
2. Upload a CSV dataset.
3. Enter the assigned Participant ID.
4. Select the appropriate business domain.
5. Specify the target audience.
6. Describe what you are looking for in the dataset.
7. Select Generate Insights.
8. The application performs the EDA.
9. The structured EDA results are sent to the LLM.
10. Three generated insights are displayed.
11. Evaluate each insight using Accept, Reject, or Edit.
12. Collection of data is completed!


_The application is designed as a research prototype rather than a production Business Intelligence platform._
