# Smart Canvas Search

## Overview

Smart Canvas Search is a locally run Python RAG application designed to enhance your learning experience by enabling you to search through your Canvas course files using natural language queries. It leverages natural language processing (NLP) techniques, including semantic text chunking, embedding generation, and hybrid search, to provide accurate and relevant search results.

This application is intended for local use, allowing you to process and search your Canvas files without relying on external cloud services for core functionality.


## Table of Contents
* [Features](#features)
* [Technologies Used](#technologies-used)
* [Installation](#installation)
* [Usage](#usage)


## Features

* **Canvas File Retrieval:** Downloads files from your specified Canvas course using the Canvas API.
* **File Parsing and Text Extraction:** Extracts text from various file types (PDF, DOCX, etc.).
* **Advanced Indexing:** Chunks text into semantically relevant segments and generates embeddings for efficient vector search.
* **Semantic Search:** Enables you to ask questions in natural language and retrieve relevant information from your course files.
* **Local Vector Database:** Utilizes a local vector database (Weaviate) for fast and private search.


## Technologies Used

* **Python:** Programming language.
* **Sentence Transformers:** Library for generating sentence embeddings.
* **Weaviate or ChromaDB:** Local vector database.
* **Canvas API:** For retrieving course files.
* **NLTK:** Natural Language Toolkit for text processing.
* **Requests:** For making HTTP requests.
* **PyPDF2, python-docx, openpyxl:** For file parsing.


## Installation

1.  **Clone the Repository:**

    ```bash
    git clone [your_repository_url]
    cd SmartCanvasSearch
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **NLTK Data:**
    ```bash
    python -m nltk.downloader punkt
    python -m nltk.downloader punkt_tab
    ```

5.  **Weaviate (Optional):**
    * If you are using Weaviate you will need to install docker, and then run the docker command provided in the code.
    * If you are using ChromaDB, no additional steps are needed.

6.  **Canvas API Credentials:**
    * Obtain your Canvas API credentials (API URL and API key) from your Canvas instance.
    * Add them to your configuration file or environment variables.


## Usage

1.  **Configure Canvas API:**
    * Update the configuration file or environment variables with your Canvas API credentials.

2.  **Run the Application:**

    ```bash
    python CanvasFileRetriever.py
    ```

3.  **Interact with the Application:**
    * The application will guide you through the process of selecting a course and asking questions.
