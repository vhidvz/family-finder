"""
# python locatefamily.py name='&Clark' family='Rice' phone='|440000000000' location='&UK' email='Clark@email.com'
"""
import sys
import json

import hashlib
import requests
from lxml import html

from collections import OrderedDict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import kwargparse
from .utils import kwpreprocessing


def queryMaker(kwargs: dict) -> str:
    kwargs = OrderedDict(sorted(kwargs.items(), key=lambda x: x[1]))
    string = 'site:locatefamily.com '
    for item in kwargs.values():
        if item.startswith('&') or item.startswith('|'):
            string += item[:1]+'"'+item[1:]+'" '
        else:
            string += item+' '
    return string


def getOptions(kwargs: dict) -> tuple:
    required = {}
    optional = {}
    for key, value in kwargs.items():
        if value.startswith('&'):
            required.update({key: value[1:]})
        elif value.startswith('|'):
            optional.update({key: value[1:]})
        else:
            optional.update({key: value})
    return required, optional


def isTrueInstance(required: dict, optional: dict, **kwargs) -> bool:
    flag = 1
    _conditions = []
    for key, value in required.items():
        if (key == 'name' or key == 'family') and flag:
            _string = kwargs['name'].lower()+' '+kwargs['family'].lower()
            if ('name' in required.keys() and 'family' in required.keys()):
                _conditions.append(
                    required['name'].lower() in _string and required['family'].lower() in _string)
            else:
                _conditions.append(value.lower() in _string)
            flag = 0
        else:
            _conditions.append(value.lower() in kwargs[key].lower())
    _conditions = [all(_conditions)]
    for key, value in optional.items():
        _conditions.append(value.lower() in kwargs[key].lower())
    return any(_conditions)


def getPersons(*args, **kwargs):
    with open('./websites/Info.json') as f:
        info = json.load(f)['locatefamily.com']

    kwargs = kwpreprocessing(info, kwargs)

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # go to the google home page
    driver.get("http://www.google.com")

    # find the element that's name attribute is q (the google search box)
    inputElement = driver.find_element_by_name("q")

    # type in the search
    inputElement.send_keys(queryMaker(kwargs))

    # submit the form (although google automatically searches now without submitting)
    inputElement.submit()
    try:
        # we have to wait for the page to refresh, the last thing that seems to be updated is the title
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#center_col')))

        linksElements = driver.find_elements(by=By.XPATH,
                                             value="//a[contains(@href, 'https://www.locatefamily.com/Street-Lists/')]")

        links = []
        for el in linksElements:
            _href = el.get_attribute('href')
            if not _href.startswith('https://www.google.com') and \
                    not _href.startswith('https://webcache.googleusercontent.com'):
                links.append(_href)
        if links == []:
            driver.quit()
            return 404, json.dumps([])

        # streetAddress = []
        addressLocality = []
        # addressRegion = []
        postalCode = []
        telephone = []
        givenName = []
        familyName = []
        for link in links:
            page = requests.get(link)
            tree = html.fromstring(page.content)

            # streetAddress = tree.xpath('//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "streetAddress")]/text()')
            addressLocality.extend(tree.xpath(
                '//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "addressLocality")]/text()'))
            # addressRegion = tree.xpath('//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "addressRegion")]/text()')
            postalCode.extend(tree.xpath(
                '//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "postalCode")]/text()'))
            telephone.extend(tree.xpath(
                '//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//li[contains(@itemprop, "telephone")]//a/text()'))
            givenName.extend(tree.xpath(
                '//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "givenName")]//text()'))
            familyName.extend(tree.xpath(
                '//div[contains(@itemtype, "https://schema.org/Person")]/ul[contains(@class, "list-inline")]//span[contains(@itemprop, "familyName")]//text()'))

        data = {}
        required, optional = getOptions(kwargs)
        for (location, zipcode, phone, name, family) in zip(
                addressLocality, postalCode, telephone, givenName, familyName):
            _cond = isTrueInstance(required, optional, location=location,
                                   zipcode=zipcode, phone=phone, name=name, family=family)
            if _cond:
                _obj = {
                    'location': location.strip().capitalize(),
                    'zipcode': zipcode.strip(),
                    'phone': phone.strip(),
                    'name': name.strip().capitalize(),
                    'family': family.strip().capitalize()
                }
                hash_object = hashlib.md5("%".join(_obj.values()).encode())
                data.update({hash_object.hexdigest(): _obj})
    finally:
        driver.quit()

    return page.status_code, data


if __name__ == "__main__":
    args = kwargparse(sys.argv)
    status, data = getPersons(**args)
