#!/usr/bin/env python3
"""
Neural News Analysis System - Main Entry Point

This script provides an interactive CLI for analyzing news topics using
15 specialized AI agents across multiple domains (financial, geopolitical,
technological, etc.) to generate comprehensive prediction reports.

Usage:
    python run.py

Commands:
    - Enter a topic to analyze
    - Type 'exit' or 'quit' to exit
"""

from src.news_retriever import NewsRetriever
from src.agent_manager import AgentManager
from src.synthesizer import Synthesizer


def print_header():
    """Display the application header with styling."""
    print("\n" + "="*70)
    print("  K_HUNE_HORA? Neural News Analysis System")
    print("  Multi-Domain AI-Powered Topic Analysis")
    print("="*70)
    print("\nCommands: Enter a topic | Type 'exit' to quit\n")


def print_step(step_num: int, total_steps: int, message: str):
    """Display a progress step with consistent formatting.
    
    Args:
        step_num: Current step number
        total_steps: Total number of steps
        message: Step description
    """
    print(f"\n[{step_num}/{total_steps}] {message}")


def print_success(message: str):
    """Display a success message with checkmark.
    
    Args:
        message: Success message to display
    """
    print(f"  ✓ {message}")


def print_error(message: str):
    """Display an error message with cross mark.
    
    Args:
        message: Error message to display
    """
    print(f"  ✗ {message}")


def print_separator():
    """Display a visual separator."""
    print("\n" + "="*70)


def main():
    """Main application loop for interactive news analysis."""
    print_header()
    
    # Initialize components
    retriever = NewsRetriever()
    agent_mgr = AgentManager()
    synthesizer = Synthesizer()
    
    while True:
        try:
            topic = input("> Topic: ").strip()
            
            # Handle exit commands
            if topic.lower() in ("exit", "quit"):
                print("\nExiting. Goodbye!\n")
                break
            
            # Skip empty input
            if not topic:
                continue
            
            # Step 1: News Retrieval
            print_step(1, 3, f"Searching news for: '{topic}'")
            articles = retriever.search(topic)
            
            if not articles:
                print_error("No articles found. Try another topic.")
                continue
            
            print_success(f"Found {len(articles)} articles")
            
            # Step 2: Agent Analysis
            print_step(2, 3, "Running 15 reasoning agents")
            agent_results = agent_mgr.run_all_agents(articles)
            
            # Step 3: Report Generation
            print_step(3, 3, "Generating comprehensive report")
            report = synthesizer.final_report(topic, articles, agent_results)
            
            # Display Report
            print_separator()
            print(report)
            print_separator()
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting gracefully.\n")
            break
        except Exception as e:
            print_error(f"An error occurred: {e}")
            print("Please try again or check your configuration.\n")


if __name__ == "__main__":
    main()