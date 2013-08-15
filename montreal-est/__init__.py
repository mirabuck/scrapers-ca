from pupa.scrape import Jurisdiction

# from .events import TorontoEventScraper
from .people import Montreal_EstPersonScraper
# from .votes import TorontoVoteScraper
from utils import lxmlize

import re

class Montreal_Est(Jurisdiction):
  jurisdiction_id = 'ca-qc-montreal-est'
  geographic_code = 3524002
  def get_metadata(self):
    return {
      'name': 'Montreal-Est',
      'legislature_name': 'Montreal-Est City Council',
      'legislature_url': 'http://ville.montreal-est.qc.ca/site2/index.php?option=com_content&view=article&id=12&Itemid=59',
      'terms': [{
        'name': '2010-2014',
        'sessions': ['2010-2014'],
        'start_year': 2010,
        'end_year': 2014,
      }],
      'provides': ['people'],
      'parties': [],
      'session_details': {
        '2010-2014': {
          '_scraped_name': '2010-2014',
        }
      },
      'feature_flags': [],
      # '_ignored_scraped_sessions': ['2006-2010'],
    }

  def get_scraper(self, term, session, scraper_type):
    # if scraper_type == 'events':
    #     return TorontoEventScraper
    if scraper_type == 'people':
        return Montreal_EstPersonScraper
    # if scraper_type == 'votes':
    #     return TorontoVoteScraper

  def scrape_session_list(self):
    return ['2010-2014']
    