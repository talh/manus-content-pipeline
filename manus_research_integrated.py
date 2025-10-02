#!/usr/bin/env python3.11
"""
Manus Research Module - Working Implementation
Uses web scraping and requests to perform actual research
"""

import json
import re
import requests
from typing import Dict, List, Any
from datetime import datetime
from bs4 import BeautifulSoup
import time


def perform_comprehensive_research(instruction_text: str, max_results: int = 10, 
                                   date_range: str = "", category: str = "") -> Dict:
    """
    Perform comprehensive web research using web scraping
    
    Args:
        instruction_text: The research instruction/query
        max_results: Maximum number of cases to find
        date_range: Time period for research
        category: Research category
        
    Returns:
        Dictionary with structured research results
    """
    
    print(f"🔬 Starting web-based research...")
    print(f"📋 Query: {instruction_text[:100]}...")
    print(f"🎯 Target: {max_results} cases")
    
    if not instruction_text or not instruction_text.strip():
        print("⚠️  Empty instruction text, returning no results")
        return {
            'cases': [],
            'total_cases': 0,
            'research_query': instruction_text,
            'category': category,
            'metadata': {
                'date_range': date_range,
                'max_results': max_results,
                'research_timestamp': datetime.now().isoformat(),
                'note': 'Empty query provided'
            }
        }
    
    # Step 1: Generate search queries
    search_queries = generate_search_queries(instruction_text, category)
    print(f"🔍 Generated {len(search_queries)} search queries")
    
    # Step 2: Collect information from multiple sources
    all_findings = []
    
    # Limit to 2 queries to avoid rate limiting
    for idx, query in enumerate(search_queries[:2], 1):
        print(f"\n📡 Search {idx}/{min(2, len(search_queries))}: {query}")
        
        try:
            # Perform web search
            findings = search_web(query, max_results_per_query=5)
            all_findings.extend(findings)
            
            print(f"   ✓ Found {len(findings)} potential cases")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"   ⚠️  Search error: {e}")
            continue
    
    # Step 3: Deduplicate and rank findings
    print(f"\n🔄 Processing {len(all_findings)} findings...")
    unique_cases = deduplicate_cases(all_findings)
    print(f"   ✓ {len(unique_cases)} unique cases after deduplication")
    
    # Step 4: Select top cases
    top_cases = rank_and_select_cases(unique_cases, max_results)
    print(f"   ✓ Selected top {len(top_cases)} cases")
    
    # Step 5: Enrich cases
    enriched_cases = []
    for idx, case in enumerate(top_cases, 1):
        enriched = enrich_case_details(case)
        enriched_cases.append(enriched)
    
    results = {
        'cases': enriched_cases,
        'total_cases': len(enriched_cases),
        'research_query': instruction_text,
        'category': category,
        'metadata': {
            'date_range': date_range,
            'max_results': max_results,
            'queries_used': search_queries[:2],
            'total_findings': len(all_findings),
            'unique_findings': len(unique_cases),
            'research_timestamp': datetime.now().isoformat()
        }
    }
    
    print(f"\n✅ Research complete: {len(enriched_cases)} high-quality cases")
    
    return results


def generate_search_queries(instruction: str, category: str = "") -> List[str]:
    """Generate multiple search queries"""
    
    queries = []
    
    if instruction.strip():
        queries.append(instruction)
        
        if category:
            queries.append(f"{category} {instruction}")
        
        queries.append(f"{instruction} examples")
        queries.append(f"recent {instruction}")
    
    return [q for q in queries if q.strip()]


