#!/usr/bin/python3

from urllib.request import urlopen, Request
import requests
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv() # Load environment variables from .env file
api_key = os.getenv('NEWS_API_KEY')

# parameters for TheNewsApi
params = {
            'api_token' : api_key,
            'published_on' : datetime.now().strftime('%Y-%m-%d'),
            'categories' : 'business',
            'locale' : 'us',
            'language' : 'en'
        }

# headers to imitate browsers
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

class News_API:
    '''
    This is a parent class that defines the structure for other API classes.
    
    Attributes:
    Title (str): title of the news.
    Author (str): author of the news.
    Publishers (str): publishers of the news.
    Description (str): description of the news.
    Link (str): link to the news site.
    Date (str): str representation of date converted to date object.
    Image (str): file path to image of publishers or the image url if provided by publishers.
    Data (list): list object that stores each instance data
    '''
    def __init__ (self, Title='', Author='', Publishers='News_API', Description='', Link='', Date='', Image='', Data=[]):
        self.Title = Title
        self.Author = Author
        self.Publishers = Publishers
        self.Description = Description
        self.Link = Link
        self.Date = Date
        self.Image = Image
        self.Data = Data

    def add_data(self, **kwargs):
        '''
        Appends keyword arguments(kwargs) to Data.
        
        Parameters:
        kwargs (key, value pairs): accept any number of arguments.
        
        Returns:
        None
        '''
        new_data = {
            'Title': kwargs.get('Title', self.Title),
            'Author': kwargs.get('Author', self.Author),
            'Publishers': kwargs.get('Publishers', self.Publishers),
            'Description': kwargs.get('Description', self.Description),
            'Link': kwargs.get('Link', self.Link),
            'Image': kwargs.get('Image', self.Image),
            'Date': kwargs.get('Date', self.Date)
        }
        self.Data.append(new_data)

    def get_data(self):
        # Returns Data of the class Instance.
        return self.Data

    def sort_news(self):
        sorted_news = self.get_data()
        return sorted(sorted_news, key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))
            
class NairaMetrics(News_API):
    '''
    Inherits from the News_API and uses it attributes and instance method.
    '''
    def __init__(self, Title='', Author='', Publishers='NairaMetrics', Description='', Link='', Image='', Date=''):
        super().__init__(Title, Author, Publishers, Description, Link, Image, Date)
        self.Image_path = '/images/Nairametrics.jpg'

    def get_market_news(self):
        # Function to get market news from news feed.
        # Returns a list containing news data.
        try:
            html = Request('https://nairametrics.com/category/market-news/feed/', headers=headers) # Parses the data with the headers.
            req = urlopen(html, timeout=10) # Returns the page feed with timeout
            
            bs = BeautifulSoup(req, 'xml') # Uses beautiful soup to parse the feed through xml parser.
            items = bs.select('item') # Select all xml elements with the item tag.

            for item in items:
                # Loops through all item tags
                Title = item.select_one('title').text  # Extract title
                Link = item.select_one('link').text  # Extract link

                _description_html = item.select_one('description').text # Extract desciption html.
                _description_soup = BeautifulSoup(_description_html, 'html.parser').find('p') # Pareses the html and finds the p tag.
                Description = _description_soup.get_text(separator=' ', strip=True)  # Extract description from p tag.

                Date = item.select_one('pubDate').text  # Extract pubDate
                Author = item.find('dc:creator').text.strip() # Extract creator
                # Category = item.select_one('category').text  # Extract all categories

                # Appends extracted elements to the list.
                self.add_data(Title=Title,
                              Author=Author,
                              Publishers=self.Publishers,
                              Description=Description,
                              Link=Link,
                              Image=self.Image_path,
                              Date=Date)

            return self.get_data()
        
        except (HTTPError, URLError) as e:
            # Handle network errors gracefully
            print(f"Error fetching market news: {e}")
            # Return empty list or cached data instead of crashing
            return self.get_data() if self.Data else [
                {
                    'Title': 'Market News Unavailable',
                    'Author': 'System',
                    'Publishers': self.Publishers,
                    'Description': 'Unable to fetch market news at the moment. Please try again later.',
                    'Link': '#',
                    'Image': self.Image_path,
                    'Date': datetime.now().strftime('%Y-%m-%d')
                }
            ]


