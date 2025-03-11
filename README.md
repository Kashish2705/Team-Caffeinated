# Team-Caffeinated
Problem statement:
Develop an AI-powered system that automatically validates and assesses the quality of open-ended text responses in market
research surveys. The system should be able to identify and flag low-quality responses including gibberish text, bot-
generated content, off-topic answers, copy-pasted content, and inappropriate language. This will replace the current manual
review process where human reviewers have to read through thousands of responses to ensure data quality.

## 1. Overview


## 2. Setup



## 3. Core tasks 
| S.No | Task                                    | Model / Library                  | Method |
|:-----:|:----------------------------------------|:----------------------------------|:--------|
| 1.    | Response Relevance to Question         | all-MiniLM-L6-v2 (lightweight)   | Create embeddings, used cosine similarity: Bi-encoder - used for text matching (match query and response) + normalized to get threshold (it is median value) |
| 2.    | Boost Keywords                         | LDA (Topic Modelling)            | Helps discover hidden topics; Increase relevance score if certain keywords are present (Hardcoded as of now) - 1 if > threshold = true else false |
| 3.    | Excluding 18th Question                | SVM Classifier                   | Random state = 42, random shuffling |
| 4.    | Jaccard Similarity                     | -                                | ∣A ∪ B∣ / ∣A ∩ B∣ (Because short responses and only one-line responses) |
| 5.    | Repetition of Responses                | -                                | Flagged if response is duplicated |
| 6.    | Detect AI-generated Responses          | -                                | One spacebar (used in ChatGPT) + punctuation marks exist |
| 7.    | AI-generated Response Detection        | -                                | Responses too short to conclude anything; Looked for proper spacing and punctuation, as context cannot play a role here clearly |


## 5. Model training

## 6. Demo

## 7. Validation Results
