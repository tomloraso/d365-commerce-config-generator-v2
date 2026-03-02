"""
ProjectProfile: central data object holding store rows + all project settings.
Passed between GUI and generators - neither layer owns it.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from .defaults import get_default_settings

ALL_FILES = [
    "1.1-SitesV2.csv",
    "1.2-Warehouses.csv",
    "1.3-InventoryAisles.csv",
    "1.4-WarehouseLocations.csv",
    "1.5-CustomersV3.csv",
    "1.6-PriceCustomerGroups.csv",
    "2.1-OperatingUnit.csv",
    "2.2-OperatingUnitContact.csv",
    "2.3-Stores.csv",
    "2.4-RetailStoreAddressBooks.csv",
    "2.5-RetailChannelPriceGroup.csv",
    "2.6-IncomeExpenseAccounts.csv",
    "2.7-InfoCodeTableAssignments.csv",
    "2.8-StorePaymentMethods.csv",
    "2.9-StorePaymentCardSetup.csv",
    "3.0-StoreHardwareStation.csv",
]

ALL_CARDS = [
    "Visa", "Mastercard", "Maestro", "JCB",
    "Amex", "Electron", "Diners", "Discover", "UnionPay",
]

DEFAULT_CARDS = [c for c in ALL_CARDS if c != "Electron"]

STORE_FIELDS = [
    'LEGALENTITY', 'COUNTRY', 'ISOCODE', 'FASCIA', 'STOREID',
    'STORENAME', 'ADDRESS', 'CITY', 'POSTCODE', 'LANGUAGE',
    'CURRENCY', 'TAXGROUP', 'PHONE', 'COUNTRYCODE',
]


@dataclass
class ProjectProfile:
    profile_name: str = "Untitled Project"
    notes: str = ""
    output_directory: str = ""
    settings: Dict[str, Any] = field(default_factory=get_default_settings)
    accepted_cards: List[str] = field(default_factory=lambda: list(DEFAULT_CARDS))
    selected_files: List[str] = field(default_factory=lambda: list(ALL_FILES))
    stores: List[Dict[str, str]] = field(default_factory=list)

    def s(self, category: str, key: str) -> str:
        """Shorthand settings accessor used by generators."""
        return self.settings.get(category, {}).get(key, "")

    def get_legal_entity(self) -> str:
        if self.stores:
            return self.stores[0].get("LEGALENTITY", "")
        return ""

    def get_output_prefix(self) -> str:
        return self.get_legal_entity()[:4].upper()
