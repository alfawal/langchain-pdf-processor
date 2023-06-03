from bs4 import BeautifulSoup
import requests

import markdownify

SOCOTRA_DOCS_URL = "https://docs.socotra.com/production/"
main_page_response = requests.get(SOCOTRA_DOCS_URL)
if main_page_response.status_code != 200:
    raise Exception("Failed to load main page")

main_page_soup = BeautifulSoup(main_page_response.content, "html.parser")
nav_bar_li_elements = main_page_soup.find_all("li", class_="toctree-l1")

pages_urls = {
    SOCOTRA_DOCS_URL + li.find("a")["href"].replace("../", "", 1)
    for li in nav_bar_li_elements
}
if not pages_urls:
    raise Exception("Failed to extract pages urls")

markdown_content = {}
for page_url in pages_urls:
    page_response = requests.get(page_url)
    if page_response.status_code != 200:
        raise Exception(f"Failed to load page {page_url}")

    page_soup = BeautifulSoup(page_response.content, "html.parser")
    div_main = page_soup.find("div", {"role": "main"})
    page_content = div_main.get_text(strip=True)
    page_content = markdownify.markdownify(str(page_content))
    markdown_content[page_url] = page_content

from pprint import pprint as pp

pp(markdown_content)
print("Total pages:", len(pages_urls))
print("Total pages with content:", len(markdown_content))
