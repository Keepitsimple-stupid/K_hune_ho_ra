"""
News retrieval module with multi-backend support for the Neural News Analysis System.

This module provides resilient news article retrieval using multiple backends:
- GNews (Google News RSS) as primary backend (no API key required)
- DuckDuckGo search as fallback backend with rate limiting protection
"""

import logging
import random
import time
from typing import List, Dict, Any

# Optional backend imports with graceful degradation
try:
    from gnews import GNews
    GNEWS_AVAILABLE = True
except ImportError:
    GNEWS_AVAILABLE = False
    logging.warning("gnews package not installed. Please install it with: pip install gnews")

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("duckduckgo-search package not installed. Please install it with: pip install duckduckgo-search")

class NewsRetriever:
    """
    Resilient news retriever with multi-backend support.
    
    Prioritizes GNews for reliability and falls back to DuckDuckGo if needed.
    Implements duplicate removal, rate limiting protection, and graceful degradation.
    """

    def __init__(self, max_articles: int = 15, time_range: str = "week", verbose: bool = False):
        """
        Initialize the NewsRetriever.

        Args:
            max_articles: Maximum number of articles to retrieve per search
            time_range: Time filter for news search ('day', 'week', or 'month')
            verbose: Enable verbose logging for debugging
        """
        self.max_articles = max_articles
        self.time_range = time_range
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Map time range strings to day counts for GNews API
        self._days_map = {
            "day": 1,
            "week": 7,
            "month": 30
        }
        self._days = self._days_map.get(self.time_range, 7)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for news articles using available backends.

        Tries GNews first (more reliable, no API key required), then falls back
        to DuckDuckGo if GNews fails or returns no results. Removes duplicate
        articles by URL before returning.

        Args:
            query: Search query string

        Returns:
            List of article dictionaries with title, url, snippet, date, and source
        """
        if self.verbose:
            self.logger.info(f"Searching for news: {query}")

        # Try GNews first (more reliable, no API key needed)
        if GNEWS_AVAILABLE:
            articles = self._search_gnews(query)
            if articles:
                if self.verbose:
                    self.logger.info(f"Retrieved {len(articles)} articles from GNews")
                # Remove duplicates by URL
                seen_urls = set()
                unique_articles = []
                for article in articles:
                    if article['url'] not in seen_urls:
                        seen_urls.add(article['url'])
                        unique_articles.append(article)
                return unique_articles[:self.max_articles]

        # Fall back to DuckDuckGo if GNews fails
        if DDGS_AVAILABLE:
            if self.verbose:
                self.logger.info("Falling back to DuckDuckGo search")
            articles = self._search_duckduckgo(query)
            if articles:
                return articles[:self.max_articles]

        # Return empty list if both methods fail
        self.logger.warning("No news articles found. Make sure you have installed: pip install gnews duckduckgo-search")
        return []

    def _search_gnews(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for news using GNews (Google News RSS backend).
        
        GNews provides reliable news aggregation without requiring API keys.
        Returns articles with title, URL, description, publication date, and source.

        Args:
            query: Search query string
            
        Returns:
            List of article dictionaries or empty list on error
        """
        try:
            google_news = GNews(
                language='en',
                country='US',
                max_results=self.max_articles,
                period=f"{self._days}d"  # e.g., "7d" for last 7 days
            )
            news = google_news.get_news(query)

            if not news:
                return []

            articles = []
            for item in news:
                article = {
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('description', ''),
                    "date": item.get('published date', ''),
                    "source": item.get('publisher', {}).get('title', '')
                }
                articles.append(article)

            return articles
        except Exception as e:
            if self.verbose:
                self.logger.error(f"GNews error: {e}")
            return []

    def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        Fallback search using DuckDuckGo with rate limiting protection.
        
        Adds a random delay (1-3 seconds) before each request to avoid rate limits.
        Appends 'news' to the query to focus results on news content.

        Args:
            query: Search query string
            
        Returns:
            List of article dictionaries or empty list on error
        """
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

            with DDGS() as ddgs:
                results = ddgs.text(
                    query + " news",
                    region='wt-wt',
                    max_results=self.max_articles,
                    timelimit=self.time_range
                )

                articles = []
                for result in results:
                    article = {
                        "title": result.get('title', ''),
                        "url": result.get('href', ''),
                        "snippet": result.get('body', ''),
                        "date": result.get('date', ''),
                        "source": result.get('source', '')
                    }
                    articles.append(article)

                return articles
        except Exception as e:
            if self.verbose:
                self.logger.error(f"DuckDuckGo error: {e}")
            return []