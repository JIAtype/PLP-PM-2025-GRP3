import streamlit as st

def show_home():
    st.title("Content Analysis Dashboard")
    
    st.markdown("""
    ## Welcome to the Content Analysis Platform
    
    This interactive dashboard provides customized analysis results for content creators and businesses.
    
    ### Available Features:
    
    **For Content Creators:**
    - Video-level analysis of comments and sentiments
    - Creator summary with overall sentiment percentages
    - Positive sentiment topic analysis
    - Entity sentiment analysis
    
    **For Business Users:**
    - Creator comparison overview
    - Multi-method sentiment analysis
    - Topic/aspect-based analysis
    - Time series trends and insights
    
    Use the sidebar to navigate to the appropriate section based on your needs.
    """)
    
    st.info("Select your user type from the sidebar to get started!")
    
    # Sample cards to illustrate available analyses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Content Creator Analytics")
        st.image("https://via.placeholder.com/300x150?text=Creator+Analytics", use_column_width=True)
        st.markdown("Gain insights into your content performance and audience sentiment")
    
    with col2:
        st.subheader("Business Intelligence")
        st.image("https://via.placeholder.com/300x150?text=Business+Intelligence", use_column_width=True)
        st.markdown("Compare creators and discover trends to inform your marketing strategy") 