def search_web(query: str, max_results_per_query: int = 5) -> List[Dict]:
    """
    Perform web search using DuckDuckGo HTML (no API key needed)
    """
    
    if not query.strip():
        return []
    
    cases = []
    
    try:
        # Use DuckDuckGo HTML search (no API key required)
        url = "https://html.duckduckgo.com/html/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'q': query,
            'b': '',
            'kl': 'us-en'
        }
        
        print(f"      🌐 Searching DuckDuckGo...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = soup.find_all('div', class_='result')
            
            print(f"      📊 Found {len(results)} results")
            
            for idx, result in enumerate(results[:max_results_per_query]):
                try:
                    # Extract title
                    title_elem = result.find('a', class_='result__a')
                    title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                    
                    # Extract URL
                    url_elem = result.find('a', class_='result__url')
                    source_url = url_elem.get('href') if url_elem else ''
                    
                    # Extract snippet/description
                    snippet_elem = result.find('a', class_='result__snippet')
                    description = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if title and source_url:
                        case = {
                            'title': title,
                            'description': description,
                            'source': source_url,
                            'date': 'Recent',
                            'key_points': extract_key_points_from_text(description, max_points=3)
                        }
                        
                        cases.append(case)
                        print(f"      ✓ Extracted: {title[:50]}...")
                        
                except Exception as e:
                    print(f"      ⚠️  Could not parse result {idx}: {e}")
                    continue
        else:
            print(f"      ⚠️  Search returned status {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ Search error: {e}")
    
    return cases


def deduplicate_cases(cases: List[Dict]) -> List[Dict]:
    """Remove duplicates"""
    
    if not cases:
        return []
    
    unique_cases = []
    seen_titles = set()
    seen_urls = set()
    
    for case in cases:
        title = case.get('title', '').lower()
        url = case.get('source', '')
        
        title_key = re.sub(r'[^a-z0-9]+', '', title)
        
        if title_key and title_key not in seen_titles and url not in seen_urls:
            unique_cases.append(case)
            seen_titles.add(title_key)
            if url:
                seen_urls.add(url)
    
    return unique_cases


def rank_and_select_cases(cases: List[Dict], max_results: int) -> List[Dict]:
    """Rank and select top cases"""
    
    if not cases:
        return []
    
    scored_cases = []
    for case in cases:
        score = calculate_case_quality_score(case)
        scored_cases.append((score, case))
    
    scored_cases.sort(key=lambda x: x[0], reverse=True)
    
    return [case for score, case in scored_cases[:max_results]]


def calculate_case_quality_score(case: Dict) -> float:
    """Calculate quality score"""
    
    score = 0.0
    
    if case.get('title'):
        score += 1.0
    
    description = case.get('description', '')
    if description:
        score += 1.0
        score += min(len(description) / 500, 2.0)
    
    if case.get('source'):
        score += 1.0
    
    if case.get('date'):
        score += 0.5
    
    key_points = case.get('key_points', [])
    if key_points:
        score += min(len(key_points) * 0.3, 1.5)
    
    return score


def enrich_case_details(case: Dict) -> Dict:
    """Enrich case with defaults"""
    
    enriched = case.copy()
    
    if not enriched.get('title'):
        enriched['title'] = 'Untitled Case'
    
    if not enriched.get('description'):
        enriched['description'] = 'No description available'
    
    if not enriched.get('source'):
        enriched['source'] = 'Source not available'
    
    if not enriched.get('date'):
        enriched['date'] = 'Recent'
    
    if not enriched.get('key_points'):
        if enriched.get('description'):
            enriched['key_points'] = extract_key_points_from_text(enriched['description'], max_points=5)
        else:
            enriched['key_points'] = ['Details from source']
    
    enriched['quality_score'] = calculate_case_quality_score(enriched)
    
    return enriched


def extract_key_points_from_text(text: str, max_points: int = 5) -> List[str]:
    """Extract key points from text"""
    
    if not text:
        return []
    
    sentences = re.split(r'[.!?]+', text)
    
    key_points = []
    for sentence in sentences:
        sentence = sentence.strip()
        if 20 < len(sentence) < 200:
            key_points.append(sentence)
            if len(key_points) >= max_points:
                break
    
    return key_points


if __name__ == '__main__':
    # Test
    results = perform_comprehensive_research(
        instruction_text="artificial intelligence healthcare applications",
        max_results=5,
        date_range="Recent",
        category="Technology"
    )
    
    print("\n" + "="*60)
    print("RESEARCH RESULTS")
    print("="*60)
    print(f"Total cases: {results['total_cases']}")
    for idx, case in enumerate(results['cases'], 1):
        print(f"\nCase {idx}: {case['title']}")
        print(f"  Source: {case['source']}")
        print(f"  Description: {case['description'][:100]}...")
