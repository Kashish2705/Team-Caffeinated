# -*- coding: utf-8 -*-
"""c5i_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LDS82aZUFWdYUFNiQ7aUdQWePKYvTjPQ
"""

import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import re

def process(filename):
    # Load a specific sheet by index (e.g., first sheet, index 0)
    df = pd.read_excel(filename, sheet_name=1)

    """**PRE-PROCESSING**

    ---


    """

    na_values = {"no", "na", "null", "n/a", "not applicable", "nan"}

    df = df.apply(
        lambda x: "na" if str(x).strip().lower() in na_values else x
    )

    df = df.applymap(lambda x: x.encode("utf-8", "ignore").decode("utf-8") if isinstance(x, str) else x)

    # Initialize stop words
    stop_words = set(stopwords.words('english'))

    # Function to remove stop words from responses
    def remove_stopwords(text):
        # Check if text is a string before applying split
        if isinstance(text, str):
            words = text.split()
            filtered_words = [word for word in words if word not in stop_words]
            return " ".join(filtered_words)
        # If not a string, return the original value (or handle it differently)
        else:
            return text

    # Assuming df is your DataFrame
    df['Q16A'] = df['Q16A. What is the most important thing you LIKE about the shown concept}?     This can include anything you would want kept for sure or aspects that might drive you to buy or try it…       Please type a detailed response in the space below'].astype(str)
    df['Q16A'] = df['Q16A'].apply(remove_stopwords)
    df['Q16B'] = df['Q16B. What is the most important thing you DISLIKE about the shown concept}?    This can include general concerns, annoyances, or any aspects of the product that need fixed for this to be more appealing to you...     Please type a detailed response in the space below.'].astype(str)
    df['Q16B'] = df['Q16B'].apply(remove_stopwords)

    df.fillna("na", inplace= True)

    # Function to process each comment
    def lemmatize_comment(comment):
        sentences = nltk.sent_tokenize(comment)  # Split comment into sentences
        lemmatized_sentences = []
        lemmatizer = WordNetLemmatizer()

        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            if len(words) == 1 and words[0] == "na":
                lemmatized_sentences.append("na")
                break
            lemmatized_words = [lemmatizer.lemmatize(word) for word in words if word.lower() not in stopwords.words('english')]
            lemmatized_sentence = ' '.join(lemmatized_words)
            lemmatized_sentences.append(lemmatized_sentence)

        # Join all lemmatized sentences back into a single string for the comment
        return " ".join(lemmatized_sentences)

    df['Q16A'] = df['Q16A'].apply(lemmatize_comment)
    df['Q16B'] = df['Q16B'].apply(lemmatize_comment)
    df.head()

    """**SEMANTIC RELEVANCE**

    ---


    """

    # Load the bi-encoder model
    bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')

    # Define questions
    question1 = "Q16A. What is the most important thing you LIKE about the shown concept}?     This can include anything you would want kept for sure or aspects that might drive you to buy or try it…       Please type a detailed response in the space below"
    question2 = "Q16B. What is the most important thing you DISLIKE about the shown concept}?    This can include general concerns, annoyances, or any aspects of the product that need fixed for this to be more appealing to you...     Please type a detailed response in the space below."

    # Encode questions
    q1_embedding = bi_encoder.encode(question1, convert_to_tensor=True)
    q2_embedding = bi_encoder.encode(question2, convert_to_tensor=True)

    # Load responses (assuming 'responses_col1' and 'responses_col2' exist)
    responses_col1 = df['Q16A'].astype(str).tolist()
    responses_col2 = df['Q16B'].astype(str).tolist()

    # Encode responses separately
    embeddings_col1 = bi_encoder.encode(responses_col1, convert_to_tensor=True)
    embeddings_col2 = bi_encoder.encode(responses_col2, convert_to_tensor=True)

    # Compute cosine similarities
    sim_col1 = util.pytorch_cos_sim(q1_embedding, embeddings_col1)[0].cpu().numpy()
    sim_col2 = util.pytorch_cos_sim(q2_embedding, embeddings_col2)[0].cpu().numpy()

    # Normalize scores dynamically
    def normalize_scores(similarities):
        min_sim, max_sim = np.min(similarities), np.max(similarities)
        return (similarities - min_sim) / (max_sim - min_sim) if max_sim - min_sim > 0 else similarities

    normalized_scores_col1 = normalize_scores(sim_col1)
    normalized_scores_col2 = normalize_scores(sim_col2)

    # Define a better threshold using the median
    threshold_col1 = np.percentile(normalized_scores_col1, 50)
    threshold_col2 = np.percentile(normalized_scores_col2, 50)

    # Boost relevant short responses
    '''boost_keywords = {
        "premium", "superior", "taste", "color", "shape", "design", "crisp", "refreshing", "smooth", "clean", "pure",
        "healthy", "carb", "light", "low", "calorie", "natural", "organic", "homegrown", "ingredients",
        "finest", "authentic", "sleek", "modern", "stylish", "elegant", "price", "cheap", "inexpensive", "expensive",
        "sophisticated", "golden", "exclusive", "elite", "luxurious", "aspirational", "nothing", "service"
    }'''

    # LDA model
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    df['cleaned_text'] = df['Q16A'].astype(str) + ' ' + df['Q16B'].astype(str)
    X = vectorizer.fit_transform(df['cleaned_text'])
    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(X)

    # Gather words by topics
    def gather_topic_words(model, feature_names, num_top_words):
        topic_words = set()  # Use a set to avoid duplicates
        for idx, topic in enumerate(model.components_):
            words = [feature_names[i] for i in topic.argsort()[:-num_top_words - 1:-1]]
            topic_words.update(words)  # Add words to the set
        return topic_words

    # Gather words from topics
    boost_keywords = gather_topic_words(lda, vectorizer.get_feature_names_out(), 10)

    def boost_score(response, score):
        words = response.lower().split()
        if len(words) == 1 and words[0] == "na":
            return 1  # Automatically relevant if "na"
        if any(word in boost_keywords for word in words):
            return min(score + 0.4, 1.0)  # Apply boost
        return score

    # Apply boosting
    boosted_scores_col1 = [boost_score(resp, normalized_scores_col1[i]) for i, resp in enumerate(responses_col1)]
    boosted_scores_col2 = [boost_score(resp, normalized_scores_col2[i]) for i, resp in enumerate(responses_col2)]

    # Convert scores to binary (1 if above threshold, else 0)
    binary_relevance_col1 = [1 if score > threshold_col1 else 0 for score in boosted_scores_col1]
    binary_relevance_col2 = [1 if score > threshold_col2 else 0 for score in boosted_scores_col2]

    #Store results in a DataFrame
    df_results = pd.DataFrame({
        "16A_text": df['Q16A. What is the most important thing you LIKE about the shown concept}?     This can include anything you would want kept for sure or aspects that might drive you to buy or try it…       Please type a detailed response in the space below'],
        'Response_Column1': responses_col1,
        'Relevance_Column1': binary_relevance_col1,
        "16B_text": df['Q16B. What is the most important thing you DISLIKE about the shown concept}?    This can include general concerns, annoyances, or any aspects of the product that need fixed for this to be more appealing to you...     Please type a detailed response in the space below.'],
        'Response_Column2': responses_col2,
        'Relevance_Column2': binary_relevance_col2
    })


    # Save the entire DataFrame, not just the modified columns
    df_results.to_csv('relevance.csv')


    df['Q16A'] =binary_relevance_col1
    df['Q16B'] = binary_relevance_col2

    columns_to_keep = ['Unique ID', 'Start Date', 'End Date',
        'Q1. What is your current age? \n(Age)',
        'Q2. What is your gender? \n(Gender)',
        'Q3. Which of the following best describes the area or community in which you live? \n(Urban/Rural)',
        'Q4.  Please indicate the answer that includes your entire household income in (previous year) before taxes. \n(Income)',
        'Q6 Which of the following types of alcoholic beverages have you consumed in the past 4 weeks?\n(Alcohol Category)',
        'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12',
        'Unnamed: 13', 'Unnamed: 14',
        'Q7. Which of the following beer types of have you consumed in the past 4 weeks? \n(Beer Category )',
        'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19',
        'Unnamed: 20', 'Unnamed: 21',
        'Q9. How relevant would you say the shown product is to you based on what you saw and read?\n(Concept Relevance)',
        'Q10. How appealing or unappealing is the shown product  to you?\n(Concept Appeal)',
        'Q11. How different do you think the shown product is from other beers currently available for purchase?\n(Concept Differentiation)',
        'Q12. Thinking about the shown product, which option describes how believable or unbelievable you feel the description and statements made about it are?\n(Concept Beleivability)',
        'Q13. How does the price fit with what you’d expect the shown to cost?\n(Concept_Price)',
        'Q14. Which statement below best describes how likely you would be to buy shown product if it were available at your local stores?\n(Concept_Purchase Intent)',
        'Q15. If the shwon product was available to you, how often would you expect yourself to drink at least one of these products?\n(Concept_Drinking Frequency)',
        'Q16A',
        'Q16B',
        'Q17. We would like to know what effect this new product might have on the other beverages you buy. If it were available, would the shown product…? \n(Concept_Replacement Product)',
        'Q18_1 What specific product that you are currently using would the shown product replace?\n Please type in ONE specific brand or product per space provided.',
        'Q18_2 What specific product that you are currently using would the shown concept replace?\n Please type in ONE specific brand or product per space provided.',
        'Q18_3 What specific product that you are currently using would the shown concept replace?\n Please type in ONE specific brand or product per space provided.'
        ]  # Replace with actual columns you want
    df_new = df[columns_to_keep].copy()

    # Save the entire DataFrame, not just the modified columns
    df_new.to_csv('test_data.csv')
    return 'test_data.csv'


