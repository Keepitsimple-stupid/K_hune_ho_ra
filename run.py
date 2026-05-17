#!/usr/bin/env python3
from src.news_retriever import NewsRetriever
from src.agent_manager import AgentManager
from src.synthesizer import Synthesizer

def main():
    print("\n[KHUNEHO?] Neural News Analysis System (Topic-to-Report)")
    print("Type 'exit' to quit.\n")
    
    retriever = NewsRetriever()
    agent_mgr = AgentManager()
    synthesizer = Synthesizer()
    
    while True:
        topic = input("> Topic: ").strip()
        if topic.lower() in ("exit", "quit"):
            break
        if not topic:
            continue
        
        print(f"\n[1/3] Searching news for: {topic}")
        articles = retriever.search(topic)
        if not articles:
            print("No articles found. Try another topic.\n")
            continue
        print(f"      Found {len(articles)} articles.\n")
        
        print("[2/3] Running 15 reasoning agents...")
        agent_results = agent_mgr.run_all_agents(articles)
        
        print("\n[3/3] Generating report...")
        report = synthesizer.final_report(topic, articles, agent_results)
        
        print("\n" + "="*70)
        print(report)
        print("="*70 + "\n")

if __name__ == "__main__":
    main()