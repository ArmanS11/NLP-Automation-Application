#write a shebang script to use from cli

import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import spacy
import re
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import dateparser
from typing import Dict, Optional

# Setup for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = ''  # Add your Spreadsheet ID
RANGE_NAME = 'Applications!A1'

# Spacy NLP model
nlp = spacy.load("en_core_web_lg")

# Function to authenticate and return credentials for Google Sheets API
def authenticate():
    creds = None
    # Check if token.pickle file exists (it stores user's access and refresh tokens)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no credentials or they are expired, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def append_data_to_sheet(creds, data):
    """Append data to a Google Sheet."""
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        response = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body={"values": data}
        ).execute()
        
        print(f"{response.get('updates').get('updatedCells')} cells updated.")
    except Exception as e:
        print(f"Error occurred: {e}")

class JobScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": #add your user agent value here
        } 

    async def fetch_html(self, url: str) -> Optional[str]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=10) as response:
                    return await response.text()
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None

    def clean_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def extract_position(self, soup: BeautifulSoup, doc: spacy.tokens.Doc) -> str:
        #def extract_position(self, soup: BeautifulSoup, doc: spacy.tokens.Doc) -> str:
        # First, check for position title in known tags
        for selector in ['h1.job-title', '.job-title', '#position-title']:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.text)
        
        # If no direct match, search for job-related keywords in the entire document
        possible_titles = ['developer', 'engineer', 'manager', 'analyst', 'scientist', 'designer', 'technician', 'architect', 'consultant', 'specialist', 'coordinator', 'director']
        # Make a more comprehensive search for job titles using keyword matching
        doc_text = doc.text.lower()
        for word in possible_titles:
            if word in doc_text:
                return word.capitalize()  # Return the title if a keyword is found

        # Fallback to spaCy named entities (adjusted for possible job-related entities)
        # Consider looking for "WORK_OF_ART", "ORG", and possibly custom job titles
        for ent in doc.ents:
            if ent.label_ in ["WORK_OF_ART", "ORG"] and len(ent.text.split()) < 5:  # Adjust entity length as needed
                return ent.text.capitalize()

        # Detect capitalized job titles (common pattern in job listings)
        capitalized_words = [word for word in doc_text.split() if word.istitle() and len(word) > 3]
        for word in capitalized_words:
            if word.lower() not in possible_titles:
                return word.capitalize()

        return "Unknown Position"



    def extract_company(self, soup: BeautifulSoup, doc: spacy.tokens.Doc) -> str:
        for meta in soup.select('meta[property="og:site_name"], meta[name="company"]'):
            if meta.get('content'):
                return self.clean_text(meta['content'])
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        return orgs[0] if orgs else "Unknown Company"

    def extract_salary(self, text: str) -> Optional[str]:
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*K?)\s*[-–—]\s*\$(\d{1,3}(?:,\d{3})*K?)',
            r'(?:USD|CAD|)\s*(\d+[kK])\s*-\s*(\d+[kK])',
            r'(?:salary|compensation).{1,20}?\$(\d+[\d,.]*).{1,20}?\$(\d+[\d,.]*)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}-{match.group(2)}"
        return None

    def extract_dates(self, text: str) -> Dict[str, datetime]:
        dates = {}
        for ent in nlp(text).ents:
            if ent.label_ == "DATE":
                parsed = dateparser.parse(ent.text)
                if parsed:
                    if not dates.get('posted'):
                        dates['posted'] = parsed
                    else:
                        dates['applied'] = parsed
        return dates

    async def analyze_job(self, url: str) -> Dict[str, Optional[str]]:
        html = await self.fetch_html(url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'lxml')
        main_text = self.clean_text(soup.get_text())
        doc = nlp(main_text)

        dates = self.extract_dates(main_text)

        return {
            "Position": self.extract_position(soup, doc),
            "Company": self.extract_company(soup, doc),
            "Industry": "Technology",
            "Role": "Full-time",
            "Link": url,
            "Status": "Waiting",
            "Location": "Remote",  # Default, modify as needed
            "Date Posted": dates.get('posted', datetime.now()).strftime('%Y-%m-%d'),
            "Date Applied": datetime.now().strftime('%Y-%m-%d'),
            "Salary Range": self.extract_salary(main_text),
            "Cover Letter": "cover letter" in main_text.lower(),
            "Résumé upload": bool(re.search(r"resume|cv", main_text, re.I)),
            "Résumé Form": False,
        }

# Combined main function to use both scraping and Google Sheets integration
async def main():
    creds = authenticate()  # Authenticate for Google Sheets
    scraper = JobScraper()

    job_url = str(input("Link: "))  # Get the job URL
    job_data = await scraper.analyze_job(job_url)  # Scrape job details

    if job_data:
        # Append job data to Google Sheet
        append_data_to_sheet(creds, [list(job_data.values())])
        print(f"{job_data} has been appended to the Google Sheet.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
