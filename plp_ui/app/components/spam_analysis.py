import streamlit as st
import pickle
import pandas as pd
import os
import matplotlib.pyplot as plt
import time

@st.cache_resource
def load_model_and_vectorizer(model_version):
    """Load trained model and vectorizer"""
    model_file = f'spam_model/spam_model_v{model_version}.pkl'
    vectorizer_file = f'spam_model/vectorizer_v{model_version}.pkl'
    
    try:
        # Load model
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        
        # Load vectorizer
        with open(vectorizer_file, 'rb') as f:
            vectorizer = pickle.load(f)
        
        return model, vectorizer, True
    except Exception as e:
        return None, None, str(e)

# Predict comment
def predict_comment(comment, model, vectorizer):
    """Predict if comment is spam"""
    if not comment or not isinstance(comment, str) or comment.strip() == "":
        return "Cannot analyze (empty comment)"
    
    try:
        # Convert comment text to feature vector
        comment_vector = vectorizer.transform([comment]).toarray()
        
        # Predict result
        prediction = model.predict(comment_vector)
        
        return prediction[0]
    except Exception as e:
        return f"Analysis error: {str(e)}"

def load_all_models_and_predict(comment):
    """Load all models and make predictions"""
    model_options = {
        1: "BernoulliNB",
        2: "MultinomialNB",
        3: "LogisticRegression",
        4: "SVM (LinearSVC)",
        5: "RandomForest"
    }
    
    results = {}
    
    for model_version in range(1, 6):
        model, vectorizer, status = load_model_and_vectorizer(model_version)
        if isinstance(status, str):
            results[model_version] = {
                "name": model_options[model_version],
                "result": f"Error: {status}",
                "is_error": True
            }
        else:
            prediction = predict_comment(comment, model, vectorizer)
            results[model_version] = {
                "name": model_options[model_version],
                "result": prediction,
                "is_error": False
            }
    
    return results

