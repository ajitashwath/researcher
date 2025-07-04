__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

from crewai import Agent, Task, Crew
import os
from datetime import datetime
import logging
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAITool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def research(self, query: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a research analyst. Provide comprehensive research on the given topic with current information, statistics, and credible insights."},
                    {"role": "user", "content": f"Research and provide detailed information about: {query}"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI research error: {str(e)}")
            return f"Research unavailable for: {query}"
    
    def analyze(self, content: str, topic: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst. Analyze the provided content and extract key insights, trends, and recommendations."},
                    {"role": "user", "content": f"Analyze this content about {topic}:\n\n{content}"}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            return f"Analysis unavailable for: {topic}"

class CrewOutput:
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self):
        return self.content

class ReportCreator:
    def __init__(self):
        self.setup_tools()
        self.setup_agents()
    
    def setup_tools(self):
        try:
            self.openai_tool = OpenAITool()
            logger.info("OpenAI tool initialized successfully")
        except Exception as e:
            logger.error(f"Could not initialize OpenAI tool: {str(e)}")
            self.openai_tool = None
        
    def setup_agents(self):       
        # Research Agent
        self.researcher = Agent(
            role="Senior Research Analyst",
            goal="Conduct comprehensive research on the given topic and gather relevant, accurate information",
            backstory="""You are a senior research analyst with expertise in gathering and analyzing 
            information from various sources. You have a keen eye for detail and can distinguish 
            between credible and unreliable sources. You excel at finding the most current and 
            relevant information on any topic.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
        
        # Content Writer Agent
        self.writer = Agent(
            role="Professional Content Writer",
            goal="Create well-structured, engaging, and comprehensive reports based on research findings",
            backstory="""You are a professional content writer with years of experience in creating 
            reports, articles, and documentation. You have the ability to transform complex research 
            findings into clear, engaging, and well-structured content that is easy to understand 
            for the target audience.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Quality Assurance Agent
        self.reviewer = Agent(
            role="Quality Assurance Specialist",
            goal="Review and improve the quality, accuracy, and completeness of the generated report",
            backstory="""You are a quality assurance specialist with expertise in reviewing and 
            improving written content. You have a sharp eye for inconsistencies, gaps in information, 
            and areas that need improvement. You ensure that all reports meet the highest standards 
            of quality and accuracy.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Data Analyst Agent
        self.analyst = Agent(
            role="Data Analyst",
            goal="Analyze data, identify trends, and provide insights to support the report",
            backstory="""You are a data analyst with strong analytical skills and experience in 
            interpreting data to extract meaningful insights. You can identify patterns, trends, 
            and correlations that add value to reports and help in decision-making.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_report(self, config: Dict[str, Any]) -> str:
        try:
            logger.info(f"Starting report creation for topic: {config['topic']}")
            research_data = ""
            if self.openai_tool:
                research_data = self.openai_tool.research(config['topic'])
                logger.info("Research data gathered from OpenAI")
            tasks = self.create_tasks(config, research_data)
            
            crew = Crew(
                agents=[self.researcher, self.writer, self.analyst, self.reviewer],
                tasks=tasks,
                verbose=True
            )
            
            result = crew.kickoff()
            logger.info("Report creation completed successfully")
            return str(result)
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return self.create_fallback_report(config)
    
    def create_tasks(self, config: Dict[str, Any], research_data: str = "") -> list:
        topic = config['topic']
        report_type = config['report_type']
        length = config['length']
        
        # Research Task
        research_task = Task(
            description=f"""
            Conduct comprehensive research on the topic: "{topic}"
            
            Additional research data available:
            {research_data}
            
            Your research should include:
            1. Current state and background information
            2. Key challenges and opportunities
            3. Best practices and solutions
            4. Recent developments and trends
            5. Statistical data and factual information
            6. Expert opinions and case studies
            
            Focus on gathering credible, up-to-date information from reliable sources.
            The research should be thorough enough to support a {length}-page {report_type.lower()}.
            """,
            expected_output="A comprehensive research summary with key findings, data points, and source references",
            agent=self.researcher
        )
        
        # Analysis Task
        analysis_task = Task(
            description=f"""
            Analyze the research findings for the topic: "{topic}"
            
            Your analysis should include:
            1. Identify key patterns and trends
            2. Highlight critical insights and implications
            3. Assess the significance of different findings
            4. Provide data-driven recommendations
            5. Identify gaps or areas needing further attention
            
            Focus on extracting actionable insights that will strengthen the report.
            """,
            expected_output="A detailed analysis with insights, trends, and recommendations based on research findings",
            agent=self.analyst
        )
        
        # Writing Task
        writing_task = Task(
            description=f"""
            Create a comprehensive {report_type.lower()} report on: "{topic}"
            
            The report should be approximately {length} pages long and include:
            
            1. Executive Summary
            2. Introduction and Background
            3. Current State Analysis
            4. Key Challenges and Opportunities
            5. Proposed Solutions and Recommendations
            6. Implementation Strategies
            7. Expected Outcomes and Benefits
            8. Conclusion and Next Steps
            
            Writing guidelines:
            - Use clear, professional language
            - Include relevant data and statistics
            - Provide specific examples and case studies
            - Make it engaging and easy to read
            - Ensure logical flow and structure
            - Include actionable recommendations
            
            {"Include references to sources and data visualizations as requested." if config.get('include_sources') else ""}
            """,
            expected_output=f"A well-structured, comprehensive {report_type.lower()} report of approximately {length} pages",
            agent=self.writer
        )
        
        # Review Task
        review_task = Task(
            description=f"""
            Review and improve the generated report on: "{topic}"
            
            Your review should focus on:
            1. Accuracy and factual correctness
            2. Completeness and comprehensiveness
            3. Clarity and readability
            4. Logical structure and flow
            5. Actionability of recommendations
            6. Overall quality and professionalism
            
            Provide the final, polished version of the report with any necessary improvements.
            Ensure the report meets the requirements for a {report_type.lower()} of {length} pages.
            """,
            expected_output="A final, polished, and high-quality report ready for presentation",
            agent=self.reviewer
        )
        
        return [research_task, analysis_task, writing_task, review_task]
    
    def create_fallback_report(self, config: Dict[str, Any]) -> str:
        topic = config['topic']
        report_type = config['report_type']
        if self.openai_tool:
            try:
                response = self.openai_tool.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a professional report writer. Create a comprehensive {report_type.lower()} report."},
                        {"role": "user", "content": f"Create a detailed {config['length']}-page report on: {topic}"}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Fallback OpenAI report failed: {str(e)}")
        
        return f"""
# {report_type}: {topic}

**Generated on:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}

## Executive Summary

This report provides an analysis of "{topic}". Due to technical limitations, this is a simplified version of the report. For a comprehensive analysis, please ensure all dependencies are properly configured.

## Introduction

The topic "{topic}" represents an important area that requires careful analysis and consideration. This report aims to provide insights and recommendations based on available information.

## Key Areas of Focus

### 1. Current State
- Assessment of the current situation
- Identification of key stakeholders
- Analysis of existing challenges

### 2. Opportunities and Challenges
- Potential opportunities for improvement
- Key challenges that need to be addressed
- Risk factors to consider

### 3. Recommendations
- Short-term actionable steps
- Long-term strategic recommendations
- Implementation considerations

## Conclusion

The analysis of "{topic}" reveals several important considerations that should be addressed through strategic planning and implementation of recommended solutions.

## Next Steps

1. Further research and analysis
2. Stakeholder engagement
3. Development of implementation plan
4. Monitoring and evaluation

---

*Note: This is a simplified report. For a comprehensive analysis with detailed research and insights, please ensure OpenAI API key is properly configured.*
        """

def run_report_creation():
    creator = ReportCreator()
    
    config = {
        'topic': 'How to improve infrastructure in Bangalore?',
        'report_type': 'Comprehensive Analysis',
        'length': 5,
        'include_charts': True,
        'include_sources': True
    }
    
    report = creator.create_report(config)
    print(report)

if __name__ == "__main__":
    run_report_creation()