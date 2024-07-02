from collections.abc import Iterator
from datetime import date
from typing import NamedTuple

from bs4 import BeautifulSoup, Comment, Tag
from dateutil.parser import parse as parse_datetime

BASE_URL = "https://www.qwantz.com"

EMPTY_HAPS_DATE_PREFIX = "This comic is from "
EMPTY_HAPS = "I didn't write things down here back then.  Or maybe I did, and they are now LOST FOREVER."
MAILTO_PREFIX = "mailto:ryan@qwantz.com?subject="
ONE_YEAR_AGO = "<p><b>One year ago today:</b>"


class MetadataFromHTML(NamedTuple):
    comic_id: int
    comic_url: str
    date: date
    image_url: str
    title_text: str
    contact_text: str
    archive_text: str
    haps: str | None
    header_texts: list[str]
    image_link_target: str | None


def parse_qwantz_html(html: str) -> Iterator[MetadataFromHTML]:
    soup = BeautifulSoup(html, features="html.parser")
    images = soup.find_all("img", {"class": "comic"})
    comic_url = get_comic_url(soup)
    for image in images:
        yield MetadataFromHTML(
            comic_id=int(comic_url.split("=")[1]),
            comic_url=comic_url,
            date=get_date(soup),
            image_url=get_image_url(image),
            title_text=image.attrs["title"],
            contact_text=get_contact_text(soup),
            archive_text=get_archive_text(soup),
            haps=get_blog_post(soup),
            header_texts=get_header_texts(soup),
            image_link_target=image.parent.attrs["href"] if image.parent.name == "a" else None,
        )


def get_archive_text(soup: BeautifulSoup) -> str:
    rss_comment = soup.find(string=lambda text: isinstance(text, Comment) and '<span class="rss-title">' in text)
    return BeautifulSoup(rss_comment, features="html.parser").span.decode_contents()


def get_contact_text(soup: BeautifulSoup) -> str:
    contact_link = soup.find("a", {"href": lambda href: href.startswith(MAILTO_PREFIX)})
    return contact_link.attrs["href"][len(MAILTO_PREFIX):]


def get_header_texts(soup: BeautifulSoup) -> list[str]:
    headertext_divs = soup.find_all("div", {"class": "headertext"})
    results = []
    for headertext_div in headertext_divs:
        while len(headertext_div.contents) == 1 and isinstance(headertext_div.contents[0], Tag) and headertext_div.contents[0].name in ("p", "center"):
            headertext_div = headertext_div.contents[0]
        inner_html = headertext_div.decode_contents()
        inner_html = inner_html.replace("<p></p>", "").replace("<br/>", "")
        results.append(inner_html)
    return results


def get_blog_post(soup: BeautifulSoup) -> str | None:
    rss_content_spans = soup.find_all("span", {"class": "rss-content"})
    if len(rss_content_spans) > 3:
        main_content = rss_content_spans[3]
        haps = main_content.decode_contents()
        blog_post = haps[:haps.find(ONE_YEAR_AGO)]
        return None if EMPTY_HAPS in blog_post else blog_post


def get_date(soup: BeautifulSoup) -> date:
    date_text = soup.find("title").text.split(" - ")[1]
    return parse_date(date_text)


def get_image_url(image: Tag) -> str:
    image_path = image.attrs["src"]
    if not image_path.startswith("/") and not image_path.startswith("http"):
        image_path = "/" + image_path.replace('//', '/')
    return image_path if image_path.startswith("http") else BASE_URL + image_path


def get_comic_url(soup: BeautifulSoup) -> str:
    return soup.find("meta", {"property": "og:url"}).attrs["content"]


def parse_date(date_text: str) -> date:
    return parse_datetime(date_text).date()
