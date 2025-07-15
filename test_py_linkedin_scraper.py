from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, OnSiteOrRemoteFilters
from linkedin_jobs_scraper.events import Events

def on_data(data):
    print('[DATA]', data)

def on_error(error):
    print('[ERROR]', error)

def on_end():
    print('[END]')

scraper = LinkedinScraper(
    chrome_executable_path=None,  # Custom Chrome executable path (optional)
    chrome_options=None,  # Custom Chrome options (optional)
    headless=True,
    max_workers=1,
    slow_mo=0.5,
    page_load_timeout=40
)

scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='Engineer',
        options=QueryOptions(
            locations=['San Francisco, California, United States'],
            limit=10,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.MID_SENIOR],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE]
            )
        )
    ),
]

scraper.run(queries) 