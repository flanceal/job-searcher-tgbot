import requests
from bs4 import BeautifulSoup
from job_posting import JobPosting


class DjinniScrapper:
    """
    Web Scraper for site 'Djinni' that makes reusable TCP request to 'Djinni' site
    and parses all the jobs for specific specialisation
    """
    djinni_url = 'https://djinni.co/jobs/?primary_keyword={}&page={}'
    exceptional_specialisations = {''}

    # set specialisation to search and create reusable TCP request
    def __init__(self, specialisation):
        self.specialisation = specialisation
        self.session = requests.Session()

    # Search for jobs using _get_page and _get_jobs function
    def search_jobs(self):
        with requests.Session() as session:
            for page in self._get_pagination_elements():
                for job in self._get_job_postings(page):
                    yield job

    # generator function that gets max number of pages
    def _get_pagination_elements(self):
        url = self.djinni_url.format(self.specialisation, 1)
        try:
            html_text = self.session.get(url, timeout=20).text
            soup = BeautifulSoup(html_text, 'lxml')
            pagination_element = soup.find('ul', class_='pagination pagination_with_numbers')
            max_page = int(pagination_element.find_all('li', class_='page-item')[-2].text)
            for page in range(1, max_page + 1):
                yield page
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, AttributeError) as e:
            print(f"An error occurred while trying to scrape Djinni: {e}")

    def _get_job_postings(self, page):
        url = self.djinni_url.format(self.specialisation, page)
        try:
            html_text = self.session.get(url, timeout=5).text
            soup = BeautifulSoup(html_text, 'lxml')
            jobs = soup.find_all('li', class_='list-jobs__item list__item')
            concise_mapping = {"Тільки віддалено": 'Remote',
                               "Тільки офіс": "On-site",
                               "Гібридна робота": "Hybrid",
                               "Office/Remote на ваш вибір": "Both"}
            for job in jobs:
                # Extract job information
                # title
                job_title = job.find('div', 'list-jobs__title list__title order-1').find('span').text.strip()

                # company name
                job_company_name = job.find('div', class_='list-jobs__details__info').find('a').text.strip()

                # remote or on-site
                job_remote_onsite = concise_mapping.get(job.find_all('nobr', class_='ml-1')[-1].text.strip())

                # experience
                job_experience = None
                nobr_list = job.find('div', class_='list-jobs__details__info').find_all('nobr')
                for nobr in nobr_list:
                    if 'досвіду' in nobr.text.strip():
                        job_experience = nobr.text.strip()[2:]
                        break

                # salary
                job_salary = job.find('span', class_='public-salary-item')
                if job_salary:
                    job_salary = job_salary.text.strip()
                job_link = 'https://djinni.co' + job.find('a', class_='profile')['href']
                # create and yield JobPosting object
                yield JobPosting(job_title, self.specialisation,
                                 job_experience, job_company_name, job_remote_onsite, job_link, job_salary)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, AttributeError) as e:
            print(f"An error occurred while trying to scrape Djinni: {e}")