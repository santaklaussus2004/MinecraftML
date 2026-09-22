import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import cloudscraper
from pathlib import Path
import os
import json
from llm import describe_map
import traceback
import re
import html
import logging
import nbtlib
from nbtlib import serialize_tag

from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG, 
                    filename="log.log",
                    filemode='w',
                    encoding='utf8',
                    format="%(asctime)s - %(levelname)s - %(message)s")
base_url = "https://www.planetminecraft.com/projects/?platform=1&monetization=0&share=schematic&p="
domain = "https://www.planetminecraft.com"

# ...
# create a cloudscraper instance
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
    },
)

# specify the target URL
url = "https://www.planetminecraft.com"


def download_and_put_in_folder(download_link,images,author_text,i,page,link):
    
    folder = Path(f"data/map{page}_{i}")
    folder.mkdir(parents=True,exist_ok=True)
    file_path = folder / "map.schem"
    response = scraper.get(download_link)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type","").lower()
    start = response.content[:200].lstrip().lower()
    
    if (
    "text/html" in content_type
    or start.startswith(b"<!doctype html")
    or start.startswith(b"<html")
):
        raise ValueError(
            f"Вместо .schem получен HTML. "
            f"Content-Type: {content_type}"
            f"Content: {response.content[:100]}"
        )
    logging.info(f"""Получен ответ от скачиваемой ссылки:
                 url = {download_link},
                 Статус = {response.status_code},
                 Длина = {len(response.content)},
                 Контент = {response.content[:20]}
                 """)

    schem = response.content
    with open(file_path,"wb") as file:
        file.write(schem)
    data = nbtlib.load(file_path)

    meta_path = folder / "metadata.json"
    # map_description = describe_map(images,author_text)
    map_description = "Временно нет"
    logging.info(f"Map description is {map_description[:20]}")
    
    metadata = {"images":images, "link":link,"page":page,"map_description":map_description,"download_link":download_link}
    logging.info(f"What is about to be written - len of images {len(images)}\n link of the map {link}\npage {page}\n map description - {map_description[:20]}\ndownload link - {download_link}")
    with open(meta_path,"w",encoding='utf8') as file:
        json.dump(metadata,file,ensure_ascii=False,indent=2)
    
def find_images(soup):
    images = list(soup.select("#light-media > .gSlide > a.rsImg[href]"))
    
    for number, image in enumerate(images,start=1):
        if "youtube.com" in image['href']:
            del images[number-1]
            # continue
    image_urls = []
    for number, image in enumerate(images,start=1):        
        image_url = urljoin(domain,image["href"])
        # print(f"IMAGE URL:{image_url}")
        image_urls.append(image_url)
    return image_urls


def find_real_schematic_link(page_html):
    logging.info("Searching for schematic link")

    match = re.search(
        r'schematic:\s*"([^"]+)"',
        page_html
    )

    if match is None:
        raise ValueError("Schematic link is not found")

    link = html.unescape(match.group(1))

    # Берём расширение без параметров ?...
    extension = Path(urlparse(link).path).suffix.lower()

    if extension != ".schem":
        raise ValueError(
            f"Old schematic format is skipped: {extension}"
        )

    logging.info(" ")

    return link

def find_download_link_and_images(link):
    logging.info(f"Sending request to map {link}")
    response = scraper.get(link)
    response.raise_for_status()
    logging.info(f"""Получен ответ от страницы карты:
                 url = {link},
                 Статус = {response.status_code},
                 Длина = {len(response.content)}
                 """)
    soup = BeautifulSoup(response.text,"html.parser")
    button = soup.select_one(
    'a.branded-download[href*="/download/schematic/"]'
)

    if button is None:
        raise ValueError(
            "Кнопка Download Schematic не найдена"
        )

    author_block = soup.select_one("#r-text-block")
    if author_block is None:
        logging.warning("Author block is not found")
        author_text = ""
    else:
        author_text = author_block.get_text(separator="\n", strip=True)
        logging.info(f"Author block is found - {author_text[:20]}")
    
    images = find_images(soup)
    if not images:
        raise ValueError("Images not found")

    download_link = find_real_schematic_link(response.text)

    return download_link, images,author_text




def gather_links(url):
    logging.info(f"Starting to gather links, sending request to {url}")
    response = scraper.get(url)
    response.raise_for_status()
    logging.info(
        f"Ответ получен: URL={url}, "
        f"status={response.status_code}, "
        f"size={len(response.content)} байт"
    )
    
    soup = BeautifulSoup(response.text,"html.parser")
    # print(f"HTML OF MAP URL {soup}")
    logging.info("Starting to search for links")
    links = soup.select("li.resource.r-data a.r-title[href]")
    if not links:
        raise ValueError(f"Links are not found on url {url}")
    logging.info(f"Links found, number of links:{len(links)}")
    return links



def main():
    logging.info("Starting the program")
    for page in range(1,1000):
        logging.info(f"Analyzing the page {page}")
        url = f"{base_url}{page}"
        
        try:
        
            links = gather_links(url)
            logging.info(f"Number of links on page {page} is {len(links)}")
        except Exception as error:
            logging.exception(f"Error while gathering links on url {url}")
            continue
        for i, link in enumerate(links,start=1):
            logging.info(f"Starting to proccess link number {i},{urljoin(domain,link['href'])}")
            try:
                
                download_link,images,author_text = find_download_link_and_images(urljoin(domain,link['href']))
            
                download_and_put_in_folder(download_link,images,author_text,i,page,urljoin(domain,link['href']))
                print(f"ANALYSING LINK {link} NUMBER {i} ON PAGE {page} IS FINISHED!!!!")
            except Exception as error:
                logging.exception("Неожиданная ошибка")
                print("Тип ошибки:", type(error).__name__)
                print("Сообщение:", error)
                traceback.print_exc()
                continue

main()


            
    