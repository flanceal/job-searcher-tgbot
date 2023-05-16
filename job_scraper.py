import requests
from bs4 import BeautifulSoup


class JobPosting:
    """
    Have all the job necessary attributes
    """
    def __init__(self, title, experience, company, location, link, salary=None):
        self.title = title
        self.experience = experience
        self.company = company
        self.location = location
        self.salary = salary
        self.link = link


class DjinniScrapper:
    """
    Web Scraper for site 'Djinni' that makes reusable TCP request to 'Djinni' site
    and parses all the jobs for specific specialisation
    """
    djinni_url = 'https://djinni.co/jobs/?primary_keyword={}&page={}'

    # set specialisation to search and create reusable TCP request
    def __init__(self, specialisation):
        self.specialisation = specialisation
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })

    # Close the session after parsing all the jobs
    def __del__(self):
        self.session.close()

    # Search for jobs using _get_page and _get_jobs function
    def search_jobs(self):
        for page in self._get_pages():
            for job in self._get_jobs(page):
                yield job

    # generator function that gets max number of pages
    def _get_pages(self):
        url = self.djinni_url.format(self.specialisation, 1)
        html_text = self.session.get(url, timeout=20).text
        soup = BeautifulSoup(html_text, 'lxml')
        pagination = soup.find('ul', class_='pagination pagination_with_numbers')
        max_page = int(pagination.find_all('li', class_='page-item')[-2].text)
        for page in range(1, max_page + 1):
            yield page

    # parse jobs from the site for a specific attributes
    def _get_jobs(self, page):
        url = self.djinni_url.format(self.specialisation, page)
        html_text = self.session.get(url, timeout=5).text
        soup = BeautifulSoup(html_text, 'lxml')
        jobs = soup.find_all('li', class_='list-jobs__item list__item')
        concise_mapping = {"Тільки віддалено": 'Remote',
                           "Тільки офіс": "On-site",
                           "Гібридна робота": "Hybrid",
                           "Office/Remote на ваш вибір": "Both"}
        for job in jobs:
            # Extract job information
            job_title = job.find('div', 'list-jobs__title list__title order-1').text.strip()
            job_company_name = job.find('div', class_='list-jobs__details__info').find('a').text.strip()
            job_remote_onsite = concise_mapping.get(job.find_all('nobr', class_='ml-1')[-1].text.strip())
            job_experience = job.find('div', class_='list-jobs__details__info').text.split()[-5]
            job_salary = job.find('span', class_='public-salary-item')
            if job_salary:
                job_salary = job_salary.text.strip()
            job_link = 'https://djinni.co' + job.find('a', class_='profile')['href']
            # create and yield JobPosting object
            yield JobPosting(job_title, job_experience, job_company_name, job_remote_onsite, job_link, job_salary)