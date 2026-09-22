import os
import base64
import cloudscraper

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
    }
)


def image_url_to_base64(image_url: str) -> str:
    response = scraper.get(image_url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        "image/webp"
    ).split(";")[0]

    if not content_type.startswith("image/"):
        raise ValueError(
            f"Получен не файл изображения: {content_type}"
        )

    encoded_image = base64.b64encode(
        response.content
    ).decode("utf-8")

    return f"data:{content_type};base64,{encoded_image}"

def describe_map(image_urls: list[str],author_text) -> str:
    content = [
        {
            "type": "input_text",
            "text": (
    "Проанализируй изображения одной Minecraft-постройки. "
    "Составь одно связное и естественное предложение, похожее на запрос пользователя "
    "к генератору Minecraft-построек. "
    "Опиши тип объекта, архитектурный стиль, форму, материалы, цвета и заметные детали. "
    "Не пиши список тегов, не используй двоеточия и точки с запятой. "
    "Не упоминай собственное название карты, проекта, автора или сервера, "
    "даже если они указаны в тексте автора. "
    "Тип объекта, например крепость, арена, мост или дом, указывать можно. "
    "Описывай только видимые особенности, используя текст автора лишь как дополнительную информацию. "
    "Не описывай интерфейс Minecraft. "
    "Максимум 25 слов. "
    f"Текст автора: {author_text}"
)
        }
    ]

    for image_url in image_urls[:6]:
        try:
            base64_image = image_url_to_base64(image_url)

            content.append(
                {
                    "type": "input_image",
                    "image_url": base64_image,
                    "detail": "high",
                }
            )

        except Exception as error:
            print(
                f"Не удалось получить изображение: "
                f"{image_url}\n{error}"
            )

    if len(content) == 1:
        raise ValueError("Не удалось загрузить ни одной картинки")

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    return response.output_text