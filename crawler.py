import requests
from bs4 import BeautifulSoup

# Define the base URL for the arXiv API
base_url = 'http://export.arxiv.org/api/query?'

# Define the search parameters
search_params = "search_query=ti:jumping&sortBy=submittedDate&sortOrder=descending"

# Make the API request
response = requests.get(f"{base_url}{search_params}")

# Parse the response
soup = BeautifulSoup(response.content, 'lxml-xml')

# Loop through each entry (paper)
for entry in soup.findAll('entry'):
    title = entry.find('title').text
    summary = entry.find('summary').text
    published = entry.find('published').text
    link = entry.find('link', {'title': 'pdf'})['href'] if entry.find('link', {'title': 'pdf'}) else None

    print(f"Title: {title}\nSummary: {summary}\nPublished: {published}\nLink: {link}\n---")