def show_spam_analysis():
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .header-container {
            display: flex;
            align-items: center;
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header-text {
            margin-left: 20px;
        }
        .result-spam {
            background-color: #ffcccc;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        .result-not-spam {
            background-color: #ccffcc;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        .result-error {
            background-color: #ffffcc;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        .stats-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .model-info {
            border-left: 3px solid #4CAF50;
            padding-left: 10px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state variables
    if 'total_tested' not in st.session_state:
        st.session_state.total_tested = 0
    if 'spam_count' not in st.session_state:
        st.session_state.spam_count = 0
    if 'not_spam_count' not in st.session_state:
        st.session_state.not_spam_count = 0
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'primary_model' not in st.session_state:
        st.session_state.primary_model = 1
    
    # Header with Logo
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/youtube-play.png", width=80)
    with col2:
        st.title("YouTube Comment Spam Detector")
        st.write("Analyze YouTube comments to detect spam using multiple machine learning models")
    
    # Main Interface
    st.markdown("---")
    
    # Top Row - Input Area and Stats
    top_col1, top_col2 = st.columns([3, 1])
    
    with top_col1:
        st.subheader("Comment Analysis")
        user_input = st.text_area(
            "Enter YouTube comment text:",
            height=120,
            placeholder="Type a comment here to analyze if it's spam..."
        )
        
        input_col1, input_col2, input_col3 = st.columns([1, 1, 2])
        with input_col1:
            analyze_button = st.button("Analyze Comment", use_container_width=True, type="primary")
        with input_col2:
            clear_button = st.button("Clear", use_container_width=True)
        with input_col3:
            model_options = {
                1: "BernoulliNB",
                2: "MultinomialNB",
                3: "LogisticRegression",
                4: "SVM (LinearSVC)",
                5: "RandomForest"
            }
            st.session_state.primary_model = st.selectbox(
                "Primary Model for Statistics",
                [1, 2, 3, 4, 5],
                index=0,
                format_func=lambda x: f"Model v{x} ({model_options[x]})"
            )
            
    with top_col2:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.subheader("Statistics")
        st.markdown(f"**Total analyzed:** {st.session_state.total_tested}")
        st.markdown(f"**Spam detected:** {st.session_state.spam_count}")
        st.markdown(f"**Normal comments:** {st.session_state.not_spam_count}")
        
        # Only show pie chart if we have data
        if st.session_state.total_tested > 0:
            fig, ax = plt.subplots(figsize=(3, 3))
            labels = ['Spam', 'Normal']
            sizes = [st.session_state.spam_count, st.session_state.not_spam_count]
            colors = ['#ff9999', '#66b3ff']
            explode = (0.1, 0)
            
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Handle clear button
    if clear_button:
        user_input = ""
        st.rerun()
    
    # Analysis Results
    if analyze_button and user_input:
        with st.spinner("Analyzing comment with all models..."):
            # Add a slight delay for UX
            time.sleep(0.5)
            
            # Get results from all models
            all_results = load_all_models_and_predict(user_input)
            
            # Update statistics based on primary model
            primary_result = all_results[st.session_state.primary_model]["result"] if not all_results[st.session_state.primary_model]["is_error"] else "ERROR"
            
            st.session_state.total_tested += 1
            
            if primary_result == "SPAM COMMENT":
                st.session_state.spam_count += 1
                result_text = "Spam Comment"
            elif primary_result == "NOT A SPAM COMMENT":
                st.session_state.not_spam_count += 1
                result_text = "Normal Comment"
            else:
                result_text = primary_result
            
            # Add to history
            st.session_state.history.append({
                "Comment": user_input,
                "Primary Result": result_text,
                "Model": f"v{st.session_state.primary_model} ({model_options[st.session_state.primary_model]})",
                "Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Display results
            st.markdown("---")
            st.subheader("Analysis Results")
            
            # Create results cards for all models
            result_cols = st.columns(5)
            
            for i, (model_num, result_info) in enumerate(all_results.items()):
                with result_cols[i]:
                    status = "ERROR" if result_info["is_error"] else \
                             "SPAM" if result_info["result"] == "SPAM COMMENT" else "NOT SPAM"
                    
                    result_class = "result-error" if result_info["is_error"] else \
                                  "result-spam" if status == "SPAM" else "result-not-spam"
                    
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; text-align: center;">
                        <h4>Model v{model_num}</h4>
                        <p>{result_info['name']}</p>
                        <div class="{result_class}">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Content Tabs
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["History", "Model Information", "Instructions"])
    
    with tab1:
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)
            st.dataframe(history_df, use_container_width=True)
            
            if st.button("Clear History"):
                st.session_state.history = []
                st.session_state.total_tested = 0
                st.session_state.spam_count = 0
                st.session_state.not_spam_count = 0
                st.rerun()
        else:
            st.info("No history yet. Analyzed comments will appear here.")
    
    with tab2:
        st.markdown("""
        <div class="model-info">
            <h4>Model v1: BernoulliNB</h4>
            <p>Bernoulli Naive Bayes algorithm, designed for binary features. Ideal for presence/absence based features in text.</p>
        </div>
        
        <div class="model-info">
            <h4>Model v2: MultinomialNB</h4>
            <p>Multinomial Naive Bayes algorithm, optimized for word frequency counts. Great for text classification tasks.</p>
        </div>
        
        <div class="model-info">
            <h4>Model v3: LogisticRegression</h4>
            <p>Logistic Regression classifier, excellent for binary classification problems with linear decision boundaries.</p>
        </div>
        
        <div class="model-info">
            <h4>Model v4: SVM (LinearSVC)</h4>
            <p>Linear Support Vector Machine, effective for high-dimensional data like text. Creates optimal dividing hyperplane.</p>
        </div>
        
        <div class="model-info">
            <h4>Model v5: RandomForest</h4>
            <p>Random Forest ensemble learning method, combines multiple decision trees to improve accuracy and prevent overfitting.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        ### How to Use This Tool
        
        1. **Enter a comment** in the text box at the top of the page.
        2. **Click "Analyze Comment"** to process the comment with all five models.
        3. **View the results** from each model displayed as color-coded cards.
        4. **Select a primary model** from the dropdown to determine which model's results are used for statistics.
        5. **Check the History tab** to view previously analyzed comments.
        6. **Explore the Model Information tab** to learn about the different algorithms used.
        
        ### Understanding Results
        
        - **Green**: The model classified the comment as NOT SPAM.
        - **Red**: The model classified the comment as SPAM.
        - **Yellow**: An error occurred with this model.
        
        ### Notes
        
        - Different models may provide different results for the same comment.
        - This tool is for educational and reference purposes only.
        - Results should be interpreted in context, considering the strengths and weaknesses of each algorithm.
        - The statistics pie chart reflects only the results from your selected primary model.
        """)