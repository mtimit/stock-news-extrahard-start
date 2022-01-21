import requests
from difflib import SequenceMatcher
from itertools import islice
from datetime import datetime

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
SYMBOL_STONKS = ""
alphavantage_api_key = "S5PT48UIM02U7CCK"
newsapi_key = "79cab1023f284a69ac3df02f68f82c02"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# Get data from alphavantage api
parameters_alphavantage = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": alphavantage_api_key
}
response_alpha = requests.get(url="https://www.alphavantage.co/query",
                              params=parameters_alphavantage)
# Editing data and extracting last and day before info on stock price
data_alphavantage = islice(response_alpha.json()["Time Series (60min)"].items(), 17)
last_data = islice(data_alphavantage, 1)
first_data = islice(data_alphavantage, 15, 16)

temp_dict1 = list({key: value for (key, value) in last_data}.values())
temp_dict2 = list({key: value for (key, value) in first_data}.values())

last_price = float(temp_dict1[0]["1. open"])
first_price = float(temp_dict2[0]["1. open"])

# Condition if 5% delta =>
delta = (last_price - first_price) / first_price


## STEP 2: Use https://newsapi.org
# Define similarity, if true pop extra
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


news_dict = {}


def get_news():
    # Get news from newsapi
    parameters_news = {
        "q": COMPANY_NAME,
        "from": datetime.now().strftime("%Y-%m-%d"),
        "sortBy": "popularity",
        "pageSize": 10,
        "apiKey": newsapi_key
    }
    response_news = requests.get(url="https://newsapi.org/v2/everything",
                                 params=parameters_news).json()
    response_news_list = response_news["articles"]
    # Need to get 3 different articles
    for i in range(1, len(response_news_list) - 2):
        if similar(response_news_list[i - 1]["title"], response_news_list[i]["title"]) > 0.8:
            response_news_list.pop(i)
            print(f"i poped {i}")
        print(response_news_list[i]["title"])

    for i in range(3):
        news_dict[response_news_list[i]["title"]] = response_news_list[i]["description"]
    print(news_dict)


if delta > 0.05:
    SYMBOL_STONKS = "🔺"
    get_news()
elif delta < 0.05:
    SYMBOL_STONKS = "🔻"
    get_news()


# STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.
def send_sms():
    for k, v in news_dict.items():
        print(f"{STOCK}: {SYMBOL_STONKS}{'%.00f' % (delta * 100)} \n Headline: {k} \n Brief: {v}")


# Optional: Format the SMS message like this:
"""TSLA: 🔺2% Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. Brief: We at Insider Monkey have 
gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings 
show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash. 
or "TSLA: 🔻5% Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. Brief: We at Insider Monkey 
have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F 
filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus 
market crash. """
