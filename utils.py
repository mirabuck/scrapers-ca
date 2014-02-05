# coding: utf-8
import re

import lxml.html
from scrapelib import urlopen

from pupa.scrape import Scraper, Jurisdiction, Legislator
from pupa.models.person import Person

CONTACT_DETAIL_TYPE_MAP = {
  'Address': 'address',
  'bb': 'cell',
  'bus': 'voice',
  'Bus': 'voice',
  'Bus.': 'voice',
  'Business': 'voice',
  'Cell': 'cell',
  'Cell Phone': 'cell',
  'Email': 'email',
  'Fax': 'fax',
  'Home': 'voice',
  'Home Phone': 'voice',
  'Home Phone*': 'voice',
  'Office': 'voice',
  'ph': 'voice',
  u'ph\xc2': 'voice',
  'Phone': 'voice',
  'Res': 'voice',
  'Res/Bus': 'voice',
  'Residence': 'voice',
  'Voice Mail': 'voice',
}
# In Newmarket, for example, there are both "Phone" and "Business" numbers.
CONTACT_DETAIL_NOTE_MAP = {
  'Address': 'legislature',
  'bb': 'legislature',
  'bus': 'office',
  'Bus': 'office',
  'Bus.': 'office',
  'Business': 'office',
  'Cell': 'legislature',
  'Cell Phone': 'legislature',
  'Email': None,
  'Fax': 'legislature',
  'Home': 'residence',
  'Home Phone': 'residence',
  'Home Phone*': 'residence',
  'ph': 'legislature',
  u'ph\xc2': 'legislature',
  'Phone': 'legislature',
  'Office': 'legislature',
  'Res': 'residence',
  'Res/Bus': 'office',
  'Residence': 'residence',
  'Voice Mail': 'legislature',
}


class CanadianJurisdiction(Jurisdiction):
  session_details = {
    'N/A': {
      '_scraped_name': 'N/A',
    }
  }
  terms = [
    {
      'name': 'N/A',
      'sessions': ['N/A'],
      'start_year': 1900,
      'end_year': 2030,
    }
  ]

  def __init__(self):
    for scraper_type in ('bills', 'events', 'people', 'speeches', 'votes'):
      try:
        __import__(self.__module__ + '.' + scraper_type)
      except ImportError:
        pass
      else:
        self.provides.append(scraper_type)

  def get_scraper(self, term, session, scraper_type):
    if scraper_type in self.provides:
      class_name = self.__class__.__name__ + {
        'bills': 'Bill',
        'events': 'Event',
        'people': 'Person',
        'speeches': 'Speech',
        'votes': 'Vote',
      }[scraper_type] + 'Scraper'
      return getattr(__import__(self.__module__ + '.' + scraper_type, fromlist=[class_name]), class_name)

  def scrape_session_list(self):
    return ['N/A']


class CanadianLegislator(Legislator):
    def __init__(self, name, post_id, **kwargs):
      super(CanadianLegislator, self).__init__(clean_name(name), clean_post_id(post_id), **kwargs)

    def add_link(self, url, note=None):
        if url.startswith('www.'):
          url = 'http://%s' % url
        if re.match('\A@[A-Za-z]+\Z', url):
          url = 'https://twitter.com/%s' % url[1:]
        self.links.append({"note": note, "url": url})

    def add_contact(self, type, value, note):
      if type in CONTACT_DETAIL_TYPE_MAP:
        type = CONTACT_DETAIL_TYPE_MAP[type]
      if note in CONTACT_DETAIL_NOTE_MAP:
        note = CONTACT_DETAIL_NOTE_MAP[note]
      if type in ('text', 'voice', 'fax', 'cell', 'video', 'pager'):
        value = clean_telephone_number(value)
      self._contact_details.append({'type': type, 'value': value, 'note': note})


# Removes _is_legislator flag, _contact_details and _role. Used by aggregations.
# @see https://github.com/opencivicdata/pupa/blob/master/pupa/scrape/helpers.py
class AggregationLegislator(Person):
  __slots__ = ('post_id', 'party', 'chamber')

  def __init__(self, name, post_id, party=None, chamber=None, **kwargs):
    super(AggregationLegislator, self).__init__(clean_name(name), **kwargs)
    self.post_id = clean_post_id(post_id)
    self.party = party
    self.chamber = chamber


def clean_name(s):
  return s.replace(u' ', ' ').replace(u'’', "'").replace('Mayor', '').replace('Councillor', '').strip()

def clean_post_id(s):
  return s.replace(u' ', ' ').replace(u'’', "'").strip() # non-breaking space

# @see http://www.noslangues-ourlanguages.gc.ca/bien-well/fra-eng/typographie-typography/telephone-eng.html
def clean_telephone_number(s):
  splits = re.split(r'[\s-](?:x|ext\.?|poste)[\s-]?(?=\b|\d)', s, flags=re.IGNORECASE)
  digits = re.sub(r'\D', '', splits[0])

  if len(digits) == 10:
    digits = '1' + digits

  if len(digits) == 11 and digits[0] == '1' and len(splits) <= 2:
    digits = re.sub(r'\A(\d)(\d{3})(\d{3})(\d{4})\Z', r'\1-\2-\3-\4', digits)
    if len(splits) == 2:
      return '%s x%s' % (digits, splits[1])
    else:
      return digits
  else:
    return s

def lxmlize(url, encoding='utf-8'):
  entry = urlopen(url).encode(encoding)
  page = lxml.html.fromstring(entry)
  meta = page.xpath('//meta[@http-equiv="refresh"]')
  if meta:
    _, url = meta[0].attrib['content'].split('=', 1)
    return lxmlize(url, encoding)
  else:
    page.make_links_absolute(url)
    return page
