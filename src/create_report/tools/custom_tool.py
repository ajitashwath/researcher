from crewai.tools import BaseTool
from typing import Type, Optional, Any
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
                return self._analyze_text_data(data, analysis