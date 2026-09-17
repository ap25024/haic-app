   
## Automated Business Insight Generation Using Large Language Models with User-in-the-Loop Evaluation 
## Project purpose
The project explores how large language models can support the interpretation of business data within a workflow that includes human evaluation.
The application performs predefined calculations and provides their results to the model alongside the user's business context. Users then decide which insights to accept, edit or reject before viewing a final Reviewed Insight Summary. Their decisions determine the content retained in the final summary.
   
## Main features
   
- CSV upload and validation.  
- Business context collection, including domain, target audience and analysis goal.  
- Automated exploratory data analysis using pandas.  
- Generation of three insights connected to numerical evidence.  
- Sequential review through Accept, Edit and Reject actions.  
- Recording of review decisions, edited text and decision times.  
- SQLite storage of session information, analysis outputs, insights and evaluations.  
- An on-screen Reviewed Insight Summary containing accepted and edited insights.  
   
## Application workflow  
   
1. **Upload a dataset:** Select a CSV file for analysis.  
2. **Provide context:** Specify the business domain, intended audience and analysis goal.*  
3. **Generate insights:** The application calculates an EDA package and combines it with the supplied context in a structured prompt.*  
4. **Review each insight:** Examine the generated content and its supporting evidence, then accept, edit or reject it.*  
5. **View the reviewed summary:** Read the retained insights after completing all three reviews.*  
   
### Exploratory data analysis  
   
*The predefined EDA package covers:*  
   
| Analysis | Purpose |  
| --- | --- |  
| Dataset overview | Summarise the dataset's structure and dimensions. |  
| Column classification | Identify column types for subsequent analysis. |  
| Missing data | Identify incomplete fields and missing-value patterns. |  
| Descriptive statistics | Summarise numerical variables. |  
| Categorical analysis | Examine category frequencies and distributions. |  
| Correlations | Identify associations between numerical variables. |  
| Outliers | Flag potentially unusual numerical values. |
   
### Generated insights  
   
Each analysis produces three insight types:  
   
| Insight type | Focus |  
| --- | --- |  
| KPI Performance | Findings related to business performance within the available evidence. |  
| Anomaly / Risk | Unusual values or patterns that may warrant investigation. |  
| Data Quality / Limitation | Data issues or analytical constraints that affect interpretation. |  
   
### User review  
   
- **Accept:** Retain the insight as presented.  
- **Edit:** Revise the insight before retaining it. 
- **Reject:** Exclude the insight from the final summary.
   
Insights are reviewed one at a time. Review decisions are stored separately from the original generated content, allowing the original output and subsequent user changes to be examined.  
   
## Technology stack 
   
| Component | Technology |  
| --- | --- |  
| Programming language | Python |  
| Web interface | Streamlit |  
| Data analysis | pandas |  
| Persistent storage | SQLite |  
| LLM provider | Groq API |  
| Model used in the evaluated implementation | `openai/gpt-oss-120b` |


The application was developed using Python 3.12.     
--------------------------
## Main Streamlit application --> app.py  
   
Responsible for:  
   
- CSV upload  
- context collection  
- application state  
- execution of the analysis pipeline  
- presentation of generated insights  
- user evaluation  
- modules/eda_engine.py  
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
*1. Clone the repository*  
*```*  
*git clone <repository-url>*  
*cd <repository-folder>*  
*```*  
## Running locally  
### 1. Prepare the environment  From the repository's root directory, create and activate a virtual environment.  
**Linux / macOS**  
```bash python3 -m venv .venv source .venv/bin/activate```

**Windows PowerShell**  
```powershell python -m venv .venv .\.venv\Scripts\Activate.ps1```

### 2. Install dependencies  
If the repository includes `requirements.txt`, install its dependencies\  
```bash python -m pip install -r requirements.txt```

### 3. Configure the API key  
Configure your Groq API key using the environment-variable name expected by the LLM service module. For an implementation using `GROQ_API_KEY` and loading a local `.env` file:  
```dotenv GROQ_API_KEY=your_groq_api_key```

### 4. Start the application  
```
bash python -m streamlit run app.py
```

Open the local address displayed in the terminal. Insight generation requires an internet connection and a valid Groq API key.  
## Data storage 
The application uses `haic_app.db` to store session information, the EDA package, generated insights and user evaluations.  The database supports analysis of review behaviour, including acceptance, editing, rejection and decision times. The Reviewed Insight Summary is displayed after the review process is completed.  API keys, local environment files and the participant evaluation database should be excluded from the public repository.  

## Evaluation status  
*Create a .env file in the root directory:*  
   
```  
   
DISS/  
├── .env  
├── app.py  
└── ...   
```  
### User Steps to Follow  
   
*1. Start the Streamlit application.*  
*2. Upload a CSV dataset.*  
*3. Enter the assigned Participant ID.*  
*4. Select the appropriate business domain.*  
*5. Specify the target audience.*  
*6. Describe what you are looking for in the dataset.*  
*7. Select Generate Insights.*  
*8. The application performs the EDA.*  
*9. The structured EDA results are sent to the LLM.*  
*10. Three generated insights are displayed.*  
*11. Evaluate each insight using Accept, Reject, or Edit.*  
*12. Review Insights Summary is returned, option to copy the text*    
   
API availability, model availability and usage limits can affect insight generation. 

_The application is designed as a research prototype rather than a production Business Intelligence platform._ 
