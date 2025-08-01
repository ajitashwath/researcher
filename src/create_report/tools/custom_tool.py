from crewai.tools import BaseTool
from typing import Type, Optional, Any, List
from pydantic import BaseModel, Field
import requests
import json
import pandas as pd
from datetime import datetime
import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class OpenAIWebSearchInput(BaseModel):
    query: str = Field(..., description="The search query to research")
    depth: str = Field("comprehensive", description="Depth of search: 'basic', 'comprehensive', or 'detailed'")

class OpenAIWebSearchTool(BaseTool):
    name: str = "openai_web_search"
    description: str = "Search and research information using OpenAI's knowledge base"
    args_schema: Type[BaseModel] = OpenAIWebSearchInput
    
    def __init__(self, api_key=None):
        super().__init__()
        if not api_key:
            raise ValueError("OpenAI API key must be provided")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Use GPT-4o-mini instead of GPT-3.5-turbo
    
    def _run(self, query: str, depth: str = "comprehensive") -> str:
        try:
            system_prompt = {
                "basic": "Provide a concise answer with key facts about the query.",
                "comprehensive": "Provide detailed information including background, current state, key facts, and relevant examples.",
                "detailed": "Provide an in-depth analysis including historical context, current trends, statistical data, expert opinions, and future implications."
            }
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt.get(depth, system_prompt["comprehensive"])},
                    {"role": "user", "content": f"Research and provide information about: {query}"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                return content
            else:
                return f"Error searching for information about {query}: No content returned."
            
        except Exception as e:
            logger.error(f"Error in OpenAI web search for {query}: {str(e)}")
            return f"Error searching for information about {query}: {str(e)}"

class OpenAIDataAnalysisInput(BaseModel):
    data: str = Field(..., description="Data to analyze (JSON format or CSV-like string)")
    analysis_type: str = Field("summary", description="Type of analysis: 'summary', 'trends', 'insights', 'recommendations'")
    context: str = Field("", description="Additional context for analysis")

class OpenAIDataAnalysisTool(BaseTool):
    name: str = "openai_data_analysis"
    description: str = "Analyze data and provide insights using OpenAI's analytical capabilities"
    args_schema: Type[BaseModel] = OpenAIDataAnalysisInput
    
    def __init__(self, api_key=None):
        super().__init__()
        if not api_key:
            raise ValueError("OpenAI API key must be provided")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Use GPT-4o-mini instead of GPT-3.5-turbo
    
    def _run(self, data: str, analysis_type: str = "summary", context: str = "") -> str:
        try:
            system_prompts = {
                "summary": "Analyze the provided data and give a comprehensive summary highlighting key statistics and patterns.",
                "trends": "Identify and explain trends, patterns, and correlations in the provided data.",
                "insights": "Extract meaningful insights and implications from the data that could inform decision-making.",
                "recommendations": "Based on the data analysis, provide actionable recommendations and strategic suggestions."
            }
            
            user_prompt = f"Analyze this data: {data}"
            if context:
                user_prompt += f"\nContext: {context}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompts.get(analysis_type, system_prompts["summary"])},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            if content:
                return content
            else:
                return f"Error analyzing data: No content returned."
            
        except Exception as e:
            logger.error(f"Error in OpenAI data analysis: {str(e)}")
            return f"Error analyzing data: {str(e)}"

class OpenAIContentGeneratorInput(BaseModel):
    topic: str = Field(..., description="Topic for content generation")
    content_type: str = Field("report", description="Type of content: 'report', 'summary', 'analysis', 'proposal'")
    length: str = Field("medium", description="Length: 'short', 'medium', 'long'")
    style: str = Field("professional", description="Writing style: 'professional', 'academic', 'casual'")

class OpenAIContentGeneratorTool(BaseTool):
    name: str = "openai_content_generator"
    description: str = "Generate structured content like reports, summaries, and analyses using OpenAI"
    args_schema: Type[BaseModel] = OpenAIContentGeneratorInput
    
    def __init__(self, api_key=None):
        super().__init__()
        if not api_key:
            raise ValueError("OpenAI API key must be provided")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Use GPT-4o-mini instead of GPT-3.5-turbo
    
    def _run(self, topic: str, content_type: str = "report", length: str = "medium", style: str = "professional") -> str:
        try:
            token_limits = {
                "short": 800,
                "medium": 1500,
                "long": 2000
            }
            system_prompt = f"""You are a {style} writer specializing in creating {content_type}s. 
            Generate well-structured, informative content that is {length} in length and follows {style} writing conventions."""
            
            user_prompt = f"Create a {length} {content_type} about: {topic}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=token_limits.get(length, 1500),
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                return content
            else:
                return f"Error generating content about {topic}: No content returned."
            
        except Exception as e:
            logger.error(f"Error in OpenAI content generation: {str(e)}")
            return f"Error generating content about {topic}: {str(e)}"

class OpenAIResearchInput(BaseModel):
    query: str = Field(..., description="Research query or topic")
    focus_areas: List[str] = Field([], description="Specific areas to focus on")
    research_depth: str = Field("standard", description="Research depth: 'basic', 'standard', 'comprehensive'")

class OpenAIResearchTool(BaseTool):
    name: str = "openai_research_tool"
    description: str = "Conduct comprehensive research on topics using OpenAI's knowledge base"
    args_schema: Type[BaseModel] = OpenAIResearchInput
    
    def __init__(self, api_key=None):
        super().__init__()
        if not api_key:
            raise ValueError("OpenAI API key must be provided")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Use GPT-4o-mini instead of GPT-3.5-turbo
    
    def _run(self, query: str, focus_areas: List[str] = [], research_depth: str = "standard") -> str:
        try:
            system_prompts = {
                "basic": "Provide basic information and key facts about the topic.",
                "standard": "Provide comprehensive research including background, current state, key findings, and implications.",
                "comprehensive": "Provide in-depth research with historical context, current trends, statistical analysis, expert perspectives, and future outlook."
            }
            
            user_prompt = f"Research the following topic: {query}"
            
            if focus_areas:
                user_prompt += f"\n\nPlease focus specifically on these areas: {', '.join(focus_areas)}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompts.get(research_depth, system_prompts["standard"])},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            if content:
                return content
            else:
                return f"Error researching {query}: No content returned."
            
        except Exception as e:
            logger.error(f"Error in OpenAI research: {str(e)}")
            return f"Error conducting research on '{query}': {str(e)}"

def get_all_tools(api_key=None) -> List[BaseTool]:
    if not api_key:
        return []
    try:
        return [
            OpenAIWebSearchTool(api_key=api_key),
            OpenAIDataAnalysisTool(api_key=api_key),
            OpenAIContentGeneratorTool(api_key=api_key),
            OpenAIResearchTool(api_key=api_key)
        ]
    except Exception as e:
        logger.error(f"Error initializing tools: {str(e)}")
        return []