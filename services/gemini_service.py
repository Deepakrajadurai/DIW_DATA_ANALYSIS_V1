import google.generativeai as genai
import os
import json
from typing import List, Optional
from models import ReportData, StoryboardData, ChartConfig
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("Gemini API key not found. AI features will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.AI_MODEL)
            self.enabled = True
            logger.info(f"Gemini AI service initialized with model: {settings.AI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            self.enabled = False
    
    async def generate_narrative(self, data: ReportData) -> str:
        """Generate a narrative analysis for a report."""
        if not self.enabled:
            return "AI features are disabled. Please configure the Gemini API key."
        
        prompt = f"""
            You are a world-class economic data analyst from the German Institute for Economic Research (DIW Berlin).
            Based on the following data from a DIW Weekly Report on "{data.title}", write a compelling narrative summary.

            Your analysis should:
            1. Start with a concise, high-level summary of the main issue.
            2. Explain the key trends shown in the provided data and charts.
            3. **Crucially, identify and elaborate on the interconnections.** Discuss how the findings in this report might influence or be influenced by other economic sectors or social issues in Germany.
            4. Conclude with a forward-looking statement or a key takeaway.
            5. Format your entire response in GitHub-flavored Markdown for web display.

            Here is the data for your analysis:
            - **Report Title:** {data.title}
            - **High-Level Summary:** {data.summary}
            - **Key Findings:**
            {chr(10).join(f"  - {f}" for f in data.keyFindings)}
            - **Chart Data:** {json.dumps([chart.dict() for chart in data.charts], indent=2)}
            - **Original Report Excerpt:** 
            ---
            {data.fullText[:4000]}...
            ---
            """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return "An error occurred while generating the analysis. Please check the console for details."
    
    async def generate_storyboard(self, reports: List[ReportData]) -> Optional[StoryboardData]:
        """Generate a storyboard synthesis from multiple reports."""
        if not self.enabled:
            return None
        
        def serialize_report(report):
            try:
                return report.dict()
            except Exception as e:
                logger.warning(f"Failed to serialize report: {e}")
                return str(report)

        reports_data = json.dumps([serialize_report(report) for report in reports], indent=2, default=str)
        
        # Improved prompt with explicit JSON formatting instructions
        prompt = f"""
    You are a chief economist creating a synthesis from economic reports.

    Return ONLY a valid JSON object with this exact structure (no code fences, no extra text):

    {{"narrative": "Your narrative here (use \\n for line breaks, escape quotes as \\\")", "charts": [...]}}

    Instructions:
    1. Write a compelling economic narrative about Germany
    2. Create 1-3 synthesized charts from the data
    3. CRITICAL: Properly escape all JSON strings (\\n for newlines, \\" for quotes)

    Data: {reports_data[:50000]}...

    Respond with ONLY the JSON object:"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=0.8
                )
            )
            
            if not response or not response.text:
                logger.error("Empty response from AI")
                return None
            
            # Robust JSON extraction and parsing
            parsed_data = self._extract_and_parse_json(response.text)
            if not parsed_data:
                return None
                
            # Build result
            charts = []
            for chart_data in parsed_data.get("charts", []):
                try:
                    charts.append(ChartConfig(**chart_data))
                except Exception as e:
                    logger.warning(f"Invalid chart data: {e}")
            
            return StoryboardData(
                narrative=parsed_data.get("narrative", ""),
                charts=charts
            )
            
        except Exception as e:
            logger.error(f"Error generating storyboard: {e}")
            return None

    def _extract_and_parse_json(self, text: str) -> dict:
        """Robust JSON extraction and parsing."""
        try:
            # Remove markdown fences and extra whitespace
            clean_text = text.strip()
            if clean_text.startswith('```'):
                lines = clean_text.split('\n')
                clean_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
            
            # Find JSON object boundaries
            start = clean_text.find('{')
            if start == -1:
                raise ValueError("No JSON object found")
            
            # Find matching closing brace
            brace_count = 0
            end = len(clean_text)
            for i in range(start, len(clean_text)):
                if clean_text[i] == '{':
                    brace_count += 1
                elif clean_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            json_str = clean_text[start:end]
            
            # Try parsing - if it fails, attempt to fix common issues
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed: {e}")
                # Fix common issues: unescaped newlines and quotes in narrative
                fixed_json = self._fix_json_narrative(json_str)
                return json.loads(fixed_json)
                
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            return None

    def _fix_json_narrative(self, json_str: str) -> str:
        """Fix unescaped characters in the narrative field."""
        import re
        
        # Find the narrative value (between "narrative": " and ", "charts")
        pattern = r'"narrative":\s*"(.*?)"(?=\s*,\s*"charts")'
        match = re.search(pattern, json_str, re.DOTALL)
        
        if match:
            narrative_content = match.group(1)
            # Fix unescaped characters
            fixed_narrative = (narrative_content
                            .replace('\\', '\\\\')  # Escape backslashes first
                            .replace('\n', '\\n')   # Escape newlines
                            .replace('\r', '\\r')   # Escape carriage returns
                            .replace('\t', '\\t')   # Escape tabs
                            .replace('"', '\\"'))   # Escape quotes
            
            # Replace in original string
            json_str = json_str.replace(match.group(0), f'"narrative": "{fixed_narrative}"')
        
        return json_str
    async def create_report_from_text(self, full_text: str) -> Optional[ReportData]:
        """Create a structured report from raw text."""
        if not self.enabled:
            return None
        
        prompt = f"""
            You are an expert data analyst AI. Your task is to read the following text from an economic report and convert it into a structured JSON object.

            Your output MUST be a JSON object that follows this structure:
            {{
            "id": "url-friendly-slug",
            "title": "Report Title",
            "summary": "2-3 sentence summary",
            "keyFindings": ["Finding 1", "Finding 2", "Finding 3"],
            "charts": [
                {{
                "type": "bar|line|pie",
                "data": [{{ "name": "Category", "value": 123 }}],
                "dataKeys": [{{ "key": "value", "color": "#8884d8" }}],
                "title": "Chart Title",
                "description": "Chart description",
                "xAxisKey": "name"
                }}
            ]
            }}

            **Instructions:**
            1. Read the entire provided text carefully.
            2. Generate a title that accurately reflects the report's main subject.
            3. From the title, create a URL-friendly id (e.g., "Women in Leadership" becomes "women-in-leadership").
            4. Write a concise summary.
            5. Extract the most important points as key findings.
            6. For charts, scan for quantifiable data that can be visualized. If no suitable data exists, return an empty array [].
            7. Your entire response MUST be ONLY the JSON object.

            Here is the report text:
            ---
            {full_text[:8000]}...
            ---
            """
                    
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=0.5
                )
            )
            
            json_str = response.text.strip()
            parsed_data = json.loads(json_str)
            
            # Convert charts to ChartConfig objects
            charts = []
            for chart_data in parsed_data.get("charts", []):
                try:
                    chart = ChartConfig(**chart_data)
                    charts.append(chart)
                except Exception as e:
                    logger.warning(f"Invalid chart data in uploaded report: {e}")
            
            return ReportData(
                id=parsed_data["id"],
                title=parsed_data["title"],
                summary=parsed_data["summary"],
                keyFindings=parsed_data["keyFindings"],
                charts=charts,
                fullText=full_text
            )
        except Exception as e:
            logger.error(f"Error creating report from text: {e}")
            return None
    
    async def chat_with_report(self, report: ReportData, message: str) -> str:
        """Chat with AI about a specific report."""
        if not self.enabled:
            return "AI features are disabled. Please configure the Gemini API key."
        
        system_instruction = f"""You are an expert AI assistant from DIW Berlin, specializing in German economic data. Your knowledge base for this conversation is the DIW Weekly Report on "{report.title}". 

                Your tasks are:
                1. Answer the user's questions concisely about the provided report.
                2. If asked, summarize the key findings or explain the charts.
                3. When relevant, briefly mention potential interconnections with other economic areas.
                4. Keep your answers focused on the provided report context.

                Report context:
                - **Title:** {report.title}
                - **Summary:** {report.summary}
                - **Key Findings:** {', '.join(report.keyFindings)}
                - **Full Text:** {report.fullText[:6000]}...
                """
                        
        chat_prompt = f"""
                {system_instruction}

                User question: {message}

                Please provide a helpful and concise response based on the report data provided above.
                """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                chat_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1024,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "Sorry, I encountered an error. Please try again."