"""
Validation logic for store records.
All functions are pure: accept data, return error strings or None.
"""

import re
from typing import Optional, List, Dict


def validate_store_id(value: str) -> Optional[str]:
    if not re.match(r'^\d{4}$', value):
        return "STOREID must be a 4-digit number (e.g. 0580)"
    return None


def validate_isocode(value: str) -> Optional[str]:
    if not re.match(r'^[A-Z]{3}$', value):
        return "ISOCODE must be a 3-letter uppercase code (e.g. GBR)"
    return None


def validate_countrycode(value: str) -> Optional[str]:
    if value and not re.match(r'^[A-Za-z]{2}$', value):
        return "COUNTRYCODE must be a 2-letter code (e.g. GB)"
    return None


def validate_currency(value: str) -> Optional[str]:
    if not re.match(r'^[A-Z]{3}$', value):
        return "CURRENCY must be a 3-letter uppercase code (e.g. GBP)"
    return None


def validate_record(record: Dict[str, str], existing_store_ids: List[str] = None) -> List[str]:
    """
    Validate a single store record. Returns a list of error messages (empty = valid).
    existing_store_ids: list of already-loaded STOREID values to check for duplicates.
    """
    errors = []
    required = [f for f in [
        'LEGALENTITY', 'COUNTRY', 'ISOCODE', 'FASCIA', 'STOREID',
        'STORENAME', 'ADDRESS', 'CITY', 'LANGUAGE', 'CURRENCY', 'TAXGROUP',
    ]]

    for field in required:
        if not record.get(field, "").strip():
            errors.append(f"{field} is required")

    if record.get("STOREID"):
        err = validate_store_id(record["STOREID"].strip())
        if err:
            errors.append(err)
        elif existing_store_ids and record["STOREID"].strip() in existing_store_ids:
            errors.append(f"STOREID {record['STOREID']} already exists")

    if record.get("ISOCODE"):
        err = validate_isocode(record["ISOCODE"].strip())
        if err:
            errors.append(err)

    if record.get("CURRENCY"):
        err = validate_currency(record["CURRENCY"].strip())
        if err:
            errors.append(err)

    if record.get("COUNTRYCODE"):
        err = validate_countrycode(record["COUNTRYCODE"].strip())
        if err:
            errors.append(err)

    return errors


def validate_all_stores(stores: List[Dict[str, str]]) -> Dict[int, List[str]]:
    """
    Validate all stores. Returns dict of {row_index: [errors]}.
    Only rows with errors are included.
    """
    results = {}
    seen_ids = []
    for i, store in enumerate(stores):
        store_id = store.get("STOREID", "").strip()
        errors = validate_record(store, seen_ids)
        if errors:
            results[i] = errors
        if store_id and not errors:
            seen_ids.append(store_id)
    return results
