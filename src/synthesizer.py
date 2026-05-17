"""
Report synthesis module for the Neural News Analysis System.

This module combines predictions from multiple analysis domains into a comprehensive
report with weighted domain analysis, timelines, and source citations.
"""

from src.config import config
from datetime import datetime


class Synthesizer:
    """
    Synthesizes multi-domain analysis results into a comprehensive report.
    
    The Synthesizer applies domain-specific weights to prioritize relevant insights,
    builds chronological timelines, and formats predictions for readability.
    """
    
    def __init__(self):
        """Initialize the synthesizer with domain weights from configuration."""
        self.weights = config.DOMAIN_WEIGHTS
    
    def compute_weights(self, topic: str) -> dict:
        """
        Dynamically adjust domain weights based on topic relevance.
        
        If a domain name appears in the topic query, its weight is boosted
        to increase its influence in the final report.
        
        Args:
            topic: The search topic string
            
        Returns:
            Dictionary of domain names to adjusted weights
        """
        topic_lower = topic.lower()
        boosted = self.weights.copy()
        for d in boosted:
            if d in topic_lower:
                boosted[d] = min(1.0, boosted[d] + 0.1)
        return boosted
    
    def build_timeline(self, articles):
        """
        Build a chronological timeline from article dates.
        
        Args:
            articles: List of article dictionaries with 'date' and 'title' keys
            
        Returns:
            List of up to 10 timeline entries sorted by date
        """
        timeline = []
        for a in articles:
            if a.get("date"):
                timeline.append({"date": a["date"], "title": a["title"][:80]})
        timeline.sort(key=lambda x: x["date"])
        return timeline[:10]
    
    def format_predictions(self, domain, data):
        """
        Format domain predictions into a readable string.
        
        Dynamically handles domain-specific fields (e.g., affected_group, sector)
        in addition to the standard prediction, confidence, and timeline fields.
        
        Args:
            domain: The domain name for context
            data: Dictionary containing 'predictions' list
            
        Returns:
            Formatted string of predictions
        """
        if "predictions" not in data or not data["predictions"]:
            return "  No predictions generated.\n"
        lines = []
        for i, pred in enumerate(data["predictions"], 1):
            lines.append(f"    {i}. {pred.get('prediction', 'N/A')}")
            lines.append(f"       Confidence: {pred.get('confidence', 'N/A')} | Timeline: {pred.get('timeline', 'N/A')}")
            # Dynamically add domain-specific fields (affected_group, sector, etc.)
            extra_fields = [k for k in pred.keys() if k not in ['prediction', 'confidence', 'timeline']]
            for field in extra_fields:
                lines.append(f"       {field.replace('_',' ').title()}: {pred[field]}")
            lines.append("")  # empty line between predictions
        return "\n".join(lines)
    
    def final_report(self, topic, articles, agent_results):
        """
        Generate the final comprehensive analysis report.
        
        Combines weighted domain predictions, chronological timeline,
        and source citations into a single formatted report.
        
        Args:
            topic: The analysis topic
            articles: List of retrieved news articles
            agent_results: Dictionary of domain analysis results
            
        Returns:
            Formatted report string
        """
        weights = self.compute_weights(topic)
        timeline = self.build_timeline(articles)
        
        report = f"""
------ IN-DEPTH PREDICTIONS REPORT ------

Topic: {topic}
Generated from {len(articles)} news articles
Timestamp: {datetime.now().isoformat()}

=== DOMAIN-WISE PREDICTIONS (5-10 each) ===
"""
        for domain in config.DOMAINS:
            weight = weights.get(domain, 0.5)
            report += f"\n## {domain.upper()} (weight {weight:.2f})\n"
            if domain in agent_results and "predictions" in agent_results[domain]:
                report += self.format_predictions(domain, agent_results[domain])
            else:
                report += "  Failed to generate predictions.\n"
        
        if timeline:
            report += "\n=== TIMELINE OF SOURCES ===\n"
            for t in timeline:
                report += f"  {t['date']}: {t['title']}\n"
        
        report += "\n=== FULL NEWS SOURCES ===\n"
        for i, a in enumerate(articles, 1):
            report += f"{i}. {a['title']}\n   {a['url']}\n   Date: {a.get('date','unknown')}\n\n"
        
        return report