#!/usr/bin/env python3
import json
import urllib

import requests

HEADERS = {
    "x-waapi-token": "6f4b5e82-d4f5-4a82-bfa3-39c2740e09b4",
    "accept": "application/json",
    "content-type": "application/json",
}


def debug(*vals):
    try:
        print(json.dumps(vals, indent=4))
    except:
        print(vals)


class MinRenovasjonNo:
    def __init__(self, municipality: str, street: str, number: int | str):
        self._municipality: str = municipality
        self._street: str = street
        self._number: str = str(number)

    def get_supported_municipalities():
        s = requests.session()
        s.headers.update(HEADERS)

        r = s.get("https://www.webatlas.no/WAAPI-Kommuneinfo/kommune")
        r.raise_for_status()
        municipalities = r.json()["KommuneList"]

        r = s.get(
            "https://tjenestekatalogen.api.norkart.no/CatalogueService.svc/json/GetRegisteredRenovationCustomers"
        )
        r.raise_for_status()

        supported = {}
        for mun in r.json():
            supported[mun["Number"]] = mun

        supported_municipals = []

        for mun in municipalities:
            if mun["KommuneNumber"] in supported:
                supported_municipals.append(
                    {"municipality": mun, "customer": supported[mun["KommuneNumber"]]}
                )
        return supported_municipals

    def find_address(self) -> dict:
        mun = self.find_municipality()
        debug("Municipality", mun)

        street = self.find_street(mun["municipality"]["KommuneNumber"])
        debug("street", street)

        address = self.find_house_number(
            mun["municipality"]["KommuneNumber"], street["Text"].split(",")[0].strip()
        )

        self.get_gatekode(
            address_id=address["Id"],
            street_name=street["Text"].split(",")[0].strip(),
            number=self._number,
        )

        return address

    def find_municipality(self) -> dict:
        for mun in MinRenovasjonNo.get_supported_municipalities():
            if (
                self._municipality.lower().strip()
                == mun["municipality"]["KommuneName"]["nor"].lower().strip()
            ):
                return mun
        raise ValueError(f"Unknown municipality: {self._municipality}")

    def find_street(self, municipality_id: int | str) -> dict:
        s = requests.session()
        s.headers.update(**HEADERS)

        params = {
            "KommuneLimit": municipality_id,
            "Targets": "gate",
            "Query": self._street,
            "Size": 50,
        }
        params = urllib.parse.urlencode(params)

        r = s.get(
            "https://www.webatlas.no/WAAPI-FritekstSok/suggest/kommunecustom",
            params=params,
        )
        r.raise_for_status()
        try:
            streets = r.json()["Options"]
        except:
            raise Exception("Failed to parse response")

        if len(streets) < 1:
            raise ValueError(f"Unknown street: {self._street}")
        if len(streets) > 1:
            for street in streets:
                if self._street.lower().strip() in street["Text"].lower():
                    return street

        return streets[0]

    def find_house_number(self, municipality_id: int | str, street_name: str) -> dict:
        s = requests.session()
        s.headers.update(HEADERS)
        params = {
            "KommuneLimit": municipality_id,
            "Targets": "gateadresse",
            "Query": f"{street_name} {self._number}",
            "Size": 50,
        }
        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        r = s.get(
            "https://www.webatlas.no/WAAPI-FritekstSok/suggest/kommunecustom",
            params=params,
        )
        r.raise_for_status()

        addresses = r.json()["Options"]
        if len(addresses) < 1:
            raise ValueError(f"Unknown number: {self._number}")

        if len(addresses) > 1:
            for address in addresses:
                if self._number.lower().strip() in address["Text"].lower():
                    return address

        return addresses[0]

    def get_waste_types():
        r = requests.get(
            "https://komteksky.norkart.no/minrenovasjon.api/api/Fraksjoner",
            headers=HEADERS,
        )
        r.raise_for_status()
        return r.json()

    def get_gatekode(self, address_id: str | int, street_name, number):
        s = requests.session()
        s.headers.update(HEADERS)
        r = s.get(
            "https://komteksky.norkart.no/minrenovasjon.api/api/Tommekalender/Adresseforslag",
            params={
                "gatenavn": street_name,
                "husnr": number,
                "eiendom": address_id,
                "api-version": 2,
                "gatekode": 2020,
            },
        )
        r.raise_for_status()
        debug(r.json())

    def get_collections(street: str, number: str | int):
        pass

    def get_schedule(self):
        pass

    def generate_service_map():
        print(json.dumps(MinRenovasjonNo.get_supported_municipalities(), indent=4))
        # print([mun["KommuneName"]["nor"] for mun in supported_municipals])


if __name__ == "__main__":
    # MinRenovasjonDe.generate_service_map()

    minRenovasjonNo = MinRenovasjonNo("Alvdal", "amundsmoen", 15)
    address = minRenovasjonNo.find_address()
    debug("address", address)
    minRenovasjonNo.get_gatekode(address["Id"])
