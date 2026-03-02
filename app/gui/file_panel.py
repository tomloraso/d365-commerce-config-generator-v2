"""
FilePanel: right-hand panel for selecting which output files to generate.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..config.profile import ALL_FILES


class FilePanel(ttk.LabelFrame):

    def __init__(self, master, profile, **kwargs):
        kwargs.setdefault("text", "Files to Generate")
        kwargs.setdefault("padding", 10)
        super().__init__(master, **kwargs)
        self.profile = profile
        self._vars = {}
        self._build()

    def _build(self):
        # Select All toggle
        self._all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self, text="Select All", variable=self._all_var,
            bootstyle="primary-round-toggle",
            command=self._toggle_all,
        ).pack(anchor=W, pady=(0, 6))

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, pady=(0, 6))

        # Scrollable list
        canvas = tk.Canvas(self, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor=NW)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)

        for file_name in ALL_FILES:
            var = tk.BooleanVar(value=(file_name in self.profile.selected_files))
            cb = ttk.Checkbutton(inner, text=file_name, variable=var,
                                 bootstyle="primary", command=self._on_change)
            cb.pack(anchor=W, pady=2)
            self._vars[file_name] = var

        self._sync_all_toggle()

    def _toggle_all(self):
        state = self._all_var.get()
        for var in self._vars.values():
            var.set(state)
        self._sync_profile()

    def _on_change(self):
        self._sync_profile()
        self._sync_all_toggle()

    def _sync_all_toggle(self):
        all_on = all(v.get() for v in self._vars.values())
        self._all_var.set(all_on)

    def _sync_profile(self):
        self.profile.selected_files = [f for f, v in self._vars.items() if v.get()]

    def refresh(self):
        for fname, var in self._vars.items():
            var.set(fname in self.profile.selected_files)
        self._sync_all_toggle()

    def get_selected(self):
        return [f for f, v in self._vars.items() if v.get()]
