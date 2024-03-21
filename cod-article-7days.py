import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import os
from ai_search_last7days import scrape_microsoft_blog

# Use the function
search_query = 'generative ai'
scrape_microsoft_blog(search_query)
# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_APIM_ENDPOINT"),
    api_key=os.getenv("AZURE_APIM_API_KEY"),
    api_version="2023-12-01-preview",
)

def summarize_with_gpt(prompt, token_count):
    completion = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=token_count
    )
    return completion.choices[0].message.content.strip()

def render_density_prompt(article, previous_summary=None):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('./density_prompt.jinja2')
    prompt = template.render(article=article, previous_summary=previous_summary)
    # Add an explicit instruction for the model to generate a summary in natural language
    prompt += "\nPlease provide a concise summary in natural language."
    return prompt

def extract_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the title
    title = soup.find('h1').text.strip() if soup.find('h1') else 'Title Not Found'

    # Extract the date
    date_element = soup.find('time')
    date = date_element.text.strip() if date_element else 'Unknown Date'

    # Extract the content
    content_container = soup.find('div', class_='entry-content')
    paragraphs = content_container.find_all('p') if content_container else []
    content = ' '.join([p.text.strip() for p in paragraphs])

    return {
        'title': title,
        'date': date,
        'link': url,
        'content': content
    }

def chunk_content(content, n=5):
    words = content.split()
    chunk_size = max(1, len(words) // n)  # Ensure chunk_size is at least 1
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def chain_of_density_summarization(chunks, token_count=500):
    summaries = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            prompt = render_density_prompt(chunk)  # For the first summary, use only the chunk
        else:
            fused_content = fuse_summaries(summaries[-1], chunk, token_count)
            prompt = render_density_prompt(fused_content, summaries[-1])  # Pass the previous summary and the fused content
        summary = summarize_with_gpt(prompt, token_count)
        summaries.append(summary)
    return summaries[-1]

def fuse_summaries(previous_summary, new_chunk, token_count):
    fused_content = previous_summary + ' ' + new_chunk
    return fused_content[:token_count]

def json_to_markdown(data, output_filename):
    markdown_str = f"# {data['title']}\n\n"
    markdown_str += f"Date: {data['date']}\n\n"
    markdown_str += f"[Link]({data['link']})\n\n"
    markdown_str += f"## Summary\n\n{data['final_summary']}\n"

    with open(output_filename, 'w') as f:
        f.write(markdown_str)

def generate_summary_markdown(articles):
    markdown_str = ""
    for article in articles:
        output = main(article['link'])  # Extract the URL from the dictionary
        markdown_str += f"## [{output['title']}]({output['link']})\n\n"
        markdown_str += f"Date: {output['date']}\n\n"
        markdown_str += f"### Summary\n\n{output['final_summary']}\n\n"
        print(f"Summary for {output['title']}:\n{output['final_summary']}\n")  # Print the summary to the console

    with open('summary_output.md', 'w') as f:
        f.write(markdown_str)

def main(url):
    article = extract_article(url)
    chunks = chunk_content(article['content'])
    if not chunks:
        output = {
            'title': article['title'],
            'date': article['date'],
            'link': article['link'],
            'final_summary': 'No content to summarize'
        }
    else:
        final_summary = chain_of_density_summarization(chunks)
        output = {
            'title': article['title'],
            'date': article['date'],
            'link': article['link'],
            'final_summary': final_summary
        }
    return output

if __name__ == '__main__':
    search_query = 'AI'
    article_urls = scrape_microsoft_blog(search_query)
    generate_summary_markdown(article_urls)