class ThisDailyLive(News_API):
    '''
    Follows the same principle as NairaMetrics and inherits from News_API.
    '''
    def __init__(self, Title='', Author='', Publishers='ThisDailyLive', Description='', Link='', Image='',Date=''):
        super().__init__(Title, Author, Publishers, Description, Link, Image, Date)
        self.Image_path = '/images/Thisdailylive.jpg'

    def get_market_news(self):
        # Function to get market news from news feed.
        # Returns a list containing news data.
        html = Request('https://www.thisdaylive.com/index.php/category/business/feed/', headers=headers) # Parses the data with the headers.
        req = urlopen(html) # Returns the page feed

        bs = BeautifulSoup(req, 'xml') # Uses beautiful soup to parse the feed through xml parser.
        items = bs.select('item') # Select all xml elements with the item tag.

        for item in items:
            # Loops through all item tags
            Title = item.select_one('title').text # Extract title.
            Link = item.select_one('link').text # Exract link.
            Description = item.select_one('description').text.strip() # Extract description.
            Date = item.select_one('pubDate').text # Extract date.
            Author = item.find('dc:creator').text.strip()  # Extract author.
            
            # Appends extracted elements to the list.
            self.add_data(Title=Title,
                          Author=Author,
                          Publishers=self.Publishers,
                          Description=Description,
                          Link=Link,
                          Image=self.Image_path,
                          Date=Date)

        return self.get_data()

class BusinessDay(News_API):
    '''
    Inherits from News_API.
    '''
    def __init__(self, Title='', Author='', Publishers='BusinessDay', Description='', Link='', Date=''):
        super().__init__(Title, Author, Publishers, Description, Link, Date)
        self.Image_path = '/images/Businessday.png'

    def get_market_news(self):
        # Function to get market news from news feed.
        # Returns a list containing news data.
        html = Request('https://businessday.ng/category/markets/feed/', headers=headers) # Parses the data with the headers.
        req = urlopen(html) # Returns the page feed

        bs = BeautifulSoup(req, 'xml') # Uses beautiful soup to parse the feed through xml parser.
        items = bs.select('item') # Select all xml elements with the item tag

        for item in items:
            # Loops through all item tags
            Title = item.select_one('title').text # Extract text.
            Link = item.select_one('link').text # Extract link.
            _description_html = item.select_one('description').text # Extract description html
            _description_soup = BeautifulSoup(_description_html, 'html.parser').find('img').get('alt')
            # _description_soup stores a alt attr whic is gotten from the img tag,
            # parsed from the description html.
            Description = _description_soup # Extract description.
            Date = item.select_one('pubDate').text # Extract date.
            Author = item.find('dc:creator').text.strip() # Extract author.

            # Appends extracted elements to the list.
            self.add_data(Title=Title,
                          Author=Author,
                          Publishers=self.Publishers,
                          Description=Description,
                          Link=Link,
                          Image=self.Image_path,
                          Date=Date)

        return self.get_data()
            
class USA_NEWS(News_API):
    '''
    Inherits from the News_API class and uses external api
    '''

    def __init__(self, Title='', Author='',Publishers='', Description='', Link='', Image ='', Date=''):
        super().__init__(Title, Author, Publishers, Description, Link, Image, Date)

    def get_market_news(self):
        # Function to get market news from thenewsapi.
        # Returns a list containing news data.
        response = requests.get(f'https://api.thenewsapi.com/v1/news/top', params=params) # Parses news to Parameters.
        response_data = response.json().get('data', {}) # Returns JSON format of data requested.
        
        for item in response_data:
            # Loops through response_data.
            Title = item.get('title') # Extract title
            Link = item.get('url') # Extract link.
            Description = item.get('description') # Extract description.
            Date = datetime.strptime(item.get('published_at'),
                                     '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') # Extract date
            Publishers = item.get('source') # Extract Publishers
            Image = item.get('image_url') # Extract Image url

            # Appends extracted elements to the list.
            self.add_data(Title=Title,
                          Publishers=Publishers,
                          Description=Description,
                          Link=Link,
                          Image=Image,
                          Date=Date)

        return self.get_data()

def search_news(keyword, news_list):
    '''
    searches for news based on keyword passed.
    
    Parameters:
    Keyword (str): input given by the user.
    news_list (list): list of news data.
    
    Returns:
    search_list (list): list of news data that contain the keyword.
    '''
    search_list = list()
    for news in news_list:
        if keyword.strip().lower() in news.get('Title', '').strip().lower():
            search_list.append(news)
    
    return search_list

def group_news(category, news_list):
    '''
    searches for news based on keyword passed.
    
    Parameters:
    Keyword (str): input given by the user.
    news_list (list): list of news data.
    
    Returns:
    search_list (list): list of news data that contain the keyword.
    '''
    group_list = list()
    for news in news_list:
        if category in news.get('Category').lower():
            group_list.append(news)
            
    return group_list