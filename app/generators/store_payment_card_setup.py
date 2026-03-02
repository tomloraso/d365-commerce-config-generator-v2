from .base import BaseGenerator

CARD_MAPPING = {
    "Visa":       ("VISA",     "Visa"),
    "Mastercard": ("MASTER",   "Mastercard"),
    "Maestro":    ("MAESTRO",  "Maestro"),
    "JCB":        ("JCB",      "JCB"),
    "Amex":       ("AMEX",     "Amex"),
    "Electron":   ("ELECTRON", "Electron"),
    "Diners":     ("DINERS",   "Diners"),
    "Discover":   ("DISCOVER", "Discover"),
    "UnionPay":   ("UNIONPAY", "UnionPay"),
}


class StorePaymentCardSetupGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "TENDERTYPEID", "CARDTYPEID", "OMOPERATINGUNITNUMBER", "ACCOUNTTYPE",
            "ALLOWMANUALINPUT", "CARDFEE", "CARDFEEMAX", "CARDFEEMIN", "CARDINQUIRYFEE",
            "CARDNUMBERSWIPED", "CASHBACKLIMIT", "CHECKEXPIREDDATE", "CHECKMODULUS",
            "COUNTINGREQUIRED", "ENTERFLEETINFO", "ISEXPIRATIONDATEREQUIRED", "ISPINREQUIRED",
            "LEDGERDIMENSIONDISPLAYVALUE", "MANUALAUTHORIZATION", "MAXNORMALDIFFERENCEAMOUNT",
            "NAME", "PREAPPROVALDURATIONDAYS", "PROCESSLOCALLY", "SAMECARDALLOWED",
        ]

    def _row(self, tender_id, card_type_id, om_unit, ledger, name, allow_manual="Yes"):
        return {
            "TENDERTYPEID": tender_id,
            "CARDTYPEID": card_type_id,
            "OMOPERATINGUNITNUMBER": om_unit,
            "ACCOUNTTYPE": "Ledger",
            "ALLOWMANUALINPUT": allow_manual,
            "CARDFEE": "0",
            "CARDFEEMAX": "0",
            "CARDFEEMIN": "0",
            "CARDINQUIRYFEE": "0",
            "CARDNUMBERSWIPED": "No",
            "CASHBACKLIMIT": "0",
            "CHECKEXPIREDDATE": "No",
            "CHECKMODULUS": "No",
            "COUNTINGREQUIRED": "No",
            "ENTERFLEETINFO": "No",
            "ISEXPIRATIONDATEREQUIRED": "No",
            "ISPINREQUIRED": "No",
            "LEDGERDIMENSIONDISPLAYVALUE": ledger,
            "MANUALAUTHORIZATION": "No",
            "MAXNORMALDIFFERENCEAMOUNT": "0",
            "NAME": name,
            "PREAPPROVALDURATIONDAYS": "0",
            "PROCESSLOCALLY": "No",
            "SAMECARDALLOWED": "No",
        }

    def generate(self, stores):
        la = self.s.get("ledger_accounts", {})
        pmt = self.s.get("payment", {})
        cash_ledger = la.get("cash_ledger", "821701")
        bfv_ledger = la.get("black_friday_voucher_ledger", "917023")
        cn_ledger = la.get("credit_note_ledger", "917012")
        gc_ledger = la.get("gift_card_ledger", "917002")
        t_bfv = pmt.get("tender_id_black_friday_voucher", "1023")
        t_cn = pmt.get("tender_id_credit_note", "631")
        t_gc = pmt.get("tender_id_gift_card", "650")
        t_card = pmt.get("tender_id_card", "660")
        prefix = self.setting("store", "operating_unit_prefix")
        selected_cards = self.profile.accepted_cards

        rows = []
        for r in stores:
            store_id = r["STOREID"].zfill(4)
            om_unit = f"{prefix}{store_id}"

            # Fixed tenders: BFV, Credit Note, Gift Card
            rows.append(self._row(t_bfv, "ExtLIAB", om_unit, bfv_ledger, "Black Friday Voucher"))
            rows.append(self._row(t_cn,  "ExtLIAB", om_unit, cn_ledger,  "Credit Note"))
            rows.append(self._row(t_gc,  "ExtLIAB", om_unit, gc_ledger,  "Gift Card"))

            # Dynamic card tenders under Tender 660
            for card_name in selected_cards:
                if card_name in CARD_MAPPING:
                    card_type_id, display_name = CARD_MAPPING[card_name]
                    rows.append(self._row(t_card, card_type_id, om_unit, cash_ledger, display_name, allow_manual="No"))

        return rows
