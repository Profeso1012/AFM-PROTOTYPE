# pages/views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .dynamic_api import NairaMetrics, ThisDailyLive, BusinessDay, USA_NEWS, search_news
from datetime import datetime, date
from dateutil import parser
from django.shortcuts import redirect
from django.urls import reverse
from django.http import QueryDict
from urllib.parse import unquote

class HomePageView(ListView):
    '''
    Inherits from django ListView,
    to display home page.
    '''

    template_name = "home.html"
    context_object_name = "top_news" # News identifier in django template.

    def get_queryset(self):
        '''
        Django named function to return data to views
        
        Return:
        returns data to be used on home template
        '''
        nairametrics = NairaMetrics().get_market_news()
        this_daily_live = ThisDailyLive().get_market_news()
        businessday = BusinessDay().get_market_news()
        usa_news = USA_NEWS().get_market_news()
        List_of_news = nairametrics + this_daily_live + businessday + usa_news
        
        NEWS = [] # Storing top news data.
        today = datetime.now().date()
        
        for all_news in List_of_news:
            # Loop through list of news,
            # to get only up to date news.
            news_date = all_news.get('Date') # Get all news date.
            if news_date:
                try:
                    #  Parsing the date string using dateutil.
                    if isinstance(news_date, str):
                        parsed_date = parser.parse(news_date).date()
                    else:
                        parsed_date = news_date.date()

                    # If the date is today, append news.
                    if parsed_date == today:
                        NEWS.append(all_news)
                        print(f"Added news item: {all_news.get('Title')}")  # Debug print
                        
                        if len(NEWS) == 4:
                            break
                except (ValueError, AttributeError) as e:
                    print(f"Error parsing date: {news_date}, Error: {e}")
                    continue
        
        print(f"Final number of news items: {len(NEWS)}")
        return NEWS


class NewsListView(ListView):
    '''
    Class-based view to display paginated news from various sources with search functionality.
    '''
    template_name = "news.html"
    context_object_name = "news"  # Variable name in the template
    paginate_by = 12  # Number of items per page

    def get_queryset(self):
        '''
        Override the method to dynamically fetch and filter news.
        Implements keyword search filtering based on title and description.
        
        Return:
        - List of news items, optionally filtered by search query.
        '''
        # Fetch news from different sources
        nairametrics = NairaMetrics().get_market_news()
        this_daily_live = ThisDailyLive().get_market_news()
        businessday = BusinessDay().get_market_news()
        usa_news = USA_NEWS().get_market_news()
        List_of_news = nairametrics + this_daily_live + businessday + usa_news

        NEWS = []  # List to store today's news

        for all_news in List_of_news:
            # Loop through all news items to filter by today's date
            news_date = all_news.get('Date')  # Get the date of the news item
            if news_date:
                try:
                    # Parse the date string using dateutil
                    if isinstance(news_date, str):
                        parsed_date = parser.parse(news_date).date()
                    else:
                        parsed_date = news_date.date()

                    # Append the news if the date is today
                    #if parsed_date == today:
                    NEWS.append(all_news)

                except (ValueError, AttributeError) as e:
                    print(f"Error parsing date: {news_date}, Error: {e}")
                    continue

        # Get search query from GET parameters
        search_query = self.request.GET.get('q', '').strip()
        
        # Filter by search query if provided
        if search_query:
            search_terms = search_query.lower().split()
            filtered_news = []
            
            for news_item in NEWS:
                # Get title and description
                title = (news_item.get('Title') or '').lower()
                description = (news_item.get('Description') or '').lower()
                publisher = (news_item.get('Publishers') or '').lower()
                
                # Check if any search term matches
                match_found = False
                for term in search_terms:
                    if term in title or term in description or term in publisher:
                        match_found = True
                        break
                
                if match_found:
                    filtered_news.append(news_item)
            
            return filtered_news
        
        return NEWS

    def get_context_data(self, **kwargs):
        '''
        Add search query and filtered news count to context.
        '''
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        context['search_query'] = search_query
        context['news_count'] = len(self.get_queryset())
        return context

