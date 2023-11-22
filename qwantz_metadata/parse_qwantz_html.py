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
    header_text: str | None
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
            haps=get_haps(soup),
            header_text=get_header_text(soup),
            image_link_target=image.parent.attrs["href"] if image.parent.name == "a" else None,
        )


def get_archive_text(soup: BeautifulSoup) -> str:
    rss_comment = soup.find(string=lambda text: isinstance(text, Comment) and '<span class="rss-title">' in text)
    return BeautifulSoup(rss_comment, features="html.parser").span.decode_contents()


def get_contact_text(soup: BeautifulSoup) -> str:
    contact_link = soup.find("a", {"href": lambda href: href.startswith(MAILTO_PREFIX)})
    return contact_link.attrs["href"][len(MAILTO_PREFIX):]


def get_header_text(soup: BeautifulSoup) -> str | None:
    headertext_div = soup.find("div", {"class": "headertext"})
    if headertext_div:
        while len(headertext_div.contents) == 1 and isinstance(headertext_div.contents[0], Tag) and headertext_div.contents[0].name in ("p", "center"):
            headertext_div = headertext_div.contents[0]
        inner_html = headertext_div.decode_contents()
        inner_html = inner_html.replace("<p></p>", "").replace("<br/>", "")
        return inner_html


def get_haps(soup: BeautifulSoup) -> str | None:
    blogpost = get_blogpost(soup)
    if len(blogpost.contents) > 3:
        main_content = blogpost.contents[3]
        haps = main_content.decode_contents()
        return haps[:haps.find(ONE_YEAR_AGO)]


def get_date(soup: BeautifulSoup) -> date:
    blogpost = get_blogpost(soup)
    if len(blogpost.contents) > 3:
        date_text = blogpost.b.text[:-1]
    else:
        placeholder_text = blogpost.contents[1].text
        assert EMPTY_HAPS in placeholder_text
        assert placeholder_text.startswith(EMPTY_HAPS_DATE_PREFIX)
        date_text = placeholder_text.split("!")[0][len(EMPTY_HAPS_DATE_PREFIX):]
    return parse_date(date_text)


def get_image_url(image: Tag) -> str:
    image_path = image.attrs["src"]
    if not image_path.startswith("/") and not image_path.startswith("http"):
        image_path = "/" + image_path
    return image_path if image_path.startswith("http") else BASE_URL + image_path


def get_comic_url(soup: BeautifulSoup) -> str:
    return soup.find("meta", {"property": "og:url"}).attrs["content"]


def get_blogpost(soup: BeautifulSoup) -> Tag:
    return soup.find("div", {"class": "padded"}).find_all("p")[1]


def parse_date(date_text: str) -> date:
    return parse_datetime(date_text).date()
