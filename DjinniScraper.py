import requests
from bs4 import BeautifulSoup
from job_posting import JobPosting
import re

class DjinniScrapper:
    """
    Web Scraper for the Djinni website. Parses job postings for a specified specialisation.
    """
    BASE_URL = 'https://djinni.co'
    JOB_URL_FORMAT = f'{BASE_URL}/jobs/?primary_keyword={{}}&page={{}}'
    EXCEPTIONAL_SPECIALISATIONS = {'Front-End(JavaScript)': 'JavaScript', 'C#/.NET': '.NET', 'C++': 'C%2B%2B'}

    def __init__(self, specialisation):
        """
        Initializes the DjinniScrapper with a specified specialisation.
        Args:
            specialisation (str): The job specialisation to scrape.
        """
        self.specialisation = self.EXCEPTIONAL_SPECIALISATIONS.get(specialisation, specialisation)

    def search_jobs(self):
        """
        Searches for jobs based on the specified specialisation.
        Yields:
            JobPosting: An object containing job posting information.
        """
        with requests.Session() as session:
            for page in self._get_pagination_elements(session):
                for job in self._get_job_postings(session, page):
                    yield job

    def _get_pagination_elements(self, session):
        """
        Retrieves pagination elements from the Djinni job listings page.
        Args:
            session (requests.Session): The session object for making HTTP requests.
        Yields:
            int: Page numbers for job listings.
        """
        url = self.JOB_URL_FORMAT.format(self.specialisation, 1)
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            pagination = soup.find('ul', class_='pagination pagination_with_numbers')
            max_page = int(pagination.find_all('li', class_='page-item')[-2].text)
            for page in range(1, max_page + 1):
                yield page
        except requests.exceptions.RequestException as e:
            print(f"Error while scraping Djinni pagination: {e}")

    def _get_job_postings(self, session, page):
        """
        Retrieves job postings from a specific page.
        Args:
            session (requests.Session): The session object for making HTTP requests.
            page (int): Page number to scrape.
        Yields:
            JobPosting: An object containing job posting information.
        """
        url = self.JOB_URL_FORMAT.format(self.specialisation, page)
        try:
            response = session.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = soup.find_all('li', class_='list-jobs__item job-list__item')
            for job in jobs:
                yield self._parse_job_posting(job)
        except requests.exceptions.RequestException as e:
            print(f"Error while scraping Djinni job postings: {e}")

    def _parse_job_posting(self, job_element):
        """
        Parses a single job posting element.
        Args:
            job_element (bs4.element.Tag): The BeautifulSoup Tag object representing a job posting.
        Returns:
            JobPosting: An object containing job posting information.
        """
        job_header = job_element.find('header')
        job_title = job_header.find('div', class_='job-list-item__title').a.text.strip()
        job_company_name = job_header.find('a', class_='mr-2').text.strip()
        job_type, job_experience = self._extract_job_details(job_header)
        job_salary = job_header.find('span', class_='public-salary-item')
        job_salary = job_salary.text.strip() if job_salary else None
        job_link = f"{self.BASE_URL}{job_header.find('a', class_='job-list-item__link')['href']}"

        return JobPosting(title=job_title, company=job_company_name, specialisation=self.specialisation,
                          experience=job_experience, location=job_type, salary=job_salary, link=job_link)

    def _extract_job_details(self, job_header):
        """
        Extracts job type and experience requirements from a job header.
        Args:
            job_header (bs4.element.Tag): The BeautifulSoup Tag object representing a job header.
        Returns:
            tuple: A tuple containing job type and job experience.
        """
        job_types = ["Remote", "Office", "Hybrid"]
        job_type = "Job type not found"
        experience_pattern = re.compile(r'(\d+ years of experience|\d+ years|experience)')
        experience = "Experience not found"
        spans = job_header.find_all("span", class_="nobr")

        for span in spans:
            text = span.text.strip()
            if any(job_type_keyword in text for job_type_keyword in job_types):
                job_type = text
            elif experience_pattern.search(text):
                experience = text

        return job_type, experience
