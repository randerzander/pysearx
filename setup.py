from setuptools import setup, find_packages

setup(
    name='pysearx',
    version='0.1.0',
    description='A plain Python library for generic web search',
    author='pysearx contributors',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'lxml>=4.6.0',
    ],
    extras_require={
        # DuckDuckGo API support (recommended, avoids CAPTCHA/blocking)
        'ddg-api': [
            'ddgs>=9.0.0',
        ],
        # Bing API support (optional, requires Azure API key)
        'bing-api': [
            'azure-cognitiveservices-search-websearch>=2.0.0',
        ],
        # All optional API integrations
        'all-apis': [
            'ddgs>=9.0.0',
            'azure-cognitiveservices-search-websearch>=2.0.0',
        ],
    },
    python_requires='>=3.7',
)
