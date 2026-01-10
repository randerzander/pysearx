"""
Tests for API-based search engines (DuckDuckGo and Bing).

These tests verify that the new API-based engines work correctly
and provide better reliability than HTML scraping.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pysearx.base import SearchEngine


class TestDuckDuckGoAPIEngine(unittest.TestCase):
    """Test cases for DuckDuckGoAPIEngine."""
    
    def test_import_when_available(self):
        """Test that DuckDuckGoAPIEngine can be imported when ddgs is installed."""
        try:
            from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine, is_available
            # If import succeeds, check availability
            if is_available():
                self.assertTrue(True)
            else:
                self.skipTest("ddgs package not installed")
        except ImportError:
            self.skipTest("ddgs package not installed")
    
    def test_initialization_without_package(self):
        """Test that initialization fails gracefully without ddgs package."""
        # Mock the import to simulate missing package
        with patch('pysearx.engines.duckduckgo_api.DDGS_AVAILABLE', False):
            from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
            
            with self.assertRaises(ImportError) as context:
                engine = DuckDuckGoAPIEngine()
            
            self.assertIn('ddgs', str(context.exception).lower())
    
    @patch('pysearx.engines.duckduckgo_api.DDGS_AVAILABLE', True)
    @patch('pysearx.engines.duckduckgo_api.DDGS')
    def test_search_basic(self, mock_ddgs_class):
        """Test basic search functionality."""
        # Mock DDGS instance
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=False)
        mock_ddgs_class.return_value = mock_ddgs
        
        # Mock search results
        mock_results = [
            {
                'title': 'Test Result 1',
                'href': 'https://example.com/1',
                'body': 'Test description 1'
            },
            {
                'title': 'Test Result 2',
                'href': 'https://example.com/2',
                'body': 'Test description 2'
            }
        ]
        mock_ddgs.text.return_value = mock_results
        
        # Import and test
        from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
        engine = DuckDuckGoAPIEngine()
        results = engine.search("test query")
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Result 1')
        self.assertEqual(results[0]['url'], 'https://example.com/1')
        self.assertEqual(results[0]['description'], 'Test description 1')
    
    @patch('pysearx.engines.duckduckgo_api.DDGS_AVAILABLE', True)
    @patch('pysearx.engines.duckduckgo_api.DDGS')
    def test_search_filters_invalid_results(self, mock_ddgs_class):
        """Test that results without URLs are filtered out."""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=False)
        mock_ddgs_class.return_value = mock_ddgs
        
        # Mock results with one invalid entry (no href)
        mock_results = [
            {
                'title': 'Valid Result',
                'href': 'https://example.com/1',
                'body': 'Description'
            },
            {
                'title': 'Invalid Result',
                # Missing 'href'
                'body': 'Description'
            }
        ]
        mock_ddgs.text.return_value = mock_results
        
        from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
        engine = DuckDuckGoAPIEngine()
        results = engine.search("test query")
        
        # Should only get the valid result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Valid Result')


class TestBingAPIEngine(unittest.TestCase):
    """Test cases for BingAPIEngine."""
    
    def test_import_when_available(self):
        """Test that BingAPIEngine can be imported when azure package is installed."""
        try:
            from pysearx.engines.bing_api import BingAPIEngine, is_available
            # If import succeeds, check availability
            if is_available():
                self.assertTrue(True)
            else:
                self.skipTest("azure-cognitiveservices-search-websearch not installed")
        except ImportError:
            self.skipTest("azure-cognitiveservices-search-websearch not installed")
    
    def test_initialization_without_package(self):
        """Test that initialization fails gracefully without azure package."""
        with patch('pysearx.engines.bing_api.AZURE_AVAILABLE', False):
            from pysearx.engines.bing_api import BingAPIEngine
            
            with self.assertRaises(ImportError) as context:
                engine = BingAPIEngine(api_key="test")
            
            self.assertIn('azure', str(context.exception).lower())
    
    @patch('pysearx.engines.bing_api.AZURE_AVAILABLE', True)
    def test_initialization_without_api_key(self):
        """Test that initialization requires API key."""
        from pysearx.engines.bing_api import BingAPIEngine
        
        with self.assertRaises(ValueError) as context:
            engine = BingAPIEngine(api_key="")
        
        self.assertIn('api key', str(context.exception).lower())
    
    @patch('pysearx.engines.bing_api.AZURE_AVAILABLE', True)
    def test_search_basic(self):
        """Test basic search functionality."""
        # Mock the Azure imports
        with patch('pysearx.engines.bing_api.WebSearchClient') as mock_client_class, \
             patch('pysearx.engines.bing_api.CognitiveServicesCredentials'):
            
            # Mock the Azure client
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock search response
            mock_result1 = MagicMock()
            mock_result1.name = 'Test Result 1'
            mock_result1.url = 'https://example.com/1'
            mock_result1.snippet = 'Test description 1'
            
            mock_result2 = MagicMock()
            mock_result2.name = 'Test Result 2'
            mock_result2.url = 'https://example.com/2'
            mock_result2.snippet = 'Test description 2'
            
            mock_response = MagicMock()
            mock_response.web_pages.value = [mock_result1, mock_result2]
            mock_client.web.search.return_value = mock_response
            
            # Import and test
            from pysearx.engines.bing_api import BingAPIEngine
            engine = BingAPIEngine(api_key="test_key")
            results = engine.search("test query")
            
            # Verify results
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['title'], 'Test Result 1')
            self.assertEqual(results[0]['url'], 'https://example.com/1')
            self.assertEqual(results[0]['description'], 'Test description 1')


class TestAPIEngineIntegration(unittest.TestCase):
    """Test integration of API engines with main search function."""
    
    @patch('pysearx.engines.duckduckgo_api.DDGS_AVAILABLE', True)
    @patch('pysearx.engines.duckduckgo_api.DDGS')
    def test_duckduckgo_api_in_search(self, mock_ddgs_class):
        """Test using DuckDuckGoAPIEngine with main search function."""
        # Mock DDGS
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=False)
        mock_ddgs_class.return_value = mock_ddgs
        
        mock_results = [
            {
                'title': 'API Result',
                'href': 'https://example.com',
                'body': 'From API'
            }
        ]
        mock_ddgs.text.return_value = mock_results
        
        # Use with search function
        from pysearx import search
        from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
        
        engine = DuckDuckGoAPIEngine()
        results = search("test", engines=[engine])
        
        self.assertGreater(len(results), 0)
        self.assertIn('engine', results[0])


if __name__ == '__main__':
    unittest.main()
