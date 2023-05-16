class JobPosting:
    """
    Have all the job necessary attributes
    """
    def __init__(self, title, specialisation, experience, company, location, link, salary=None):
        self.title = title
        self.specialisation = specialisation
        self.experience = experience
        self.company = company
        self.location = location
        self.salary = salary
        self.link = link
