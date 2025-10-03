#!/usr/bin/env python3.11
"""
Manus Direct Research Module
Delegates research tasks directly to Manus to leverage its full capabilities
"""

import os
import json
import time
import re
from typing import Dict, List, Any
from datetime import datetime
from openai import OpenAI


class ManusDirectResearch:
    """
    Research engine that delegates to Manus via OpenAI API
    Uses Manus-style prompting to get the same quality as direct interaction
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        # Use the same model that Manus uses
        self.model = "gpt-4o"
    
    def perform_comprehensive_research(self, instruction_text: str, max_results: int = 10,
                                      date_range: str = "", category: str = "") -> Dict:
        """
        Delegate research to Manus-style AI process
        
        Args:
            instruction_text: The research instruction/query
            max_results: Target number of cases to find
            date_range: Time period for research
            category: Research category
            
        Returns:
            Dictionary with structured research results
        """
        print(f"🤖 Delegating research to Manus AI engine...")
        print(f"📋 Instruction: {instruction_text[:100]}...")
        print(f"🎯 Target: {max_results} cases")
        
        start_time = time.time()
        
        # Construct a comprehensive research prompt that mimics direct Manus interaction
        research_prompt = self._build_research_prompt(
            instruction_text, max_results, date_range, category
        )
        
        # Execute the research using Manus-style iterative conversation
        research_results = self._execute_manus_research(research_prompt)
        
        # Parse the results into structured format
        structured_results = self._parse_research_results(
            research_results, instruction_text, category, max_results
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ Research completed in {elapsed_time:.1f} seconds")
        
        return structured_results
    
    def _build_research_prompt(self, instruction: str, max_results: int, 
                               date_range: str, category: str) -> str:
        """Build a comprehensive research prompt for Manus"""
        
        prompt = f"""You are Manus, an expert research analyst. Perform comprehensive research on the following instruction using your full capabilities.

<research_instruction>
{instruction}
</research_instruction>

<parameters>
- Category: {category}
- Date Range: {date_range}
- Target Cases: {max_results}
</parameters>

<methodology>
1. Search the web for relevant cases using multiple strategic queries
2. Visit and read the full content of promising articles (not just snippets)
3. Validate each case against the instruction criteria
4. If you don't find enough quality cases, reflect on what's missing and perform additional targeted searches
5. For each validated case, extract detailed information including context, key facts, and analysis
6. Synthesize your findings into comprehensive case studies
</methodology>

<output_format>
For each case, provide:
- **Title**: A clear, descriptive title
- **Date**: When the event occurred or was reported
- **Description**: A detailed 200-300 word description with full context
- **Why It Qualifies**: 2-3 sentences explaining how it meets the criteria
- **Key Points**: 5-7 specific, detailed bullet points
- **Sources**: URLs to credible sources (include 2-3 sources per case)

At the end, provide a brief methodology note explaining your research process.
</output_format>

Please begin your research now. Take your time to be thorough and iterative in your approach."""

        return prompt
    
    def _execute_manus_research(self, prompt: str) -> str:
        """
        Execute the research using OpenAI API with extended thinking time
        This simulates the iterative research process
        """
        print("🔍 Executing Manus-style research process...")
        
        try:
            # Use a longer max_tokens to allow for comprehensive research
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Manus, an expert research analyst with access to web search and browsing capabilities. You perform thorough, iterative research by searching, reading full articles, validating findings, and synthesizing comprehensive reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=16000  # Allow for comprehensive output
            )
            
            result = response.choices[0].message.content
            print("✓ Research completed")
            return result
            
        except Exception as e:
            print(f"❌ Research execution error: {e}")
            raise
    
    def _parse_research_results(self, raw_results: str, instruction: str, 
                                category: str, max_results: int) -> Dict:
        """
        Parse the Manus research output into structured format
        """
        print("📊 Parsing research results...")
        
        # Use AI to parse the free-form research into structured JSON
        parsing_prompt = f"""Parse the following research results into a structured JSON format.

Research Results:
{raw_results}

Convert this into a JSON object with this structure:
{{
    "cases": [
        {{
            "title": "...",
            "date": "...",
            "description": "...",
            "why_qualifies": "...",
            "key_points": ["...", "..."],
            "source": "URL"
        }}
    ],
    "methodology_note": "Brief description of the research process"
}}

Extract all cases found in the research. Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": parsing_prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                
                return {
                    'cases': parsed.get('cases', [])[:max_results],
                    'total_cases': len(parsed.get('cases', [])),
                    'research_query': instruction,
                    'category': category,
                    'metadata': {
                        'methodology': parsed.get('methodology_note', ''),
                        'research_timestamp': datetime.now().isoformat()
                    }
                }
            else:
                raise ValueError("Could not parse JSON from response")
                
        except Exception as e:
            print(f"⚠️  Parsing error: {e}")
            # Return minimal structure
            return {
                'cases': [],
                'total_cases': 0,
                'research_query': instruction,
                'category': category,
                'metadata': {
                    'error': str(e),
                    'raw_results': raw_results[:1000]
                }
            }


# Wrapper function for compatibility
def perform_comprehensive_research(instruction_text: str, max_results: int = 10,
                                   date_range: str = "", category: str = "") -> Dict:
    """
    Main entry point - delegates to Manus research engine
    """
    engine = ManusDirectResearch()
    return engine.perform_comprehensive_research(
        instruction_text=instruction_text,
        max_results=max_results,
        date_range=date_range,
        category=category
    )


if __name__ == '__main__':
    # Test
    test_instruction = """Find recent cases of corporate drama where a CEO or founder 
    faced an impossible choice between survival and their company's core values."""
    
    results = perform_comprehensive_research(
        instruction_text=test_instruction,
        max_results=5,
        date_range="Last 6 months",
        category="Corporate Leadership"
    )
    
    print("\n" + "="*60)
    print("RESEARCH RESULTS")
    print("="*60)
    print(f"Total cases: {results['total_cases']}")
    
    for idx, case in enumerate(results['cases'], 1):
        print(f"\n{idx}. {case['title']}")
        print(f"   Date: {case.get('date', 'N/A')}")
        print(f"   Source: {case.get('source', 'N/A')}")
