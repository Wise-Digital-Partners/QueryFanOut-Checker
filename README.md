Gemini Query Fan-Out Analyzer
=============================

This is a simple Streamlit application that analyzes a web page's content for potential Google AI Mode query fan-out. It works by "chunking" the page content and sending it to the Gemini API with a custom prompt to identify potential sub-queries, content gaps, and opportunities for better coverage.

Features
--------

-   Analyzes a given URL for its primary topic.

-   Predicts 8-10 likely "fan-out" queries that a large language model might generate to answer a user's comprehensive question.

-   Assesses the current content's coverage for each predicted query.

-   Identifies potential follow-up questions users might have.

-   Provides recommendations for filling content gaps.

How to Run Locally
------------------

### 1\. Clone the repository

First, clone this repository to your local machine using Git:

```
git clone [https://github.com/your-username/gemini-fanout-analyzer.git](https://github.com/your-username/gemini-fanout-analyzer.git)
cd gemini-fanout-analyzer

```

### 2\. Install dependencies

Make sure you have Python installed. Then, install the required libraries using the `requirements.txt` file:

```
pip install -r requirements.txt

```

### 3\. Get your Gemini API Key

You'll need a Gemini API key. You can get one by signing up for Google AI Studio.

### 4\. Run the app

To start the Streamlit application, run the following command in your terminal:

```
streamlit run streamlit_app.py

```

This will open the application in your web browser. Simply paste your Gemini API key and the URL you want to analyze into the text fields and click "Analyze URL" to see the results.

### Alternative: Securely storing your API key

For better security, especially if you plan to share this app on GitHub, you can store your API key in a `.streamlit/secrets.toml` file instead of entering it directly into the app.

1.  Create a `.streamlit` folder in your project directory.

2.  Inside the folder, create a file named `secrets.toml`.

3.  Add the following content to the `secrets.toml` file:

```
[gemini]
api_key = "YOUR_API_KEY_HERE"

```

Then, you can modify the `streamlit_app.py` script to read the key from this file, removing the need for the text input field:

```
import streamlit as st
# ... other imports

api_key = st.secrets["gemini"]["api_key"]
# ... rest of the code

```

This ensures your key is never committed to your Git repository.
