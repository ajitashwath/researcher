__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

from crewai import Agent, Task, Crew
import logging
from typing import Dict, Any
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAITool:
    def __init__(self, api_key=None):
        if not api_key:
            raise ValueError("OpenAI API key must be provided by the user.")
        self.client = OpenAI(api_key=api_key)
    
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
            return response.choices[0].message.content or f"Research unavailable for: {query}"
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
            return response.choices[0].message.content or f"Analysis unavailable for: {topic}"
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            return f"Analysis unavailable for: {topic}"

class ReportCreator:
    def __init__(self, api_key=None):
        if not api_key:
            raise ValueError("OpenAI API key must be provided by the user.")
        self.api_key = api_key
        self.openai_tool = OpenAITool(api_key=api_key)
        self.setup_agents()
    
    def setup_agents(self):
        # Create agents with the OpenAI client for direct API calls
        self.researcher = Agent(
            role="Senior Research Analyst",
            goal="Conduct comprehensive research on the given topic and gather relevant, accurate information",
            backstory="""You are a senior research analyst with expertise in gathering and analyzing 
            information from various sources. You have a keen eye for detail and can distinguish 
            between credible and unreliable sources. You excel at finding the most current and 
            relevant information on any topic.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            llm=self._get_llm()
        )
        
        self.writer = Agent(
            role="Professional Content Writer",
            goal="Create well-structured, engaging, and comprehensive reports based on research findings",
            backstory="""You are a professional content writer with years of experience in creating 
            reports, articles, and documentation. You have the ability to transform complex research 
            findings into clear, engaging, and well-structured content that is easy to understand 
            for the target audience.""",
            verbose=True,
            allow_delegation=False,
            llm=self._get_llm()
        )
        
        self.reviewer = Agent(
            role="Quality Assurance Specialist",
            goal="Review and improve the quality, accuracy, and completeness of the generated report",
            backstory="""You are a quality assurance specialist with expertise in reviewing and 
            improving written content. You have a sharp eye for inconsistencies, gaps in information, 
            and areas that need improvement. You ensure that all reports meet the highest standards 
            of quality and accuracy.""",
            verbose=True,
            allow_delegation=False,
            llm=self._get_llm()
        )
        
        self.analyst = Agent(
            role="Data Analyst",
            goal="Analyze data, identify trends, and provide insights to support the report",
            backstory="""You are a data analyst with strong analytical skills and experience in 
            interpreting data to extract meaningful insights. You can identify patterns, trends, 
            and correlations that add value to reports and help in decision-making.""",
            verbose=True,
            allow_delegation=False,
            llm=self._get_llm()
        )
    
    def _get_llm(self):
        """Create OpenAI LLM instance with user's API key"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=self.api_key,
                temperature=0.7
            )
        except ImportError:
            # Fallback if langchain not available
            return None
    
    def create_report(self, config: Dict[str, Any]) -> str:
        try:
            logger.info(f"Starting report creation for topic: {config['topic']}")
            
            # Use OpenAI API directly for research and analysis
            research_data = self.openai_tool.research(config['topic'])
            analysis_data = self.openai_tool.analyze(research_data, config['topic'])
            
            # Create the final report using OpenAI API
            report_content = self._generate_final_report(config, research_data, analysis_data)
            
            logger.info("Report creation completed successfully")
            return report_content
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return self.create_fallback_report(config)
    
    def _generate_final_report(self, config: Dict[str, Any], research_data: str, analysis_data: str) -> str:
        """Generate the final report using OpenAI API directly"""
        try:
            topic = config['topic']
            report_type = config['report_type']
            length = config['length']
            
            system_prompt = f"""You are a professional report writer. Create a comprehensive {report_type} report 
            that is approximately {length} pages long. The report should be well-structured, professional, 
            and include actionable recommendations."""
            
            user_prompt = f"""
            Create a detailed {report_type} report on: {topic}
            
            Research Data:
            {research_data}
            
            Analysis Data:
            {analysis_data}
            
            The report should include:
            1. Executive Summary
            2. Introduction and Background
            3. Current State Analysis
            4. Key Challenges and Opportunities
            5. Proposed Solutions and Recommendations
            6. Implementation Strategies
            7. Expected Outcomes and Benefits
            8. Conclusion and Next Steps
            
            Make it professional, comprehensive, and actionable with approximately {length} pages of content.
            """
            
            response = self.openai_tool.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                return content
            else:
                return self.create_fallback_report(config)
                
        except Exception as e:
            logger.error(f"Error generating final report: {str(e)}")
            return self.create_fallback_report(config)
    
    def create_fallback_report(self, config: Dict[str, Any]) -> str:
        """Create a basic fallback report if OpenAI API fails"""
        topic = config['topic']
        report_type = config['report_type']
        
        # Try one more time with OpenAI API for fallback
        try:
            response = self.openai_tool.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a professional report writer. Create a {report_type} report."},
                    {"role": "user", "content": f"Create a detailed report on: {topic}"}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            content = response.choices[0].message.content
            if content:
                return content
        except Exception as e:
            logger.error(f"Fallback OpenAI report failed: {str(e)}")
        
        # Final fallback - static template
        from datetime import datetime
        return f"""
# {report_type}: {topic}

**Generated on:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}

## Executive Summary

This report provides an analysis of "{topic}". The analysis covers key areas, challenges, and recommendations for moving forward.

## Introduction

The topic "{topic}" represents an important area that requires careful analysis and strategic consideration. This report aims to provide insights and actionable recommendations.

## Current State Analysis

Based on available information, the current state of "{topic}" presents both opportunities and challenges that need to be addressed through strategic planning and implementation.

## Key Challenges

1. **Resource Allocation**: Ensuring adequate resources are available for implementation
2. **Stakeholder Engagement**: Getting buy-in from all relevant stakeholders
3. **Technical Considerations**: Addressing technical requirements and constraints
4. **Timeline Management**: Developing realistic timelines for implementation

## Opportunities

1. **Strategic Advantage**: Potential to gain competitive advantage through implementation
2. **Process Improvement**: Opportunity to streamline and optimize current processes
3. **Innovation**: Chance to implement innovative solutions and approaches
4. **Stakeholder Value**: Potential to create value for all stakeholders

## Recommendations

### Short-term Actions (0-3 months)
1. Conduct detailed stakeholder analysis
2. Develop comprehensive implementation plan
3. Secure necessary resources and approvals
4. Begin pilot program or proof of concept

### Medium-term Actions (3-12 months)
1. Execute implementation plan in phases
2. Monitor progress and adjust as needed
3. Gather feedback and iterate on approach
4. Scale successful initiatives

### Long-term Strategy (12+ months)
1. Evaluate overall success and impact
2. Develop sustainability plan
3. Consider expansion opportunities
4. Document lessons learned

## Implementation Strategy

The implementation of recommendations should follow a phased approach:

**Phase 1: Planning and Preparation**
- Detailed planning and resource allocation
- Stakeholder engagement and buy-in
- Risk assessment and mitigation planning

**Phase 2: Pilot Implementation**
- Small-scale implementation to test approach
- Gather feedback and refine processes
- Address any technical or operational issues

**Phase 3: Full Implementation**
- Roll out to full scale
- Monitor performance and outcomes
- Continuous improvement and optimization

## Expected Outcomes

The successful implementation of these recommendations is expected to result in:
- Improved efficiency and effectiveness
- Enhanced stakeholder satisfaction
- Reduced risks and improved outcomes
- Sustainable long-term benefits

## Risk Assessment

Key risks and mitigation strategies include:
- **Resource constraints**: Ensure adequate budget and staffing
- **Technical challenges**: Conduct thorough testing and have contingency plans
- **Stakeholder resistance**: Maintain open communication and address concerns
- **Timeline delays**: Build buffer time into schedules

## Conclusion

The analysis of "{topic}" reveals significant opportunities for improvement and growth. With proper planning, resource allocation, and stakeholder engagement, the recommended strategies can be successfully implemented to achieve desired outcomes.

## Next Steps

1. Review and approve recommendations
2. Develop detailed implementation plan
3. Secure necessary resources and approvals
4. Begin implementation process
5. Monitor progress and adjust as needed

---

*This report was generated using AI technology. For questions or clarifications, please contact the report administrator.*
        """

def run_report_creation():
    # Example usage for CLI/testing
    api_key = input("Enter your OpenAI API Key: ")
    creator = ReportCreator(api_key=api_key)
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