# """**AI - GENERATED RESPONSE DETECTION**

# ---


# """

# # Function to check if text is likely AI-generated
# def is_ai_generated(text):
#     # Convert to string to handle potential non-string types
#     text = str(text)
#     # Check for consistent spacing (only one space between words)
#     if re.search(r'\s{2,}', text):  # More than one space
#         return False

#     # Check for proper punctuation (at least one full stop or comma)
#     if not re.search(r'[.,]', text):  # No full stops or commas
#         return False

#     return True  # Likely AI-generated if both conditions are met

# # Apply the function to all relevant columns
# columns_to_check = [
#     df.columns[26],  # Q16A
#     df.columns[27],  # Q16B
#     df.columns[28],  # Q18_1
#     df.columns[29],  # Q18_2
#     df.columns[30]   # Q18_3
# ]

# # Create a new column to flag AI-generated responses
# for column in columns_to_check:
#     df[f'{column}_ai_generated'] = df[column].fillna('').apply(is_ai_generated)

# # Update 'OE_Quality_Flag' column based on AI-generated responses
# # Assuming 'OE_Quality_Flag' is the column you want to modify
# # Convert to string to ensure compatibility
# df_new['OE_Quality_Flag'] = df[[f'{column}_ai_generated' for column in columns_to_check]].any(axis=1).astype(str)

