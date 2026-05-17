from src.config import config
from datetime import datetime

class Synthesizer:
    def __init__(self):
        self.weights = config.DOMAIN_WEIGHTS
    
    def compute_weights(self, topic: str) -> dict:
        # Simple dynamic: boost if domain word appears in topic
        topic_lower = topic.lower()
        boosted = self.weights.copy()
        for d in boosted:
            if d in topic_lower:
                boosted[d] = min(1.0, boosted[d] + 0.1)
        return boosted
    
    def build_timeline(self, articles):
        timeline = []
        for a in articles:
            if a.get("date"):
                timeline.append({"date": a["date"], "title": a["title"][:80]})
        timeline.sort(key=lambda x: x["date"])
        return timeline[:10]
    
    def generate_scenarios(self, results):
        scenarios = []
        if "predictive" in results and "error" not in results["predictive"]:
            p = results["predictive"]
            scenarios.append(f"Short-term: {p.get('short_term_outlook', 'N/A')}")
            scenarios.append(f"Long-term: {p.get('long_term_outlook', 'N/A')}")
        else:
            scenarios.append("No clear prediction from predictive agent.")
        return "\n".join(scenarios)
    
    def final_report(self, topic, articles, agent_results):
        weights = self.compute_weights(topic)
        top_domains = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        timeline = self.build_timeline(articles)
        scenarios = self.generate_scenarios(agent_results)
        
        report = f"""
------ ANALYSIS REPORT ------

Topic: {topic}
Generated from {len(articles)} news articles
Timestamp: {datetime.now().isoformat()}

== TOP INFLUENCING DOMAINS ==
"""
        for d, w in top_domains:
            report += f"  - {d.upper()} (weight {w:.2f})\n"
        
        report += "\n== DOMAIN INSIGHTS ==\n"
        for domain in config.DOMAINS[:5]:  # show first 5 for brevity
            if domain in agent_results and "error" not in agent_results[domain]:
                res = agent_results[domain]
                report += f"\n[{domain.upper()}]\n"
                for k, v in res.items():
                    if isinstance(v, list):
                        v = ", ".join(v)
                    report += f"  {k}: {v}\n"
        
        if timeline:
            report += "\n== TIMELINE ==\n"
            for t in timeline:
                report += f"  {t['date']}: {t['title']}\n"
        
        report += f"\n== FUTURE SCENARIOS ==\n{scenarios}\n"
        
        report += "\n== SOURCES ==\n"
        for i, a in enumerate(articles, 1):
            report += f"{i}. {a['title']}\n   {a['url']}\n   Date: {a.get('date','unknown')}\n\n"
        
        return report