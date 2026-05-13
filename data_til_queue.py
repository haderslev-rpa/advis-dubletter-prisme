# Ansvar: Klargør advis-data til queue

from datetime import datetime, timedelta, date  # modul (dato/tid)
from collections import defaultdict            # modul (dict med standard)
from zoneinfo import ZoneInfo                  # modul (tidszone-regler)


def clean_text(value):
    """Rens tekst (fjern ' og whitespace)."""
    return ("" if value is None else str(value)).strip().replace("'", "")


def advice_date_to_date_or_raise(value):
    """
    Konverter AdviceDate fra UTC til Europe/Copenhagen
    og returnér kun dato (date-objekt).
    """
    if value in (None, ""):
        raise ValueError("AdviceDate mangler")

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        dt_utc = value
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text.replace("Z", "+00:00")

        dt_utc = datetime.fromisoformat(text)

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))

    dt_dk = dt_utc.astimezone(ZoneInfo("Europe/Copenhagen"))
    return dt_dk.date()


def build_queue_rows_from_advis(advis_list):
    """
    Regel:
    - Gruppér på Id
    - Sortér efter AdviceDate
    - Spring ældste over
    - Tilføj resten til queue
    """

    normaliseret = []

    for advis in advis_list:
        cust = clean_text(advis.get("CustAccount"))
        text = clean_text(advis.get("AdviceText"))
        advice_date = advice_date_to_date_or_raise(advis.get("AdviceDate"))

        adv_id = f"{cust}-{text}"

        normaliseret.append({
            "Id": adv_id,
            "AdviceDate": advice_date,
            "Tekst": text,
            "Debitorkonto": cust,
            "RecIdLoc": clean_text(advis.get("RecIdLoc")),
        })

    grupper = defaultdict(list)
    for item in normaliseret:
        grupper[item["Id"]].append(item)

    queue_rows = []

    for adv_id, items in grupper.items():
        if len(items) <= 1:
            continue

        items_sorted = sorted(items, key=lambda x: x["AdviceDate"])

        for valgt in items_sorted[1:]:

            queue_rows.append({
                "Id": valgt["Id"],
                "Dato": (valgt["AdviceDate"] + timedelta(days=1)).isoformat(),  # <-- VIGTIG
                "Tekst": valgt["Tekst"],
                "Debitorkonto": valgt["Debitorkonto"],
                "RecIdLoc": valgt["RecIdLoc"],
            })


    return queue_rows