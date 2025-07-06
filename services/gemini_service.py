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
        """Generate a storyboard from all reports using a detailed, structured prompt."""
        if not self.enabled:
            return None

        # Prepare the source data for the prompt
        source_data = [report.dict() for report in reports]
        
        prompt = '''
You are a world-class macroeconomic strategist. Your mission is to analyze a collection of disparate economic reports and uncover the **"narrative singularity"**—the single, powerful, underlying story that connects them all. You must distill complexity into a clear, compelling, and unified thesis, visualize it, and reflect on your own analytical process.

Your response MUST be a single JSON object that conforms to this TypeScript interface:
interface ChartDataPoint { name: string; [key: string]: string | number; }
interface ChartConfig { type: 'bar' | 'line' | 'pie'; data: ChartDataPoint[]; dataKeys: { key: string; color: string; stackId?: string; name?: string }[]; title: string; description: string; xAxisKey: string; }
interface GraphNode { id: string; title: string; }
interface GraphEdge { source: string; target: string; label: string; }
interface RelationshipGraphData { nodes: GraphNode[]; edges: GraphEdge[]; }
interface KeyActor { name: string; description: string; icon: string; /* A full Font Awesome 6 class string, e.g., "fa-solid fa-users" or "fa-solid fa-industry" */ }
interface StoryboardData {
  title: string; // A compelling, overarching title for the entire storyboard analysis.
  narrative: string;
  charts: ChartConfig[];
  introspection: string;
  retrospection: string;
  relationshipGraph: RelationshipGraphData;
  keyActors: KeyActor[];
}

---
**DETAILED INSTRUCTIONS**
---

**1. For the `title`:**
*   Create a short, punchy, and insightful title for the entire synthesized report. This should encapsulate your singularity thesis.

**2. For the `narrative` - The Singularity Thesis:**
*   **Identify and State the Singularity:** Begin by explicitly stating the central theme or "singularity." This is your core thesis. Frame it as a powerful, insightful statement (e.g., "Germany's current economic friction stems not from isolated issues, but from a pervasive 'crisis of structural adaptation'").
*   **Build the Case:** Demonstrate how each individual report serves as a pillar supporting your central thesis.
*   **Synthesize the Implications:** Explain the compounded effect. What is the larger, emergent threat or opportunity?
*   **Conclude with a Call to Action:** End with a concise, forward-looking statement focused on addressing the root cause.

**3. For the `charts` - Visualizing the Singularity:**
*   **Create a Thesis Visualization:** Your charts (1-2) **must** visually represent the narrative singularity. **Do not simply copy or re-aggregate data from the source charts.**
*   **Be Creative:** Invent a new, meaningful visualization. For example, a "Structural Drag Index" chart quantifying each report's contribution to the problem.
*   If you cannot create a meaningful visualization, return an empty array `[]`.

**4. For the `relationshipGraph` - Mapping the Connections:**
*   **Goal:** Create a node-edge graph that visually maps the most critical inter-report relationships supporting your singularity thesis. This provides a visual 'mind map' of your core argument.
*   **Nodes:** Populate the `nodes` array. Each node represents one of the source reports. Use the report's `id` and `title`.
*   **Edges:** Populate the `edges` array with 2-4 of the most critical connections. An edge connects two reports (source -> target). The `label` on the edge MUST be a concise explanation of the causal link (e.g., 'Reduced construction activity lowers tax revenue, worsening debt outlook').

**5. For the `introspection` - The 'Why':**
*   **Explain Your Reasoning:** In Markdown, reveal the logical path that led to your thesis.
*   **Pivotal Evidence**: Pinpoint the specific data points from each report that were most influential.
*   **Connecting the Dots**: Detail the non-obvious connections you discovered, which should align with your `relationshipGraph`.

**6. For the `retrospection` - The 'What If':**
*   **Critique Your Own Analysis:** In Markdown, show intellectual humility.
*   **Alternative Theses**: Briefly mention one plausible alternative 'singularity' you considered and why you discarded it.
*   **Information Gaps**: If you could request one new piece of data to strengthen your analysis, what would it be?

**7. For the `keyActors` - The Main Characters:**
*   Identify 4-6 key actors or stakeholders central to your narrative (e.g., "German Consumers," "Policymakers," "Export-Oriented Industries," "Low-Income Households").
*   For each actor, provide a short `description` of their role, challenges, or position within the story.
*   Assign a relevant Font Awesome 6 icon class string to each actor for visual representation (e.g., "fa-solid fa-users" for consumers, "fa-solid fa-landmark" for policymakers).

---
**SOURCE DATA**
---
{source_data}
'''
        
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
                return None
            response_text = response.text
        except Exception as e:
            logger.error(f"Error generating storyboard: {e}")
            return None
        
        # Try to parse the response as JSON
        try:
            parsed = self._extract_and_parse_json(response_text)
            if not parsed:
                return None
            # Fallbacks for missing fields
            if not parsed.get('introspection'):
                parsed['introspection'] = 'No introspection provided by AI.'
            if not parsed.get('retrospection'):
                parsed['retrospection'] = 'No retrospection provided by AI.'
            if not parsed.get('keyActors') or not isinstance(parsed['keyActors'], list) or len(parsed['keyActors']) == 0:
                # Optionally, you could pull from a main Key Actors section if available
                parsed['keyActors'] = [
                    {
                        "name": "Policymakers (Federal/State/Municipal)",
                        "description": "Responsible for creating incentives, regulations, and investment frameworks to guide structural transformations and address social inequalities.",
                        "icon": "fa-solid fa-landmark"
                    },
                    {
                        "name": "German Households",
                        "description": "Experience the direct effects of economic stagnation, climate costs (heating, transport), and social policies (care burden, health access).",
                        "icon": "fa-solid fa-users"
                    },
                    {
                        "name": "German Industry",
                        "description": "Faces challenges adapting to higher energy costs, international competition, and the need to decarbonize while maintaining competitiveness.",
                        "icon": "fa-solid fa-industry"
                    },
                    {
                        "name": "Energy Sector",
                        "description": "Navigating the shift from fossil fuels to renewables, requiring massive investment in generation, grids, and network decommissioning.",
                        "icon": "fa-solid fa-bolt"
                    },
                    {
                        "name": "Property Owners / Landlords",
                        "description": "Key decision-makers for building renovations and investments in heating systems, influenced by financing, standards, and tenancy laws.",
                        "icon": "fa-solid fa-building"
                    },
                    {
                        "name": "European Central Bank (ECB)",
                        "description": "Sets monetary policy influencing financing conditions, inflation, and overall economic stability in the Euro Area, including Germany.",
                        "icon": "fa-solid fa-euro-sign"
                    }
                ]
            return StoryboardData(**parsed)
        except Exception as e:
            logger.error(f"Failed to parse storyboard JSON: {e}\nResponse: {response_text}")
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

    def _create_fallback_report(self, full_text: str, ai_response: str) -> dict:
        """Create a basic report structure when AI JSON parsing fails."""
        import re
        from datetime import datetime
        
        logger.info("Creating fallback report structure")
        
        # Extract title from the first few lines of text
        lines = full_text.split('\n')
        title = "Economic Report"
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 200 and not line.isdigit():
                # Look for potential titles (capitalized, reasonable length)
                if line[0].isupper() and not line.startswith('Page') and not line.startswith('www'):
                    title = line
                    break
        
        # Create URL-friendly ID
        id_base = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        id_base = re.sub(r'\s+', '-', id_base.strip())
        if not id_base:
            id_base = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create summary from first paragraph
        paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
        summary = paragraphs[0][:300] + "..." if paragraphs and len(paragraphs[0]) > 300 else "Report analysis and findings."
        
        # Extract key findings (look for bullet points, numbers, etc.)
        key_findings = []
        for line in lines:
            line = line.strip()
            if (line.startswith('•') or line.startswith('-') or 
                re.match(r'^\d+\.', line) or 
                (len(line) > 20 and len(line) < 200 and line[0].isupper())):
                # Clean up the finding
                finding = re.sub(r'^[•\-\d\.\s]+', '', line)
                if finding and len(finding) > 10:
                    key_findings.append(finding)
                    if len(key_findings) >= 5:  # Limit to 5 findings
                        break
        
        # If no findings extracted, create generic ones
        if not key_findings:
            key_findings = [
                "Analysis of economic trends and indicators",
                "Key policy implications and recommendations",
                "Statistical data and quantitative findings",
                "Comparative analysis with previous periods",
                "Future outlook and projections"
            ]
        
        return {
            "id": id_base,
            "title": title,
            "summary": summary,
            "keyFindings": key_findings,
            "charts": []  # No charts in fallback
        }
    async def create_report_from_text(self, full_text: str) -> Optional[ReportData]:
        """Create a structured report from raw text."""
        if not self.enabled:
            logger.warning("AI service is disabled")
            return None
        
        # Validate input text
        if not full_text or not full_text.strip():
            logger.error("Empty or invalid text provided")
            return None
        
        logger.info(f"Processing text of length: {len(full_text)} characters")
        
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
            logger.info("Sending request to AI model")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=0.5
                )
            )
            
            if not response or not response.text:
                logger.error("Empty response from AI model")
                return None
            
            json_str = response.text.strip()
            logger.info(f"AI response length: {len(json_str)} characters")
            
            # Try to parse JSON with better error handling
            try:
                parsed_data = json.loads(json_str)
                logger.info("JSON parsing successful with direct json.loads")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.error(f"Response text: {json_str[:500]}...")
                # Try to extract JSON from the response
                logger.info("Attempting to extract JSON from response using _extract_and_parse_json")
                parsed_data = self._extract_and_parse_json(json_str)
                if not parsed_data:
                    # Fallback: try to create a basic report from the text
                    logger.warning("Attempting fallback report creation")
                    parsed_data = self._create_fallback_report(full_text, json_str)
                    if not parsed_data:
                        logger.error("Fallback report creation also failed")
                        return None
                else:
                    logger.info("JSON extraction successful using _extract_and_parse_json")
            
            # Validate required fields
            required_fields = ["id", "title", "summary", "keyFindings"]
            missing_fields = []
            for field in required_fields:
                if field not in parsed_data:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                logger.error(f"Available fields: {list(parsed_data.keys())}")
                return None
            
            logger.info("All required fields present in parsed data")
            
            # Convert charts to ChartConfig objects
            charts = []
            chart_data = parsed_data.get("charts", [])
            logger.info(f"Processing {len(chart_data)} charts")
            
            for i, chart_data_item in enumerate(chart_data):
                try:
                    chart = ChartConfig(**chart_data_item)
                    charts.append(chart)
                    logger.info(f"Successfully processed chart {i+1}")
                except Exception as e:
                    logger.warning(f"Invalid chart data in uploaded report (chart {i+1}): {e}")
                    logger.warning(f"Chart data: {chart_data_item}")
            
            logger.info(f"Successfully created report with {len(charts)} charts")
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
            logger.error(f"Full text preview: {full_text[:200]}...")
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