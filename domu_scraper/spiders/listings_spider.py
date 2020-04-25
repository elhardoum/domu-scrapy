import scrapy
import json
import re

try:
    from urllib.parse import urljoin
except ImportError:
    def urljoin(base, path):
        return base + path

class ListingsSpider(scrapy.Spider):
    name = "listings"

    def __init__(self, **kwargs):
        if not 'base-url' in kwargs or not kwargs['base-url']:
            self.start_urls = [ 'https://www.domu.com/find/map/markers?sw=41.750076,-87.821484&ne=42.105725,-87.505207&domu_keys=&domu_search=&places_api=&domu_bedrooms_min=&domu_bedrooms_max=&domu_bathrooms_min=&domu_bathrooms_max=&domu_rentalprice_min=&domu_rentalprice_max=&sort=acttime&page=0' ]
        else:
            self.start_urls = [ kwargs['base-url'] ]

    def parse(self, response):
        if 'json' in response.headers['content-type'].decode('utf8'): # this is a REST request
            # extract listings URLs from body and follow pagination
            data = json.loads( response.body.decode('utf8') )

            try:
                listings_res = scrapy.http.HtmlResponse(url=response.url + '.listings', body=data['listings'], encoding='utf-8')

                for url in listings_res.css('.listing-title'):
                    try:
                        yield scrapy.Request(urljoin('https://www.domu.com/', url.attrib['href']), callback=self.parse)
                    except: pass
            except: pass

            try:
                page = int(re.search('page=[0-9]+', response.url).group(0).replace('page=', ''))

                if page >= 0: # attempt to load next API response page
                    yield scrapy.Request(re.sub('(\?|\&)page=[0-9]+', '\g<1>page=%s' % (page+1), response.url), callback=self.parse)
            except Exception as e: print('\n\n', e)

        else: # this is a listing request, extract and yield listing JSON data
            try:
                neighborhood = response.xpath("//div[@class='content']//h2[contains(concat(' ', normalize-space(@class), ' '), 'lb__hoods')]//text()").extract()
            except:
                neighborhood = [None]

            try:
                address = response.xpath("//div[@class='content']//h2[contains(concat(' ', normalize-space(@class), ' '), 'lb__address')]//text()").extract_first()
            except:
                address = None

            try:
                beds = response.xpath("//div[@class='content']//div[@class='lb__attributes']//*[contains(concat(' ', normalize-space(@class), ' '), 'beds')]//text()").extract_first()
                beds = re.sub('\s.+', '', beds) if beds else beds
            except:
                beds = None

            try:
                baths = response.xpath("//div[@class='content']//div[@class='lb__attributes']//*[contains(concat(' ', normalize-space(@class), ' '), 'bath')]//text()").extract_first()
                baths = re.sub('\s.+', '', baths) if baths else baths
            except:
                baths = None

            try:
                rent = response.xpath("//div[@class='content']//*[contains(concat(' ', normalize-space(@class), ' '), 'lb__price')]//text()").extract_first()
            except:
                rent = None

            try:
                date_avail = response.xpath("//div[@class='content']//div[contains(concat(' ', normalize-space(@class), ' '), 'lb__basics')]//*[contains(normalize-space(text()),'Date Available')]/following-sibling::text()").extract_first()
            except:
                date_avail = None

            try:
                landlord_name = response.xpath("//div[@class='content']//div[contains(concat(' ', normalize-space(@class), ' '), 'ref_node-contactname')]//text()").extract_first()
            except:
                landlord_name = None

            try:
                landlord_phone = response.xpath("//div[@class='content']//div[contains(concat(' ', normalize-space(@class), ' '), 'listing-phone-item')]//a/@href").extract_first()
                landlord_phone = landlord_phone.replace('tel:', '') if landlord_phone else landlord_phone
            except:
                landlord_phone = None


            listing = {
                'Neighborhood': ''.join(neighborhood[1::]),
                'Address': address,
                'Beds': beds,
                'Baths': baths,
                'Rent': rent,
                'Date Unit Available': date_avail,
                'Name of Landlord': landlord_name,
                'Phone of Landlord': landlord_phone,
                'Date Ad Posted': '',
                'Link to Ad': response.url,
            }

            for prop in listing:
                listing[prop] = listing[prop].strip() if listing[prop] else ''

            yield listing
 