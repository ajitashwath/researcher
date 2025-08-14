import logging
from typing import Dict, Any
from openai import OpenAI
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportCreator:
    def __init__(self, api_key=None):
        if not api_key:
            raise ValueError("OpenAI API key must be provided by the user.")
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        # Use GPT-4o-mini which is available to all users
        self.model = "gpt-4o-mini"
    
    def create_report(self, config: Dict[str, Any]) -> str:
        """Main method to create a comprehensive report"""
        try:
            logger.info(f"Starting report creation for topic: {config['topic']}")
            
            # Step 1: Research phase
            research_data = self._conduct_research(config['topic'])
            
            # Step 2: Analysis phase
            analysis_data = self._analyze_data(research_data, config['topic'])
            
            # Step 3: Report generation phase
            report_content = self._generate_report(config, research_data, analysis_data)
            
            # Step 4: Review and polish
            final_report = self._review_report(report_content, config)
            
            logger.info("Report creation completed successfully")
            return final_report
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return self._create_fallback_report(config)
    
    def _conduct_research(self, topic: str) -> str:
        """Conduct comprehensive research on the topic"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a senior research analyst with expertise in gathering comprehensive information. 
                        Your research should include:
                        - Current state and background information
                        - Key challenges and opportunities
                        - Statistical data and trends
                        - Best practices and solutions
                        - Expert opinions and case studies
                        - Recent developments and innovations
                        Provide detailed, well-structured research findings."""
                    },
                    {
                        "role": "user", 
                        "content": f"Conduct comprehensive research on: {topic}"
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or f"Research data for: {topic}"
            
        except Exception as e:
            logger.error(f"Research phase error: {str(e)}")
            return f"Research phase encountered an error for topic: {topic}"
    
    def _analyze_data(self, research_data: str, topic: str) -> str:
        """Analyze the research data and extract insights"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a data analyst specializing in extracting insights from research data. 
                        Your analysis should include:
                        - Key patterns and trends identification
                        - Critical insights and implications
                        - Comparative analysis of different approaches
                        - Risk assessment and opportunities
                        - Data-driven recommendations
                        Provide actionable insights that will strengthen the report."""
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this research data about {topic}:\n\n{research_data}"
                    }
                ],
                max_tokens=1500,
                temperature=0.6
            )
            
            return response.choices[0].message.content or f"Analysis data for: {topic}"
            
        except Exception as e:
            logger.error(f"Analysis phase error: {str(e)}")
            return f"Analysis phase encountered an error for topic: {topic}"
    
    def _generate_report(self, config: Dict[str, Any], research_data: str, analysis_data: str) -> str:
        """Generate the structured report based on research and analysis"""
        try:
            topic = config['topic']
            report_type = config['report_type']
            length = config['length']
            include_charts = config.get('include_charts', False)
            include_sources = config.get('include_sources', False)
            
            # Create dynamic instructions based on config
            charts_instruction = "Include suggestions for data visualizations and charts where appropriate." if include_charts else ""
            sources_instruction = "Include proper citations and references throughout the report." if include_sources else ""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are a professional report writer creating a {report_type} report 
                        of approximately {length} pages. Create a comprehensive, well-structured report with:
                        
                        1. Executive Summary
                        2. Introduction and Background
                        3. Current State Analysis
                        4. Key Challenges and Pain Points
                        5. Opportunities and Solutions
                        6. Detailed Recommendations
                        7. Implementation Strategy
                        8. Risk Assessment
                        9. Expected Outcomes
                        10. Conclusion and Next Steps
                        
                        {charts_instruction}
                        {sources_instruction}
                        
                        Use professional formatting, clear headings, and actionable content."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Create a comprehensive {report_type} report on: {topic}
                        
                        Research Findings:
                        {research_data}
                        
                        Analysis Results:
                        {analysis_data}
                        
                        Please create a {length}-page professional report with clear structure and actionable recommendations."""
                    }
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or self._create_fallback_report(config)
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return self._create_fallback_report(config)
    
    def _review_report(self, report_content: str, config: Dict[str, Any]) -> str:
        """Review and polish the generated report"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a quality assurance specialist reviewing reports. 
                        Improve the report by:
                        - Ensuring accuracy and completeness
                        - Improving clarity and readability
                        - Checking logical flow and structure
                        - Verifying actionable recommendations
                        - Enhancing professional presentation
                        - Correcting any grammar or formatting issues
                        
                        Return the polished, final version of the report."""
                    },
                    {
                        "role": "user", 
                        "content": f"Review and improve this {config['report_type']} report:\n\n{report_content}"
                    }
                ],
                max_tokens=3500,
                temperature=0.5
            )
            
            return response.choices[0].message.content or report_content
            
        except Exception as e:
            logger.error(f"Review phase error: {str(e)}")
            return report_content  # Return original if review fails
    
    def _create_fallback_report(self, config: Dict[str, Any]) -> str:
        """Create a basic fallback report when API calls fail"""
        topic = config['topic']
        report_type = config['report_type']
        
        # Try simple OpenAI call as fallback
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Create a professional {report_type} report with clear structure and recommendations."
                    },
                    {
                        "role": "user", 
                        "content": f"Create a detailed report on: {topic}"
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                return content
        except Exception as e:
            logger.error(f"Fallback report failed: {str(e)}")
        
        # Final static fallback
        return f"""
