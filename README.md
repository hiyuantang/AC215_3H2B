#### Project Milestone 2 Organization

```
├── Readme.md
├── data
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   └── Statement of Work_Sample.pdf
├── secrets
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
    ├── frontend
    │   ├── src/app
    │   │   ├── *
    │   ├── .dockerignore
    │   ├── .eslintrc.json
    │   ├── .gitignore
    │   ├── Dockerfile
    │   ├── next.config.mjs
    │   ├── package-lock.json
    │   ├── pacakge.json
    │   ├── postcss.config.mjs
    │   ├── README.md
    │   ├── tailwind.config.ts
    │   ├── tsconfig.json
    ├── gemini-finetuner
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    ├── llm-rag
    │   ├── input-datasets
    │   │   ├── cities-wiki
    │   │   │   ├── *.txt
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── agent_tools.py
    │   ├── cli.py
    │   ├── docker-compose.yml
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── semantic_splitter.py
    ├── route-optimization
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── cli.py
    ├── .env
    ├── docker-compose.yml
    ├── docker-shell.sh
    ├── env.dev

```

### AC215 - Milestone2 - LLM-powered Trip Planner App ###

**Team Members**

Yuan Tang

**Group Name**

3H2B

**Project**

In this project, we’re developing an LLM-powered travel planner application. The app will take user inputs, such as their travel destination (city), duration, dates or months, and type of trip. The LLM will then generate a carefully tailored and considerate travel itinerary based on these inputs. Additionally, a Google map will display the locations and routes for each day of the trip, providing users with visual reference. We’ll be using techniques like fine-tuning, RAG, and chain of thoughts to enhance the quality and consistency of the output. 

### Milestone2 ###

In this milestone, we have the components for data versioning, data creation, LLM fine-tuning, and RAG. 

## Introduction to Datasets ##

**Strict Format Dataset**

We generated a dataset of 500 pairs of question and answer pairs for fine-tuning the Gemini 1.5 flash model to behave in a way that facilitates us extracting days, themes, and location information. Specifically, the days and location information will go through a native route optimization to reduce the total distance for each day of the trip. With that in mind, the question and answer pair is formated in a way that the question will ask for a concise thematic travel itinerary and the answer will provide the itinerary in a strict format. For example:

- **Example Pair 1:**
	- Question: My family and I are going to Rome for 5 days in April, eager to immerse ourselves in ancient history and iconic landmarks. Can you create a concise itinerary with only days and locations, focusing on the historical significance of this city?
	- Answer: 5-Day Family Rome Itinerary for April\nDay 1: Ancient Wonders & Colosseum Majesty\n- Roman Forum\n- Colosseum\n- Palatine Hill\nDay 2: Vatican City & Artistic Treasures\n- Vatican Museums\n- Sistine Chapel\n- St. Peter's Basilica\nDay 3: Trastevere Charm & Local Flavors\n- Trastevere Neighborhood\n- Campo de' Fiori\n- Pantheon\nDay 4: Ancient Baths & Secret Gardens\n- Baths of Caracalla\n- Borghese Gallery & Gardens\n- Trevi Fountain\nDay 5: Historical Delights & Roman Views\n- Spanish Steps\n- Piazza Navona\n- Castel Sant'Angelo

- **Example Pair 2:** 
	- Question: Location: Bangkok, Days: 4, month: January, type: Culinary. What is a concise itinerary for my trip?
	- Answer: 5-Day Culinary Itinerary in Bangkok for January\nDay 1: Street Food Delights and Market Explorations\n- Chatuchak Weekend Market\n- Yaowarat (Chinatown)\n- Sukhumvit Street Food\nDay 2: Authentic Thai Cuisine and Fine Dining\n- Nahm\n- Bo.lan\n- Gaggan Anand\nDay 3: Riverfront Dining and Night Market Delights\n- Asiatique The Riverfront\n- Ratchada Night Market\n- Khao San Road\nDay 4: Traditional Thai Dishes and Culinary Workshops\n- Thipsamai Pad Thai\n- Somboon Seafood\n- Blue Elephant Cooking School

The goal for fine-tuning the LLM on this dataset is to make the model respond by following a strict format of a travel itinerary. The format is as follows:

`A sentence summarizing the travel`<br />
`Day 1: Theme 1`<br />
`-Location 1.1`<br />
`-Location 1.2`<br />
`-Location 1.*`<br />
`Day 2: Theme 2`<br />
`-Location 2.1`<br />
`-Location 2.2`<br />
`-Location 2.*`<br />
`...`

The dataset, approximately 400KB in size, is generated by Gemini 1.5 flash 002 model. We have stored it in a private Google Cloud Bucket, and we applied data version control over the dataset. 

**City Dataset**

xxxxxxxxxxxx

## Containers ##

We offer two options for building and running containers for Milestone 2:
- Build and run all containers at once. (recommended)
- Build and run a single container or a set of containers that perform a single function.

