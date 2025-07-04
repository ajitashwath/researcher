from crewai.tools import BaseTool
from typing import Type, Optional, Any, List
from pydantic import BaseModel, Field
import requests
import json
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebScraperInput(BaseModel):
    """Input schema for WebScraper tool"""
    url: str = Field(..., description="The URL to scrape content from")
    max_content_length: int = Field(5000, description="Maximum content length to return")

class WebScraperTool(BaseTool):
    """Custom tool for scraping web content"""
    
    name: str = "web_scraper"
    description: str = "Scrape content from web pages to gather information for research"
    args_schema: Type[BaseModel] = WebScraperInput
    
    def _run(self, url: str, max_content_length: int = 5000) -> str:
        """
        Scrape content from a given URL
        
        Args:
            url: The URL to scrape
            max_content_length: Maximum length of content to return
            
        Returns:
            str: Scraped content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            # Simple content extraction (in production, you'd use BeautifulSoup)
            # Remove HTML tags and clean up content
            import re
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            # Limit content length
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            return content
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return f"Error scraping content from {url}: {str(e)}"

class DataAnalysisInput(BaseModel):
    """Input schema for DataAnalysis tool"""
    data: str = Field(..., description="Data to analyze (JSON format or CSV-like string)")
    analysis_type: str = Field("summary", description="Type of analysis to perform")

class DataAnalysisTool(BaseTool):
    """Custom tool for data analysis"""
    
    name: str = "data_analysis_tool"
    description: str = "Analyze data and provide insights, trends, and statistical summaries"
    args_schema: Type[BaseModel] = DataAnalysisInput
    
    def _run(self, data: str, analysis_type: str = "summary") -> str:
        """
        Analyze data and provide insights
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            str: Analysis results
        """
        try:
            # Try to parse as JSON first
            try:
                data_obj = json.loads(data)
                return self._analyze_json_data(data_obj, analysis_type)
            except json.JSONDecodeError:
                # Try to parse as CSV-like data
                return self._analyze_text_data(data, analysis_type)
                
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            return f"Error analyzing data: {str(e)}"
    
    def _analyze_json_data(self, data_obj: Any, analysis_type: str) -> str:
        """Analyze JSON data"""
        try:
            if isinstance(data_obj, dict):
                keys = list(data_obj.keys())
                return f"Data analysis summary:\n- Keys: {keys}\n- Total fields: {len(keys)}\n- Data type: Dictionary"
            elif isinstance(data_obj, list):
                return f"Data analysis summary:\n- Items: {len(data_obj)}\n- Data type: List\n- First item type: {type(data_obj[0]) if data_obj else 'N/A'}"
            else:
                return f"Data analysis summary:\n- Data type: {type(data_obj)}\n- Value: {str(data_obj)[:100]}..."
        except Exception as e:
            return f"Error analyzing JSON data: {str(e)}"
    
    def _analyze_text_data(self, data: str, analysis_type: str) -> str:
        """Analyze text data"""
        try:
            lines = data.strip().split('\n')
            words = data.split()
            
            return f"""Text data analysis summary:
- Total lines: {len(lines)}
- Total words: {len(words)}
- Character count: {len(data)}
- Analysis type: {analysis_type}
- Sample text: {data[:200]}...
"""
        except Exception as e:
            return f"Error analyzing text data: {str(e)}"

class ResearchInput(BaseModel):
    """Input schema for Research tool"""
    query: str = Field(..., description="Research query or topic")
    max_results: int = Field(10, description="Maximum number of results to return")

class ResearchTool(BaseTool):
    """Custom tool for research tasks"""
    
    name: str = "research_tool"
    description: str = "Conduct research on topics and provide structured information"
    args_schema: Type[BaseModel] = ResearchInput
    
    def _run(self, query: str, max_results: int = 10) -> str:
        """
        Conduct research on a topic
        
        Args:
            query: Research query
            max_results: Maximum number of results
            
        Returns:
            str: Research results
        """
        try:
            # This is a placeholder implementation
            # In a real application, you would integrate with search APIs, databases, etc.
            
            research_results = f"""
Research Results for: "{query}"

Key Findings:
1. Current state analysis of {query}
2. Recent developments and trends
3. Best practices and solutions
4. Statistical data and insights
5. Expert opinions and case studies

Recommendations:
- Further investigation needed in specific areas
- Consider multiple perspectives on the topic
- Evaluate recent developments and their impact
- Analyze quantitative data where available

Sources:
- Academic papers and journals
- Industry reports and whitepapers
- Government publications
- Expert interviews and surveys

Note: This is a simulated research result. In production, this would connect to real data sources.
"""
            
            return research_results
            
        except Exception as e:
            logger.error(f"Error conducting research: {str(e)}")
            return f"Error conducting research on '{query}': {str(e)}"

def get_all_tools() -> List[BaseTool]:
    """
    Get all available custom tools
    
    Returns:
        List[BaseTool]: List of all custom tools
    """
    return [
        WebScraperTool(),
        DataAnalysisTool(),
        ResearchTool()
    ]

'''
if __name__ == "__main__":
    tools = get_all_tools()
    
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
'''