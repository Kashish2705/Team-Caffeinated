# Team-Caffeinated
Problem statement:
Develop an AI-powered system that automatically validates and assesses the quality of open-ended text responses in market
research surveys. The system should be able to identify and flag low-quality responses including gibberish text, bot-
generated content, off-topic answers, copy-pasted content, and inappropriate language. This will replace the current manual
review process where human reviewers have to read through thousands of responses to ensure data quality.

## 1. Overview
A standardized pre-processing procedure was followed before implementing core functionalities to assess data quality.
For the given training dataset , questions Q16A and Q16B were given the most priority while checking for quality of response since they actively required user to respond .


## Installation & Setup
The models used are lightweight and don't carry computational overhead. The entire code can be run on a standard PC with high computing capabilities.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Kashish2705/Team-Caffeinated.git
   cd Team-Caffeinated
   ```

2. **Create a Virtual Environment** (Optional but recommended)
   ```bash
   pip install pipenv
   pipenv install
   ```

3. **Install Dependencies**
   Using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory and add any required environment variables.

5. **Run the Flask Application**
   ```bash
   python app.py
   ```
   The app should now be running at `http://127.0.0.1:5000/`.

## Usage
- Open the `index.html` file in your browser.
- Use the Flask API for making predictions
- Modify `utils/` scripts to adapt the project as needed.



## 3. Core tasks (in addition to pre-processing
| S.No | Task                                    | Model / Method                  | Description|
|:-----:|:----------------------------------------|:----------------------------------|:--------|
| 1.    | Response Relevance to Question         | all-MiniLM-L6-v2 (lightweight)   | Create embeddings, used cosine similarity: Bi-encoder - used for text matching (match query and response) + normalized to get threshold (it is median value) |
| 2.    | Relevance to survey theme (boost keywords)                     | LDA (Topic Modelling)            | A list created to add key words that discover hidden topics; Increase relevance score of response if certain keywords are present  1 if > threshold = true else false |
| 3.    |        Repetitive/Contradictory responses per user            |                       Jaccard Similarity          | ∣A ∪ B∣ / ∣A ∩ B∣ (Because short responses and only one-line responses , thus better output) |
| 4.    | Detect AI-generated Responses          | Custom function (Responses too short , context has no role ) | One spacebar (used in ChatGPT) or consistent spacing + existence of punctuation marks |



## 5. Model training


## 6. Validation Results
