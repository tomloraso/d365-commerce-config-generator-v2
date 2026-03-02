"""
CardPanel: right-hand panel for selecting accepted credit/debit card types.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..config.profile import ALL_CARDS


class CardPanel(ttk.LabelFrame):

    def __init__(self, master, profile, **kwargs):
        kwargs.setdefault("text", "Accepted Cards  (Tender 660)")
        super().__init__(master, **kwargs)
        self.profile = profile
        self._vars = {}
        self._build()

    def _build(self):
        # Select All toggle
        self._all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self, text="Select All", variable=self._all_var,
            bootstyle="info-round-toggle",
            command=self._toggle_all,
        ).pack(anchor=W, pady=(0, 6))

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, pady=(0, 6))

        for card in ALL_CARDS:
            var = tk.BooleanVar(value=(card in self.profile.accepted_cards))
            cb = ttk.Checkbutton(self, text=card, variable=var, bootstyle="info",
                                 command=self._on_change)
            cb.pack(anchor=W, pady=2)
            self._vars[card] = var

    def _toggle_all(self):
        state = self._all_var.get()
        for var in self._vars.values():
            var.set(state)
        self._sync_profile()

    def _on_change(self):
        self._sync_profile()
        all_on = all(v.get() for v in self._vars.values())
        self._all_var.set(all_on)

    def _sync_profile(self):
        self.profile.accepted_cards = [c for c, v in self._vars.items() if v.get()]

    def refresh(self):
        for card, var in self._vars.items():
            var.set(card in self.profile.accepted_cards)
