import streamlit as st
from app.pages.home import show_home
from app.pages.creator import show_creator_page
from app.pages.business import show_business_page

def set_custom_styles():
    """设置自定义CSS样式"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            margin-bottom: 1rem;
        }
        .subheader {
            font-size: 1.5rem;
            color: #424242;
            margin-bottom: 1rem;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f0f2f6;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.8rem;
            color: #424242;
            border-top: 1px solid #ddd;
        }
        /* 修改这里：将flex方向改为垂直排列 */
        .stRadio > div {
            display: flex;
            flex-direction: column;  /* 改为垂直排列 */
            align-items: flex-start;  /* 左对齐 */
            gap: 0.5rem;              /* 添加选项间距 */
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 设置页面配置
    st.set_page_config(
        page_title="INSIGHTX Comments Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用自定义样式
    set_custom_styles()
    
    # 初始化会话状态
    if 'user_type' not in st.session_state:
        st.session_state.user_type = "Home"
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("<h1>INSIGHTX</h1>", unsafe_allow_html=True)
        st.markdown("### Video Comments Analysis")
        st.markdown("---")
        
        # 映射用户类型到带图标的选项
        user_type_mapping = {
            "Home": "🏕️ Instruction",
            "Content Creator": "📈 Content Creator",
            "Business": "📊 Business"
        }
        
        # 根据当前会话状态确定默认选项
        default_index = 0  # 默认为Home
        options = list(user_type_mapping.values())
        
        if st.session_state.user_type in user_type_mapping:
            default_index = list(user_type_mapping.keys()).index(st.session_state.user_type)
        
        # 用户类型选择 - 带图标的导航
        selected = st.radio(
            "Select User Type",
            options,
            index=default_index
        )
        
        # 更新会话状态 - 移除图标保留文本
        for key, value in user_type_mapping.items():
            if value == selected:
                st.session_state.user_type = key
                break
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This dashboard helps analyze YouTube 
        comments sentiment and trends to gain 
        actionable insights.
        """)
    
    # 显示主标题
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/youtube-play.png", width=80)
    with col2:
        st.markdown("<h1 class='main-header'>YouTube Comments Analysis</h1>", unsafe_allow_html=True)
    
    # 根据用户类型显示相应页面
    with st.spinner(f"Loading {st.session_state.user_type} dashboard..."):
        if st.session_state.user_type == "Home":
            show_home()
        elif st.session_state.user_type == "Content Creator":
            show_creator_page()
        elif st.session_state.user_type == "Business":
            show_business_page()
    
    # 添加页脚
    st.markdown(
        """
        <div class="footer">
            © 2025 INSIGHTX YouTube Sentiment Analysis Dashboard | All Rights Reserved
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 