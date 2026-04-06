import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAnalytics:
    """Gemini 1.5 Pro powered analytics service for medical chart validation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key. If None, tries to load from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment variable.\n"
                "Create a .env file in the medchart_demo directory with:\n"
                "GEMINI_API_KEY=your_api_key_here\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Use gemini-1.5-pro-latest to avoid 404 errors with v1beta API
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Initialize cache
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, prompt: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        cache_key = self._get_cache_key(prompt)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now() - cached['timestamp'] < self.cache_ttl:
                return cached['response']
        return None
    
    def _cache_response(self, prompt: str, response: str):
        """Cache response with timestamp."""
        cache_key = self._get_cache_key(prompt)
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
    
    def generate(self, prompt: str, use_cache: bool = True) -> str:
        """
        Generate response using Gemini 1.5 Pro.
        
        Args:
            prompt: The prompt to send to Gemini
            use_cache: Whether to use cached responses
            
        Returns:
            Generated text response
        """
        # Check cache first
        if use_cache:
            cached = self._get_cached_response(prompt)
            if cached:
                return cached
        
        # Generate new response
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Cache the response
            if use_cache:
                self._cache_response(prompt, result)
            
            return result
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def analyze_trends(self, results_df) -> str:
        """Analyze validation trends from historical data."""
        from analytics_prompts import get_trend_analysis_prompt
        
        # Prepare data summary
        summary = {
            'total': len(results_df),
            'approved': len(results_df[results_df['decision'] == 'approved']),
            'rejected': len(results_df[results_df['decision'] == 'rejected']),
            'manual_review': len(results_df[results_df['decision'] == 'manual_review']),
            'avg_confidence': results_df['confidence'].mean(),
            'avg_gap_score': results_df['gap_score'].mean(),
            'total_flags': results_df['disc_count'].sum(),
            'date_range': f"{results_df['created_at'].min()} to {results_df['created_at'].max()}"
        }
        
        # Get common flags
        all_flags = []
        for flags_str in results_df['flags'].dropna():
            if flags_str:
                all_flags.extend(flags_str.split(' | '))
        
        from collections import Counter
        flag_counts = Counter(all_flags).most_common(5)
        
        prompt = get_trend_analysis_prompt(summary, flag_counts)
        return self.generate(prompt)
    
    def explain_decision(self, result: Dict[str, Any]) -> str:
        """Generate human-friendly explanation of validation decision."""
        from analytics_prompts import get_decision_explanation_prompt
        
        prompt = get_decision_explanation_prompt(result)
        return self.generate(prompt)
    
    def root_cause_analysis(self, filtered_results: List[Dict[str, Any]], analysis_type: str) -> str:
        """Identify root causes for specific decision patterns."""
        from analytics_prompts import get_root_cause_prompt
        
        prompt = get_root_cause_prompt(filtered_results, analysis_type)
        return self.generate(prompt)
    
    def natural_language_query(self, question: str, results_df) -> str:
        """Answer natural language questions about validation data."""
        from analytics_prompts import get_nl_query_prompt
        
        # Prepare data context
        data_summary = {
            'total_records': len(results_df),
            'columns': list(results_df.columns),
            'sample_data': results_df.head(3).to_dict('records'),
            'decision_counts': results_df['decision'].value_counts().to_dict(),
            'date_range': f"{results_df['created_at'].min()} to {results_df['created_at'].max()}"
        }
        
        prompt = get_nl_query_prompt(question, data_summary)
        return self.generate(prompt)
    
    def generate_alerts(self, current_summary: Dict, historical_summary: Dict) -> List[Dict[str, str]]:
        """Generate automated alerts by comparing current vs historical metrics."""
        from analytics_prompts import get_alerts_prompt
        
        prompt = get_alerts_prompt(current_summary, historical_summary)
        response = self.generate(prompt)
        
        # Parse response into structured alerts
        alerts = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('🔴'):
                alerts.append({'severity': 'high', 'message': line[2:].strip()})
            elif line.startswith('🟡'):
                alerts.append({'severity': 'medium', 'message': line[2:].strip()})
            elif line.startswith('🟢'):
                alerts.append({'severity': 'low', 'message': line[2:].strip()})
        
        return alerts if alerts else [{'severity': 'low', 'message': 'No significant anomalies detected'}]

# Made with Bob