# """**REPETITION AND CONTRADICTION CHECKS**

# ---


# """

# import pandas as pd
# import numpy as np
# import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import TruncatedSVD
# from sklearn.metrics import jaccard_score
# from sklearn.preprocessing import MultiLabelBinarizer

# # Load data
# df = pd.read_excel('Final Data File_Training.xlsx', sheet_name='Data Set with Labels Text')

# # Dynamically extract text columns for LSA and profanity detection
# text_columns = [col for col in df.columns if 'LIKE' in col or 'DISLIKE' in col]
# df['combined_text'] = df[text_columns].fillna('').agg(' '.join, axis=1)

# # Text cleaning
# def clean_text(text):
#     text = re.sub(r'[^a-zA-Z0-9\s]', '', str(text))  # Remove special characters
#     text = text.lower()                               # Lowercase
#     return text

# df['cleaned_text'] = df['combined_text'].apply(clean_text)

# # Function to calculate Jaccard similarity
# def jaccard_similarity(responses):
#     # Filter out empty responses to prevent ValueError
#     responses = [response for response in responses if response and response.strip()]
#     # If all responses are empty, return False (not similar)
#     if not responses:
#         return False

#     # Create a set of words for each response
#     response_sets = [set(response.split()) for response in responses]

#     # Compute Jaccard similarity matrix
#     jaccard_sim_matrix = np.zeros((len(response_sets), len(response_sets)))

#     for i in range(len(response_sets)):
#         for j in range(len(response_sets)):
#             if i != j:
#                 intersection = len(response_sets[i].intersection(response_sets[j]))
#                 union = len(response_sets[i].union(response_sets[j]))
#                 jaccard_sim_matrix[i][j] = intersection / union if union > 0 else 0

#     # Check if any pair of responses has a Jaccard similarity above a threshold (e.g., 0.5)
#     return any(jaccard_sim_matrix[i][j] > 0.5 for i in range(len(jaccard_sim_matrix)) for j in range(i + 1, len(jaccard_sim_matrix)))

# # Updated detect_repeated_responses function
# def detect_repeated_responses(row):
#     response_columns = [
#         df.columns[26],  # Q16A
#         df.columns[27],  # Q16B
#         df.columns[28],  # Q18_1
#         df.columns[29],  # Q18_2
#         df.columns[30]   # Q18_3
#     ]
#     responses = row[response_columns].fillna('').values
#     # Check if all non-empty responses are similar
#     return int(jaccard_similarity([response for response in responses]))

# df['repeated_response'] = df.apply(detect_repeated_responses, axis=1)

# # Save results
# df.to_csv('s.csv', index=False)

