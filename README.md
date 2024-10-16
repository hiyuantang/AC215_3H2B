#### Project Milestone 2 Organization

```
├── Readme.md
├── data
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   └── Statement of Work_Sample.pdf
└── src
    ├── data-versioning
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    ├── dataset-creator
    │   ├── data
    │   │   ├── *.dvc
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    ├── gemini-finetuner
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    ├── rag
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    ├── docker-compose.yml

```

# AC215 - Milestone2 - LLM-powered Trip Planner App

**Team Members**

Yuan Tang

**Group Name**

3H2B

**Project**

In this project, we’re developing an LLM-powered travel planner application. The app will take user inputs, such as their travel destination (city), duration, dates or months, and type of trip. The LLM will then generate a carefully tailored and considerate travel itinerary based on these inputs. Additionally, a Google map will display the locations and routes for each day of the trip, providing users with visual reference. We’ll be using techniques like fine-tuning, RAG, and chain of thoughts to enhance the quality and consistency of the output. 

### Milestone2 ###

In this milestone, we have the components for data versioning, data creation, LLM fine-tuning, and RAG. 

**Strict Format Dataset**

We generated a dataset of 500 pairs of question and answer pairs for fine-tuning the Gemini 1.5 flash model to behave in a way that facilitates us extracting days, themes, and location information. Specifically, the days and location information will go through a native route optimization to reduce the total distance for each day of the trip. With that in mind, the question and answer pair is formated in a way that the question will ask for a concise thematic travel itinerary and the answer will provide the itinerary in a strict format. For example:

- **Pair 1:**
	- Question: My family and I are going to Rome for 5 days in April, eager to immerse ourselves in ancient history and iconic landmarks. Can you create a concise itinerary with only days and locations, focusing on the historical significance of this city?
	- Answer: 5-Day Family Rome Itinerary for April\nDay 1: Ancient Wonders & Colosseum Majesty\n- Roman Forum\n- Colosseum\n- Palatine Hill\nDay 2: Vatican City & Artistic Treasures\n- Vatican Museums\n- Sistine Chapel\n- St. Peter's Basilica\nDay 3: Trastevere Charm & Local Flavors\n- Trastevere Neighborhood\n- Campo de' Fiori\n- Pantheon\nDay 4: Ancient Baths & Secret Gardens\n- Baths of Caracalla\n- Borghese Gallery & Gardens\n- Trevi Fountain\nDay 5: Historical Delights & Roman Views\n- Spanish Steps\n- Piazza Navona\n- Castel Sant'Angelo

- **Pair 2:** 
	- Question: Location: Bangkok, Days: 4, month: January, type: Culinary. What is a concise itinerary for my trip?
	- Answer: 5-Day Culinary Itinerary in Bangkok for January\nDay 1: Street Food Delights and Market Explorations\n- Chatuchak Weekend Market\n- Yaowarat (Chinatown)\n- Sukhumvit Street Food\nDay 2: Authentic Thai Cuisine and Fine Dining\n- Nahm\n- Bo.lan\n- Gaggan Anand\nDay 3: Riverfront Dining and Night Market Delights\n- Asiatique The Riverfront\n- Ratchada Night Market\n- Khao San Road\nDay 4: Traditional Thai Dishes and Culinary Workshops\n- Thipsamai Pad Thai\n- Somboon Seafood\n- Blue Elephant Cooking School

The dataset, approximately 400KB in size, is generated by Gemini 1.5 flash model. We have stored it in a private Google Cloud Bucket, and we applied data version control over the dataset. 

**City Dataset**

xxxxxxxxxxxx

**Data Versioning Container**
The container is responsible for versioning both the Strict Format Dataset and the City Dataset. It will containerize and bind mount the entire Git repository. This approach is chosen because DVC (Data Version Control) works best with Git, which typically requires the inclusion of the `.git` directory in the container or bind-mounted for DVC to function properly. We set up two remotes for DVC, each responsible for tracking one of the datasets mentioned above.

- To initialize DVC, we use the command:
`dvc init`
- To add remotes, we use the following commands:
`dvc remote add llm_strict_format_dataset gs://llm-strict-format-dataset/dvc_store` for Strict Format Dataset
- To version the datasets, we follow these steps:
`dvc add src/dataset-creator/data/*.jsonl`
`dvc add src/dataset-creator/data/*.csv`
`git add .`
`git commit -m [message]`
`dvc push -r strict_format_dataset`

**Data Creator Container**
The container generates the 500 question & answer pairs dataset by providing sufficient and appropriate instruction to prompt Gemini 1.5 flash model to produce pairs in json format. Then, these json format *.txt files will be converted to *.csv and jsonl file and split into train and test sets for finetuning training and validation purpose. Both *.csv and *.jsonl files will be uploaded to GCS bucket. 

   

## Data Pipeline Overview

1. **`src/datapipeline/preprocess_cv.py`**
   This script handles preprocessing on our 100GB dataset. It reduces the image sizes to 128x128 (a parameter that can be changed later) to enable faster iteration during processing. The preprocessed dataset is now reduced to 10GB and stored on GCS.

2. **`src/datapipeline/preprocess_rag.py`**
   This script prepares the necessary data for setting up our vector database. It performs chunking, embedding, and loads the data into a vector database (ChromaDB).

3. **`src/datapipeline/Pipfile`**
   We used the following packages to help with preprocessing:
   - `special cheese package`

4. **`src/preprocessing/Dockerfile(s)`**
   Our Dockerfiles follow standard conventions, with the exception of some specific modifications described in the Dockerfile/described below.


## Running Dockerfile
Instructions for running the Dockerfile can be added here.
To run Dockerfile - `Instructions here`

**Models container**
- This container has scripts for model training, rag pipeline and inference
- Instructions for running the model container - `Instructions here`

**Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations.

----
You may adjust this template as appropriate for your project.

**Application Mockup Design**
