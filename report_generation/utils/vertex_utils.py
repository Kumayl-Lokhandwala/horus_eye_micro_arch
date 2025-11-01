import json
import vertexai
from vertexai.generative_models import GenerativeModel,GenerationConfig, Part

SECURITY_INSIGHTS_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {
            "type": "string",
            "description": "A high-level overview of the most critical risks and overall security posture, written in 2-3 paragraphs for a leadership or executive audience. Focus on business impact."
        },
        "correlated_findings": {
            "type": "array",
            "description": "A list of high-priority findings where data from *multiple* tools is correlated to show a clearer risk. (e.g., 'Amass found a subdomain, and Nmap confirmed it has a vulnerable service').",
            "items": {
                "type": "object",
                "properties": {
                   "correlated_finding": {
                      "type": "string",
                      "description": "A detailed description of the correlated finding."
                   },
                   "impact": {
                      "type": "string",
                      "description": "The specific business impact of this correlated finding."
                   },
                   "recommendation": {
                      "type": "string",
                      "description": "The detailed, actionable remediation step for this correlated issue."
                   }
                }
            }
        },
        "detailed_analysis": {
            "type": "array",
            "description": "A list of analysis objects, grouped by the security tool.",
            "items": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "The name of the security tool (e.g., 'nmap', 'amass', 'whatweb')."
                    },
                    "findings": {
                        "type": "array",
                        "description": "A list of all specific findings from this tool.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {
                                    "type": "string",
                                    "description": "The severity of the finding (e.g., 'Critical', 'High', 'Medium', 'Low', 'Informational')."
                                },
                                "description": {
                                    "type": "string",
                                    "description": "A detailed, multi-sentence description of the finding, explaining exactly what was discovered."
                                },
                                "evidence": {
                                    "type": "string",
                                    "description": "A direct quote or data point from the scan text that supports this finding. Be concise."
                                },
                                "recommendation": {
                                    "type": "string",
                                    "description": "A detailed, actionable, and specific multi-step recommendation for how to remediate this finding."
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "required": ["executive_summary", "correlated_findings", "detailed_analysis"]
}

def generate_security_report(project_id, location, compiled_text_content):
    """Sends large compiled text to Vertex AI to generate a detailed, expert-level report."""
    try:
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        You are an expert-level Cyber Security Analyst. Your task is to analyze the
        following compiled text, which contains scan results from multiple security tools.
        
        Your analysis must be detailed, thorough, and provide actionable, specific advice.
        
        **CRITICAL INSTRUCTIONS:**
        1.  **CORRELATE FINDINGS:** Do not just list findings. Correlate them. If 'amass'
            finds a subdomain and 'nmap' finds an open port on that same host, that is
            a single, high-priority correlated finding.
        2.  **BE DETAILED:** Do not use single sentences for descriptions or recommendations.
            Provide multi-step, clear, and specific remediation advice.
        3.  **NO HALLUCINATION:** You MUST ONLY use information explicitly present in the text.
            Do not invent findings or vulnerabilities.
        4.  **JSON OUTPUT ONLY:** Your response must be a JSON object matching the
            provided schema.
        
        Analyze this compiled text:
        ---
        {compiled_text_content}
        ---
        """
        
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=SECURITY_INSIGHTS_SCHEMA
        )
        
        request_contents = [Part.from_text(prompt)]
        response = model.generate_content(request_contents, generation_config=generation_config)
        report_dict = json.loads(response.text)
        print("Consolidated expert report generated successfully by Vertex AI.")
        return report_dict, None
        
    except Exception as e:
        print(f"Error calling Vertex AI API: {e}")
        return None, str(e)
