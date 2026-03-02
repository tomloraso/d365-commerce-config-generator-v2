"""
Maps display file names to their generator classes.
Import this to get the full ordered list.
"""

from .sites_v2 import SitesV2Generator
from .warehouses import WarehousesGenerator
from .inventory_aisles import InventoryAislesGenerator
from .warehouse_locations import WarehouseLocationsGenerator
from .customers_v3 import CustomersV3Generator
from .price_customer_groups import PriceCustomerGroupsGenerator
from .operating_unit import OperatingUnitGenerator
from .operating_unit_contact import OperatingUnitContactGenerator
from .stores import StoresGenerator
from .retail_store_address_books import RetailStoreAddressBooksGenerator
from .retail_channel_price_group import RetailChannelPriceGroupGenerator
from .income_expense_accounts import IncomeExpenseAccountsGenerator
from .info_code_table_assignments import InfoCodeTableAssignmentsGenerator
from .store_payment_methods import StorePaymentMethodsGenerator
from .store_payment_card_setup import StorePaymentCardSetupGenerator
from .store_hardware_station import StoreHardwareStationGenerator

GENERATOR_REGISTRY = {
    "1.1-SitesV2.csv":                SitesV2Generator,
    "1.2-Warehouses.csv":             WarehousesGenerator,
    "1.3-InventoryAisles.csv":        InventoryAislesGenerator,
    "1.4-WarehouseLocations.csv":     WarehouseLocationsGenerator,
    "1.5-CustomersV3.csv":            CustomersV3Generator,
    "1.6-PriceCustomerGroups.csv":    PriceCustomerGroupsGenerator,
    "2.1-OperatingUnit.csv":          OperatingUnitGenerator,
    "2.2-OperatingUnitContact.csv":   OperatingUnitContactGenerator,
    "2.3-Stores.csv":                 StoresGenerator,
    "2.4-RetailStoreAddressBooks.csv": RetailStoreAddressBooksGenerator,
    "2.5-RetailChannelPriceGroup.csv": RetailChannelPriceGroupGenerator,
    "2.6-IncomeExpenseAccounts.csv":  IncomeExpenseAccountsGenerator,
    "2.7-InfoCodeTableAssignments.csv": InfoCodeTableAssignmentsGenerator,
    "2.8-StorePaymentMethods.csv":    StorePaymentMethodsGenerator,
    "2.9-StorePaymentCardSetup.csv":  StorePaymentCardSetupGenerator,
    "3.0-StoreHardwareStation.csv":   StoreHardwareStationGenerator,
}
