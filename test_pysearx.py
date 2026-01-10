"""
Unit tests for pysearx library.

These tests verify the core functionality of the library.
"""

import unittest
from unittest.mock import Mock, patch
from pysearx import search, SearchEngine


class MockSearchEngine(SearchEngine):
    """Mock search engine for testing."""
    
    def search(self, query, **kwargs):
        """Return mock results."""
        return [
            {
                'title': f'Result 1 for {query}',
                'url': 'https://example.com/1',
                'description': 'This is the first result'
            },
            {
                'title': f'Result 2 for {query}',
                'url': 'https://example.com/2',
                'description': 'This is the second result'
            },
            {
                'title': f'Result 3 for {query}',
                'url': 'https://example.com/3',
                'description': 'This is the third result'
            }
        ]


class TestPysearx(unittest.TestCase):
    """Test cases for pysearx library."""
    
    def test_search_basic(self):
        """Test basic search functionality."""
        mock_engine = MockSearchEngine()
        results = search("test query", engines=[mock_engine])
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
    def test_search_result_structure(self):
        """Test that results have the correct structure."""
        mock_engine = MockSearchEngine()
        results = search("test query", engines=[mock_engine])
        
        for result in results:
            self.assertIn('title', result)
            self.assertIn('url', result)
            self.assertIn('description', result)
            self.assertIn('engine', result)
            
    def test_search_max_results(self):
        """Test max_results parameter."""
        mock_engine = MockSearchEngine()
        results = search("test query", engines=[mock_engine], max_results=2)
        
        self.assertEqual(len(results), 2)
        
    def test_search_deduplication(self):
        """Test that duplicate URLs are filtered out."""
        
        class DuplicateEngine(SearchEngine):
            def search(self, query, **kwargs):
                return [
                    {'title': 'A', 'url': 'https://example.com/same', 'description': 'desc1'},
                    {'title': 'B', 'url': 'https://example.com/same', 'description': 'desc2'},
                    {'title': 'C', 'url': 'https://example.com/different', 'description': 'desc3'},
                ]
        
        results = search("test", engines=[DuplicateEngine()])
        
        # Should only get 2 results (duplicates removed)
        self.assertEqual(len(results), 2)
        urls = [r['url'] for r in results]
        self.assertEqual(len(urls), len(set(urls)))  # All unique
        
    def test_search_engine_error_handling(self):
        """Test that errors in one engine don't break the search."""
        
        class ErrorEngine(SearchEngine):
            def search(self, query, **kwargs):
                raise Exception("Engine error")
        
        mock_engine = MockSearchEngine()
        results = search("test", engines=[ErrorEngine(), mock_engine])
        
        # Should still get results from mock_engine
        self.assertGreater(len(results), 0)
        
    def test_empty_query(self):
        """Test search with empty query."""
        mock_engine = MockSearchEngine()
        results = search("", engines=[mock_engine])
        
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
