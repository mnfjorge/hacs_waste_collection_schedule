from datetime import datetime

import requests
from bs4 import BeautifulSoup
from waste_collection_schedule import Collection  # type: ignore[attr-defined]

TITLE = "Hentavfall"
DESCRIPTION = "Source for Hentavfall."
URL = "https://www.hentavfall.no"
TEST_CASES = {
    "Sandnes 62 281 0": {
        "id": "181e5aac-3c88-4b0b-ad46-3bd246c2be2c",
        "municipality": "Sandnes",
        "gnumber": 62,
        "bnumber": 281,
        "snumber": 0,
    },
    "Stavanger": {
        "id": "57bf9d36-722e-400b-ae93-d80f8e354724",
        "municipality": "Stavanger",
        "gnumber": "57",
        "bnumber": "922",
        "snumber": "0",
    },
}


ICON_MAP = {
    "Restavfall": "mdi:trash-can",
    "Papp/papir": "mdi:recycle",
    "Bio": "mdi:leaf",
    "Juletre": "mdi:pine-tree",
}


API_URLS = {
    "sandnes": "https://www.hentavfall.no/rogaland/sandnes/tommekalender/show",
    "stavanger": "https://www.stavanger.kommune.no/renovasjon-og-miljo/tommekalender/finn-kalender/show",
}


class Source:
    def __init__(
        self,
        id: str | int,
        municipality: str,
        gnumber: str | int,
        bnumber: str | int,
        snumber: str | int,
    ):
        self._id: str | int = id
        self._municipality: str = municipality
        self._gnumber: str | int = gnumber
        self._bnumber: str | int = bnumber
        self._snumber: str | int = snumber

    def fetch(self):

        headers = {"referer": "https://www.stavanger.kommune.no"}

        params = {
            "id": self._id,
            "municipality": self._municipality,
            "gnumber": self._gnumber,
            "bnumber": self._bnumber,
            "snumber": self._snumber,
        }

        r = requests.get(API_URL, params=params, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        tag = soup.find_all("option")
        year = tag[0].get("value").split("-")
        year = year[1]

        entries = []
        for tag in soup.find_all("tr", {"class": "waste-calendar__item"}):
            if tag.text.strip() == "Dato og dag\nAvfallstype":
                continue

            date = tag.text.strip().split(" - ")
            date = datetime.strptime(date[0] + "." + year, "%d.%m.%Y").date()

            for img in tag.find_all("img"):
                waste_type = img.get("title")
                entries.append(
                    Collection(date, waste_type, icon=ICON_MAP.get(waste_type))
                )

        return entries