# {report_type}: {topic}

**Generated on:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}

## Executive Summary

This report addresses "{topic}" and provides analysis and recommendations for moving forward. Due to technical limitations, this is a simplified version of the requested report.

## Introduction

The topic "{topic}" represents an important area requiring careful analysis and strategic planning. This report aims to provide insights and actionable recommendations.

## Current State Analysis

The current situation regarding "{topic}" presents both opportunities and challenges that need to be addressed through comprehensive planning and execution.

## Key Challenges

1. **Resource Allocation**: Ensuring adequate resources for implementation
2. **Stakeholder Engagement**: Securing buy-in from relevant stakeholders  
3. **Technical Implementation**: Addressing technical requirements and constraints
4. **Timeline Management**: Developing realistic implementation timelines

## Opportunities

1. **Strategic Advantage**: Potential competitive benefits through implementation
2. **Process Optimization**: Opportunities to improve current processes
3. **Innovation**: Implementing cutting-edge solutions and approaches
4. **Value Creation**: Generating value for stakeholders

## Recommendations

### Immediate Actions (0-3 months)
- Conduct detailed stakeholder analysis
- Develop comprehensive implementation roadmap
- Secure necessary resources and approvals
- Launch pilot program or proof of concept

### Medium-term Strategy (3-12 months)
- Execute implementation plan in phases
- Monitor progress and adjust approach
- Gather feedback and iterate
- Scale successful initiatives

### Long-term Vision (12+ months)
- Evaluate overall impact and success
- Develop sustainability framework
- Explore expansion opportunities
- Document lessons learned

## Implementation Strategy

**Phase 1: Planning and Preparation**
- Detailed planning and resource allocation
- Stakeholder engagement and communication
- Risk assessment and mitigation planning

**Phase 2: Pilot Implementation**
- Small-scale testing and validation
- Feedback collection and process refinement
- Technical and operational issue resolution

**Phase 3: Full-scale Deployment**
- Complete implementation rollout
- Performance monitoring and optimization
- Continuous improvement processes

## Risk Assessment

**Key Risks:**
- Resource constraints and budget limitations
- Technical implementation challenges
- Stakeholder resistance or lack of buy-in
- Timeline delays and scope creep

**Mitigation Strategies:**
- Comprehensive planning and contingency preparation
- Regular stakeholder communication and engagement
- Phased implementation approach
- Continuous monitoring and adjustment

## Expected Outcomes

Successful implementation should result in:
- Improved operational efficiency
- Enhanced stakeholder satisfaction
- Reduced risks and improved outcomes
- Sustainable long-term benefits

## Conclusion

The analysis of "{topic}" reveals significant opportunities for improvement and growth. With proper planning, resource allocation, and stakeholder engagement, the recommended strategies can be successfully implemented.

## Next Steps

1. Review and approve recommendations
2. Develop detailed implementation plan
3. Secure resources and stakeholder buy-in
4. Begin phased implementation
5. Monitor progress and adjust as needed

---

*This report was generated using AI technology. For additional details or clarifications, please contact the report administrator.*
        """

def run_report_creation():
    """CLI function for testing"""
    api_key = input("Enter your OpenAI API Key: ")
    if not api_key:
        print("API key is required!")
        return
    
    try:
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
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_report_creation()