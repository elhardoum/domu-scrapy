# Scraping domu.com listings

This project requires will use Scrapy framework to scrap all listings in domu.com given a start URL to work with.

### Install

Your machine will have Python installed. The only module required here is `scrapy`, so install virtual environment and activate it, or just install the project on the global namespace:

```bash
pip install scrapy
```

### Running the scraper

First make sure you are in the project folder.

Next, you can run the following command to start the scrapers:

```bash
scrapy crawl listings -o listings.csv
```
- `listings` is the name of the spider
- `-o` flag allows us to pass an output file
- `listings.csv` this is the value for `-o` flag, so we'll have the listings saved in CSV format into `./listings.csv`

Now just let the scrapers work and check the CSV file later, it'll keep adding listings.

### Common issues

domu.com will identify bots and block excessive requests throttling your IP. So in this case I've modified the project settings file (`domu_scraper/settings.py`) to include throttling settings and add delays between page downloads making 1 page download every 2 seconds:

```python
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 15
```