class FinancialMarketView(TemplateView):
    template_name = 'financial_market.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        market = kwargs.get('market_type')  # Ensure `market_type` is correctly accessed

        # Set widget configuration based on the market type
        if market == 'stock':
            context['widget_data'] = {
                "width": "100%",
                "height": 550,
                "defaultColumn": "overview",
                "defaultScreen": "most_capitalized",
                "market": "america",  # Required for stocks
                "colorTheme": "light",  # Matches your desired widget
                "showToolbar": True,
                "isTransparent": True,
                "locale": "en",
            }
        elif market == 'crypto':
            context['widget_data'] = {
                "width": "100%",
                "height": 550,
                "defaultColumn": "overview",
                "screener_type": "crypto_mkt",  # Required for crypto
                "displayCurrency": "USD",  # Specific to crypto
                "colorTheme": "light",
                "isTransparent": True,
                "locale": "en",
            }
        else:
            # Handle invalid market types
            context['widget_data'] = None

        return context


class AboutPageView(TemplateView):
    """
    A simple view to render the 'About' page of the application.
    Attributes:
        template_name (str): The name of the HTML template to render.
    """
    template_name = "about.html"

class SearchRedirectView(TemplateView):
    """
    Handles search form submissions and redirects users to the appropriate page
    based on the filter option (e.g., news, stock markets) and search term.
    
    Methods:
        post(request, *args, **kwargs): Processes the POST request and redirects 
        to the appropriate page or returns a rendered template with an error message.
    """
    def post(self, request, *args, **kwargs):
        """
        Processes POST requests for the search functionality.
        
        Redirects users based on the filter option and search term:
        - 'news': Redirects to the news list page with a search query.
        - 'usa-stock-market' or 'nigeria-stock-market': Redirects to the stock profile page with exchange and symbol.
        - Returns an error message if required parameters are missing or invalid.
        
        Args:
            request (HttpRequest): The HTTP request object containing POST data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: A redirect response or a rendered error template.
        """

        filter_option = request.POST.get("filter")
        search_term = request.POST.get("search_term")

        if not filter_option or not search_term:
            return self.render_to_response({"error": "Filter and search term are required."})

        if filter_option == "news":
            return redirect(f"{reverse('news_list')}?q={search_term}")

        if filter_option in ["usa-stock-market", "nigeria-stock-market"]:
            exchange = request.POST.get("exchange")
            symbol = search_term.strip().upper()  # Strip whitespace, ensure uppercase
            
            # Format exchange codes properly
            exchange_mapping = {
                'NSENG': 'NSENG',
                'NYSE': 'NYSE',   # Keep NYSE as is
                'NASDAQ': 'NASDAQ' # Keep NASDAQ as is
            }
            
            # Get the correct exchange code
            exchange = exchange_mapping.get(exchange, exchange)

            if exchange and symbol:
                url = reverse("stock_profile")
                query_params = QueryDict('', mutable=True)
                query_params['exchange'] = exchange
                query_params['symbol'] = symbol
                print(f"DEBUG - Redirecting with: 'exchange': {exchange}, 'symbol': {symbol}")
                return redirect(f"{url}?{query_params.urlencode()}")
            else:
                return self.render_to_response({"error": "Exchange and symbol are required."})

        return self.render_to_response({"error": "Invalid filter option."})


class StockProfileView(TemplateView):
    """
    Displays detailed information about a specific stock profile based on the 
    provided exchange and symbol, or using a tvwidgetsymbol parameter.
    
     Attributes:
        template_name (str): The name of the HTML template to render.

        Methods:
        get(request, *args, **kwargs): Handles GET requests and renders the stock profile page.
    """
    template_name = 'stock_profile.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve stock profile information.

        - Extracts the exchange and symbol from the 'tvwidgetsymbol' parameter if present.
        - Alternatively, retrieves and processes 'exchange' and 'symbol' parameters from the query string.
        - Renders the 'stock_profile.html' template with the extracted data.
        
       
        """
        exchange = None
        symbol = None

        # Handle tvwidgetsymbol
        tvwidgetsymbol = request.GET.get('tvwidgetsymbol')
        if tvwidgetsymbol:
            try:
                tvwidgetsymbol = unquote(tvwidgetsymbol)
                exchange, symbol = tvwidgetsymbol.split(":")
            except ValueError:
                exchange = 'Unknown Exchange'
                symbol = 'Unknown Symbol'
        else:
            # Handle manual search
            exchange = request.GET.get('exchange')
            symbol = request.GET.get('symbol')
            
            # Clean the exchange and symbol
            if exchange:
                exchange = exchange.strip().upper()
                # Map NSENG to NGSE if needed
                if exchange == 'NSENG':
                    exchange = 'NSENG'
            if symbol:
                symbol = symbol.strip().upper()

        context = {
            'exchange': exchange,
            'symbol': symbol,
        }

        print(f"DEBUG - Final context: 'exchange': {exchange}, 'symbol': {symbol}")
        return render(request, self.template_name, context)