To get started, you need to modify two files under the `./src` directory: `.env` and `env.dev`
- `.env` is responsible for providing environmental variables to `docker-compose.yml`
- `env.dev` will be read by `docker-shell.sh`
- Make sure you have updated items such as `GCP_PROJECT`, `GCS_BUCKET_NAME`, `GCP_SERVICE_ACCOUNT`, etc., according to your GCP setup.

Additionally, ensure you have your GCP key placed in the `./secrets` directory and rename it to `llm-service-account-key.json`.

## Option1:  Build & Run All Containers At Once ##

Steps are as follows:<br />
1. Navigate to the `./src` directory:<br />
`cd src<br />`<br />
2. Build all container images:<br />
`chmod +x ./*.sh`<br />
`./docker-shell.sh`<br />
3. Run all containers:<br />
`docker-compose up`<br />
4. View the running containers:<br />
`docker ps` or `docker ps --all`<br />
5. Open a new terminal. Now, you can attach to any container:<br />
`docker attach <container_name>`

Make sure to replace `<container_name>` with the actual name of the container you wish to attach to.

**Data Versioning Container**

The container is responsible for versioning both the Strict Format Dataset and the City Dataset. It will containerize and bind mount the entire Git repository. This approach is chosen because DVC (Data Version Control) works best with Git, which typically requires the inclusion of the `.git` directory in the container or bind-mounted for DVC to function properly. We set up two remotes for DVC, each responsible for tracking one of the datasets mentioned above.

- To initialize DVC, we use the command: `dvc init`. Since our repository already has DVC initialized and contains a `.dvc` directory at the root, we do not need to perform this step again
- To add remotes, we use the following commands: `dvc remote add llm_strict_format_dataset gs://llm-strict-format-dataset/dvc_store` for Strict Format Dataset
- To version the datasets, we follow these steps: `dvc add src/dataset-creator/data/*.jsonl` `dvc add src/dataset-creator/data/*.csv` `git add .` `git commit -m [message]` `dvc push -r llm_strict_format_dataset`

**Data Creator Container**

The container generates the 500 question & answer pairs dataset by providing appropriate instruction to prompt Gemini 1.5 flash 002 model to produce pairs in json format. Then, these json format *.txt files will be converted to *.csv and jsonl file and split into train and test sets for finetuning training and validation purpose. Both *.csv and *.jsonl files will be uploaded to GCS bucket. 

- To generate question & answer pairs - `python cli.py --generate`
- To split the dataset and convert it into *.csv and *.jsonl formats - `python cli.py --prepare`
- To upload the dataset to the GCS bucket - `python cli.py --upload`
- Once we generate a new version of the Strict Format Dataset, the next step is to use the Data Versioning container for version control. We follow the steps to `dvc add`, then `git add .`, `git commit`, and finally`dvc push`.

**Gemini Finetuner Container**

The container use the Strict Format Dataset from the GCS bucket, which contains 500 question & answer pairs, to fine-tune a Gemini 1.5 flash 002 model. 

- To finetune the model - `python cli.py --train`
- To chat with the finetuned model - `python cli.py --chat`
- To delete finetuned model - `python cli.py --delete_model`
- To delete the tuning job - `python cli.py --delete_hyperparameter_tuning_job`

Specifically, the configuration we use for finetuning is: `epochs=6` `adapter_size=4` `learning_rate_multiplier=1.0`

**Route Optimizer Container**

The container accepts a list of location names, retrieves their coordinates using the Geopy API, and calculates the optimal route between them using a greedy nearest-neighbor algorithm. The first location is randomly selected and the remaining locations are ordered by the shortest distance from the previous stop.

- To get the latitude and longitude of the locations and optimize the route: `python cli.py "Location1" "Location2" "Location3" ...`
- The CLI outputs the optimal order of locations starting from a random point and following the shortest path to the next location.

**Trip Advisor frontend Container**

This frontend allows users to input trip details, including destination city, type of trip, and travel dates. Once submitted, the user is redirected to a page that displays a map with trip suggestions based on the model. The map shows optimized routes between locations, and users can view details such as travel times, locations, reasons for each stop, and travel tips.

- To select travel preferences and submit the form, users can interact with dropdowns and date pickers in the UI.
- The map visualizes the generated trip itinerary, showing location routes and travel recommendations.

## Running Dockerfile
Instructions for running the individual Dockerfile. 
- `cd` into the directory such as `data-versioning`, `dataset-creator`, `gemini-finetuner`, or `rag`
- Make sure you have the perssion to run the file. You may - `chmod +x *.sh`
- To run Dockerfile - `./docker-shell.sh`

Instructions for running all the Dockerfile at once. 
- xxxxxxxxxx

**Models container**
- This container has scripts for model training, rag pipeline and inference
- Instructions for running the model container - `Instructions here`

**Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations.

----
You may adjust this template as appropriate for your project.

**Application Mockup Design**
