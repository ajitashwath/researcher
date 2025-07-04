import streamlit as st
import sys
import os
from datetime import datetime
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from create_report.main import ReportCreator

def main():
    st.set_page_config(
        page_title="AI Report Generator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .report-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .stTextInput > div > div > input {
        border: 2px solid #667eea;
        border-radius: 5px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Report Generator</h1>
        <p>Generate comprehensive reports on any topic using AI agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Configuration")
        
        # Report type selection
        report_type = st.selectbox(
            "Select Report Type",
            ["Comprehensive Analysis", "Executive Summary", "Technical Deep Dive", "Market Research", "Strategic Planning"]
        )
        
        # Report length
        report_length = st.slider("Report Length (pages)", 1, 10, 5)
        
        # Additional options
        include_charts = st.checkbox("Include Data Visualizations", value=True)
        include_sources = st.checkbox("Include Source References", value=True)
        
        st.divider()
        
        # Example topics
        st.subheader("💡 Example Topics")
        example_topics = [
            "How to improve infrastructure in Bangalore?",
            "Impact of AI on healthcare industry",
            "Sustainable energy solutions for urban areas",
            "Digital transformation in education",
            "Future of remote work post-pandemic"
        ]
        
        for topic in example_topics:
            if st.button(f"📝 {topic}", key=f"example_{topic}"):
                st.session_state.topic_input = topic
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Enter Your Topic")
        
        # Topic input
        topic = st.text_input(
            "What would you like to create a report on?",
            value=st.session_state.get('topic_input', ''),
            placeholder="e.g., How to improve infrastructure in Bangalore?",
            help="Enter any topic you want to generate a comprehensive report on"
        )
        
        # Generate button
        if st.button("🚀 Generate Report", type="primary"):
            if topic.strip():
                generate_report(topic, report_type, report_length, include_charts, include_sources)
            else:
                st.error("Please enter a topic for the report!")
    
    with col2:
        st.header("📊 Report Stats")
        
        # Display session statistics
        if 'reports_generated' not in st.session_state:
            st.session_state.reports_generated = 0
        
        st.metric("Reports Generated", st.session_state.reports_generated)
        st.metric("Current Session", f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Recent reports
        if 'recent_reports' in st.session_state and st.session_state.recent_reports:
            st.subheader("📚 Recent Reports")
            for report in st.session_state.recent_reports[-3:]:
                st.write(f"• {report}")

def generate_report(topic, report_type, report_length, include_charts, include_sources):
    """Generate report using CrewAI agents"""
    
    # Initialize progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update progress
        status_text.text("🔄 Initializing AI agents...")
        progress_bar.progress(10)
        
        # Initialize report creator
        report_creator = ReportCreator()
        
        # Update progress
        status_text.text("🔍 Researching topic...")
        progress_bar.progress(30)
        
        # Create report configuration
        config = {
            'topic': topic,
            'report_type': report_type,
            'length': report_length,
            'include_charts': include_charts,
            'include_sources': include_sources
        }
        
        # Update progress
        status_text.text("📝 Generating report...")
        progress_bar.progress(50)
        
        # Generate the report
        report = report_creator.create_report(config)
        
        # Update progress
        status_text.text("✅ Report generated successfully!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Display the report
        display_report(report, topic)
        
        # Update session state
        st.session_state.reports_generated += 1
        if 'recent_reports' not in st.session_state:
            st.session_state.recent_reports = []
        st.session_state.recent_reports.append(topic)
        
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_report(report, topic):
    """Display the generated report"""
    
    st.success("🎉 Report Generated Successfully!")
    
    # Report header
    st.markdown("---")
    st.markdown(f"# 📊 Report: {topic}")
    st.markdown(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}")
    st.markdown("---")
    
    # Report content in a nice container
    with st.container():
        st.markdown(f"""
        <div class="report-container">
            {report}
        </div>
        """, unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name=f"report_{topic.replace(' ', '_').replace('?', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
    # Share options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Email Report"):
            st.info("Email functionality would be implemented here")
    
    with col2:
        if st.button("🔗 Share Link"):
            st.info("Share link functionality would be implemented here")
    
    with col3:
        if st.button("📋 Copy to Clipboard"):
            st.info("Copy functionality would be implemented here")

if __name__ == "__main__":
    main()