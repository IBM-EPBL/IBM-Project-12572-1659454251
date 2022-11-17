import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def extract(url, page):
    url = url+str(page)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def transform(soup):
    jobs_list = []
    divs = soup.find_all('div', class_='job_seen_beacon')
    for item in divs:
        title = item.find('h2').find_all('span')[-1].text
        company = item.find('div', class_='heading6 company_location tapItem-gutter companyInfo')
        company_name = company.find('span', class_='companyName').text
        company_location = company.find('div', class_='companyLocation').text
        company_salary = item.find('div', class_='heading6 tapItem-gutter metadataContainer noJEMChips salaryOnly')
        company_salary = company_salary.text if company_salary else 'Not Provided'
        job_link = item.find('div', class_='more_links').find_all('span', class_='mat')[1].find('a', href=True)
        jk = re.search('fromjk=(.*)&amp;from', str(job_link)).group()[7:-9]
        job_soup = extract('https://uk.indeed.com/viewjob?jk=', jk)
        job_description = job_soup.find('div', id='jobDescriptionText', class_='jobsearch-jobDescriptionText')
        responsibilities = job_description(text=lambda t: "looking for" in t)
        experiences = job_description(text=lambda t: ("experience" in t) or ("Experience" in t))
        posted_time = job_soup.find('div', class_='jobsearch-JobMetadataFooter').find_all('div')[1].text
        tech_list = ['Python', 'Java', 'Javascript', 'Node', 'C', 'C++', 'AWS', 'SQL', 'Ruby',
                     'HTML', 'Android', 'Spark', 'React', 'Apache', '.NET', 'Perl'
                     'Kafka', 'Kubernetes', 'Azure', 'Kotlin', 'CSS', 'PHP']
        tech_stack = []
        for tech in tech_list:
            if job_description(text=lambda t: tech in t):
                tech_stack.append(tech)

        job = {'Title': title,
               'Employer': company_name,
               'Location': company_location,
               'Salary': company_salary,
               'Data Posted': posted_time,
               'Tech Stack': ' '.join(tech_stack),
               'Description': job_description.text[:500]+'...',
               'Responsibilities': responsibilities,
               'Experience': experiences,
               'Learn More': 'https://uk.indeed.com/viewjob?jk=' + str(jk)
               }

        jobs_list.append(job)
    return jobs_list


jobs_list = []
for i in range(1, 60, 15):
    jobs = extract('https://uk.indeed.com/jobs?q=developer&l=London,%20Greater%20London&start=', i)
    jobs_list += transform(jobs)
    time.sleep(50)

df = pd.DataFrame(jobs_list)
df.to_csv('jobs.csv')

