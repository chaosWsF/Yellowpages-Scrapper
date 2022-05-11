#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html
import unicodecsv as csv


def parse_listing(url):
    """
    Function to process yellowpage listing page
    : param url:
    """
    print("retrieving ", url)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.yellowpages.ca',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }
    # Adding retries
    for retry in range(10):
        try:
            response = requests.get(url, verify=False, headers=headers)
            print("parsing page")
            if response.status_code == 200:
                parser = html.fromstring(response.text)
                # making links absolute
                base_url = "https://www.yellowpages.ca"
                parser.make_links_absolute(base_url)

                XPATH_LISTINGS = "//div[@class='resultList jsResultsList jsMLRContainer']//div[@class='listing__content__wrap--flexed jsGoToMp']"
                listings = parser.xpath(XPATH_LISTINGS)
                scraped_results = []

                for results in listings:
                    XPATH_BUSINESS_NAME = ".//a[@class='listing__name--link listing__link jsListingName']//text()"
                    XPATH_BUSSINESS_PAGE = ".//a[@class='listing__name--link listing__link jsListingName']//@href"
                    XPATH_TELEPHONE = ".//a[@class='mlr__item__cta jsMlrMenu']//@data-phone"
                    XPATH_STREET = ".//span[@itemprop='streetAddress']//text()"
                    XPATH_LOCALITY = ".//span[@itemprop='addressLocality']//text()"
                    XPATH_REGION = ".//span[@itemprop='addressRegion']//text()"
                    XPATH_ZIP_CODE = ".//span[@itemprop='postalCode']//text()"
                    XPATH_CATEGORIES = ".//div[@class='listing__captext']//text()"
                    XPATH_WEBSITE = ".//a[@class='mlr__item__cta']//@href"
                    XPATH_RATING = ".//div[@class='listing__rating ratingWarp']//span//@data-rating"

                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
                    raw_business_telephone = results.xpath(XPATH_TELEPHONE)
                    raw_street = results.xpath(XPATH_STREET)
                    raw_locality = results.xpath(XPATH_LOCALITY)
                    raw_region = results.xpath(XPATH_REGION)
                    raw_zip_code = results.xpath(XPATH_ZIP_CODE)
                    raw_categories = results.xpath(XPATH_CATEGORIES)
                    raw_website = results.xpath(XPATH_WEBSITE)
                    raw_rating = results.xpath(XPATH_RATING)

                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                    telephone = ','.join(raw_business_telephone).strip() if raw_business_telephone else None
                    street = ''.join(raw_street).strip() if raw_street else None
                    locality = ''.join(raw_locality).strip() if raw_locality else None
                    region = ''.join(raw_region).strip() if raw_region else None
                    zipcode = ''.join(raw_zip_code).strip() if raw_zip_code else None
                    category = ','.join(raw_categories).strip() if raw_categories else None
                    website = ''.join(raw_website).strip() if raw_website else None
                    rating = ''.join(raw_rating).replace("rating", "").strip() if raw_rating else None

                    business_details = {
                        'business_name': business_name,
                        'business_page': business_page,
                        'telephone': telephone,
                        'street': street,
                        'locality': locality,
                        'region': region,
                        'zipcode': zipcode,
                        'category': category,
                        'website': website,
                        'rating': rating,
                        'listing_url': response.url
                    }
                    scraped_results.append(business_details)

                return scraped_results

            elif response.status_code == 404:    # no need to retry for non existing page
                print("Could not find a location matching")
                return []
            else:
                print(f"Failed to process page, response error, retry {retry+1}")

        except:
            print("Failed to process page")
            return []


def helper(field: str) -> str:
        """
        convert the field into an appropriate form
        """
        tmp = s.strip().split(' ')
        return '+'.join(tmp)


if __name__ == "__main__":

    keyword = 'restaurants'
    place = 'Edmonton AB'
    pagenum = 1

    url = f"https://www.yellowpages.ca/search/si/{pagenum}/{helper(keyword)}/{helper(place)}"
    scraped_data = parse_listing(url)

    if scraped_data:
        print("Writing scraped data to %s-%s-yellowpages-scraped-data.csv" % (keyword, place))
        # TODO: change to JSON format
        with open('%s-%s-yellowpages-scraped-data.csv' % (keyword, place), 'wb') as csvfile:
            fieldnames = [
                'business_name',
                'business_page',  
                'telephone', 
                'street', 
                'locality', 
                'region', 
                'zipcode', 
                'category', 
                'website', 
                'rating',
                'listing_url'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
