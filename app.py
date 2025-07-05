__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

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
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
        background: #000000;
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
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("📋 Configuration")
        
        # API Key Input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            help="Enter your OpenAI API key to use the report generator. This key is not stored on any server.",
            placeholder="sk-..."
        )
        
        # Store API key in session state
        if api_key:
            st.session_state.openai_api_key = api_key
        
        # Report Configuration
        report_type = st.selectbox(
            "Select Report Type",
            ["Comprehensive Analysis", "Executive Summary", "Technical Deep Dive", "Market Research", "Strategic Planning"],
            index=0
        )
        
        report_length = st.slider("Report Length (pages)", 1, 10, 5)
        include_charts = st.checkbox("Include Data Visualizations", value=True)
        include_sources = st.checkbox("Include Source References", value=True)
        
        st.divider()
        
        # Example Topics
        st.subheader("💡 Example Topics")
        example_topics = [
            "How to improve infrastructure in Bangalore?",
            "Impact of AI on healthcare industry",
            "Sustainable energy solutions for urban areas",
            "Digital transformation in education",
            "Future of remote work post-pandemic"
        ]
        
        for topic in example_topics:
            if st.button(f"📝 Use: {topic[:25]}...", key=f"example_{topic}"):
                st.session_state.topic_input = topic
                st.rerun()
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Enter Your Topic")
        
        # Topic Input
        topic = st.text_input(
            "What would you like to create a report on?",
            value=st.session_state.get('topic_input', ''),
            placeholder="e.g., How to improve infrastructure in Bangalore?",
            help="Enter any topic you want to generate a comprehensive report on"
        )
        
        # Generate Button
        if st.button("🚀 Generate Report", type="primary"):
            if not topic.strip():
                st.error("❌ Please enter a topic for the report!")
            elif not api_key:
                st.error("❌ Please enter your OpenAI API key in the sidebar!")
            else:
                # Clear previous topic from session state
                if 'topic_input' in st.session_state:
                    del st.session_state['topic_input']
                
                # Generate report
                generate_report(topic, report_type, report_length, include_charts, include_sources, api_key)
    
    with col2:
        st.header("📊 Report Stats")
        
        # Initialize session state variables
        if 'reports_generated' not in st.session_state:
            st.session_state.reports_generated = 0
        if 'recent_reports' not in st.session_state:
            st.session_state.recent_reports = []
        
        # Display metrics
        st.metric("Reports Generated", st.session_state.reports_generated)
        st.metric("Current Session", f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Recent Reports
        if st.session_state.recent_reports:
            st.subheader("📚 Recent Reports")
            for i, report in enumerate(st.session_state.recent_reports[-3:]):
                st.write(f"{i+1}. {report[:30]}...")

def generate_report(topic, report_type, report_length, include_charts, include_sources, api_key):
    """Generate report with proper error handling and UI feedback"""
    
    # Validate inputs
    if not api_key:
        st.error("❌ OpenAI API key is required!")
        return
    
    if not topic.strip():
        st.error("❌ Please enter a topic for the report!")
        return
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Initialize
        status_text.text("🔄 Initializing AI Report Generator...")
        progress_bar.progress(10)
        
        # Create report creator with API key
        report_creator = ReportCreator(api_key=api_key)
        
        # Step 2: Prepare configuration
        status_text.text("⚙️ Preparing report configuration...")
        progress_bar.progress(20)
        
        config = {
            'topic': topic,
            'report_type': report_type,
            'length': report_length,
            'include_charts': include_charts,
            'include_sources': include_sources
        }
        
        # Step 3: Start report generation
        status_text.text("🔍 Conducting research and analysis...")
        progress_bar.progress(40)
        
        # Generate the report
        report = report_creator.create_report(config)
        
        # Step 4: Finalize
        status_text.text("✅ Report generated successfully!")
        progress_bar.progress(100)
        
        # Brief pause to show completion
        time.sleep(1)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display the report
        display_report(report, topic, config)
        
        # Update session state
        st.session_state.reports_generated += 1
        st.session_state.recent_reports.append(topic)
        
        # Keep only last 10 reports
        if len(st.session_state.recent_reports) > 10:
            st.session_state.recent_reports = st.session_state.recent_reports[-10:]
        
        # Success message
        st.success("🎉 Report generated successfully!")
        
    except ValueError as ve:
        # Handle API key or validation errors
        error_msg = str(ve)
        if "API key" in error_msg:
            st.error("❌ Invalid OpenAI API key. Please check your API key and try again.")
        else:
            st.error(f"❌ Configuration error: {error_msg}")
        
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        # Handle other errors
        st.error(f"❌ Error generating report: {str(e)}")
        st.info("💡 Please check your API key and internet connection, then try again.")
        
        progress_bar.empty()
        status_text.empty()

def display_report(report, topic, config):
    """Display the generated report with proper formatting"""
    
    st.markdown("---")
    st.markdown(f"# 📊 {config['report_type']}: {topic}")
    st.markdown(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}")
    st.markdown(f"**Report Type:** {config['report_type']} | **Length:** {config['length']} pages")
    st.markdown("---")
    
    # Display report content
    with st.container():
        st.markdown(f"""
        <div class="report-container">
            <div style="white-space: pre-wrap; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;">
                {report}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Create filename
        safe_topic = topic.replace(' ', '_').replace('?', '').replace('/', '_')[:30]
        filename = f"report_{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=filename,
            mime="text/plain",
            help="Download the generated report as a text file"
        )

if __name__ == "__main__":
    main()