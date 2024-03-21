# Chain Density Scrape

This project is a Python-based web scraper and summarizer that targets Microsoft's blog posts about AI. It uses the BeautifulSoup library to scrape the blog posts, and the Azure OpenAI API to generate summaries of the articles.

## Project Structure

- `.env`: Contains environment variables, including the Azure OpenAI API key.
- `ai_search_last7days.py`: Contains the function `scrape_microsoft_blog` which is used to scrape Microsoft's blog posts.
- `cod-article-7days.py`: The main script that uses the functions from `ai_search_last7days.py` and other helper functions to scrape, summarize, and output the summaries in markdown format.
- `density_prompt.jinja2`: A Jinja2 template used in the summarization process.
- `summary_output.md`: The output file containing the summaries of the blog posts in markdown format.
- `urls-html-reference.md`: A markdown file containing HTML references to the blog posts.

## How to Run

1. Set up your environment variables in the `.env` file.
2. Run the `cod-article-7days.py` script with a search query as an argument.

```sh
python cod-article-7days.py 'AI'