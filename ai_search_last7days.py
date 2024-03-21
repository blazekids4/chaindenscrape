import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_microsoft_blog(search_query):
    base_url = 'https://blogs.microsoft.com/'
    search_url = f'{base_url}?s={search_query.replace(" ", "+")}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(search_url, headers=headers)
    articles_list = []  # List to store articles

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='m-preview-content')

        for article in articles:
            title_element = article.find('h3', class_='c-heading-6')
            title = title_element.text.strip() if title_element else "Title not found"

            link_element = article.find('a', class_='f-post-link')
            link = link_element['href'] if link_element else "Link not found"

            date_element = article.find('time')
            date = date_element['datetime'] if date_element else None

            author_element = article.find('p', class_='c-meta-text').find(string=True, recursive=False)
            author = author_element.strip() if author_element else "Author not found"

            if date:
                article_date = datetime.strptime(date, '%Y-%m-%d').date()
                seven_days_ago = datetime.now().date() - timedelta(days=7)
                if article_date >= seven_days_ago:
                    articles_list.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'author': author
                    })
    else:
        print(f'Failed to fetch the webpage. Status code: {response.status_code}')

    return articles_list  # Return the list of articles

# Example usage:
search_query = 'generative ai'
articles = scrape_microsoft_blog(search_query)
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Date: {article['date']}")
    print(f"Author: {article['author']}\n")
