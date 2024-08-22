from flask import Flask, request, jsonify
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS for all routes

# Load models and data
tfidf_job_title_model = joblib.load('tfidf_job_title_model.pkl')
svd_job_title_model = joblib.load('svd_job_title_model.pkl')
job_title_lsa = joblib.load('job_title_lsa.pkl')
df_encoded = joblib.load('df_encoded.pkl')

@app.route('/')
def home():
    return "Welcome to the Job Title Recommendation API!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_job_title = data.get('job_title', '')

    # Transform and compute recommendations
    input_tfidf = tfidf_job_title_model.transform([input_job_title])
    input_lsa = svd_job_title_model.transform(input_tfidf)
    cosine_sim = cosine_similarity(input_lsa, job_title_lsa).flatten()
    df_encoded['similarity_score'] = cosine_sim
    recommendations = df_encoded.sort_values(by='similarity_score', ascending=False)
    
    # Get top 5 recommendations
    top_recommendations = recommendations[['JD_tokens_str', 'Location', 'Average Salary', 'Industry_tokens', 'similarity_score']].head(5)
    
    return jsonify(top_recommendations.to_dict(orient='records'))

if __name__ == '__main__':
    #flask deployment
    #app.run(debug=True, port=5000)
    #azure deployment
    app.run(host='0.0.0.0', port=8000)
