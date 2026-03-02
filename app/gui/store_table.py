"""
StoreTable: the left-hand panel containing the input form and treeview.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..config.profile import STORE_FIELDS
from ..utils.validation import validate_record


class StoreTable(ttk.Frame):

    def __init__(self, master, profile, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.profile = profile
        self.on_change = on_change  # callback when data changes
        self.entries = {}
        self._error_labels = {}

        self._build_form()
        self._build_table()
        self._build_form_buttons()

    # ------------------------------------------------------------------ form

    def _build_form(self):
        form_outer = ttk.LabelFrame(self, text="Store Details")
        form_outer.pack(fill=X, padx=8, pady=(8, 4))

        # Two columns of fields for compactness
        left = ttk.Frame(form_outer, padding=10)
        right = ttk.Frame(form_outer, padding=10)
        left.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        right.pack(side=LEFT, fill=X, expand=True)

        mid = len(STORE_FIELDS) // 2
        for col_frame, fields in [(left, STORE_FIELDS[:mid]), (right, STORE_FIELDS[mid:])]:
            for field in fields:
                row = ttk.Frame(col_frame)
                row.pack(fill=X, pady=2)
                lbl = ttk.Label(row, text=field, width=13, anchor=E)
                lbl.pack(side=LEFT, padx=(0, 6))
                entry = ttk.Entry(row, bootstyle="info")
                entry.pack(side=LEFT, fill=X, expand=True)
                self.entries[field] = entry
                err = ttk.Label(row, text="", foreground="#e74c3c", font=("", 8))
                err.pack(side=LEFT, padx=(4, 0))
                self._error_labels[field] = err

    def _build_form_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=8, pady=(0, 4))

        ttk.Button(btn_frame, text="Add / Update", bootstyle="success",
                   command=self.add_record).pack(side=LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="Clear Form", bootstyle="secondary-outline",
                   command=self._clear_form).pack(side=LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="Delete Selected", bootstyle="danger-outline",
                   command=self.delete_selected).pack(side=LEFT)

    # ---------------------------------------------------------------- table

    def _build_table(self):
        table_outer = ttk.LabelFrame(self, text="Stores")
        table_outer.pack(fill=BOTH, expand=True, padx=8, pady=4)

        self.tree = ttk.Treeview(
            table_outer,
            columns=STORE_FIELDS,
            show="headings",
            bootstyle="info",
            selectmode="extended",
        )
        for field in STORE_FIELDS:
            self.tree.heading(field, text=field, command=lambda f=field: self._sort_by(f))
            self.tree.column(field, width=110, minwidth=60, stretch=True)

        vsb = ttk.Scrollbar(table_outer, orient=VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_outer, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=NSEW)
        vsb.grid(row=0, column=1, sticky=NS)
        hsb.grid(row=1, column=0, sticky=EW)
        table_outer.grid_rowconfigure(0, weight=1)
        table_outer.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)

    def _sort_by(self, field):
        data = [(self.tree.set(child, field), child) for child in self.tree.get_children("")]
        data.sort(key=lambda x: x[0])
        for i, (_, child) in enumerate(data):
            self.tree.move(child, "", i)

    # ------------------------------------------------------------ CRUD ops

    def add_record(self):
        rec = {f: self.entries[f].get().strip() for f in STORE_FIELDS}

        # Build list of existing IDs excluding the currently selected row (for edit)
        sel = self.tree.selection()
        existing_ids = [
            r["STOREID"] for i, r in enumerate(self.profile.stores)
            if not (sel and i == int(self.tree.index(sel[0])))
        ]

        errors = validate_record(rec, existing_ids)
        self._show_errors(errors, rec)
        if errors:
            return

        self._clear_errors()

        if sel:
            idx = int(self.tree.index(sel[0]))
            self.profile.stores[idx] = rec
        else:
            self.profile.stores.append(rec)

        self.refresh_table()
        self._clear_form()
        if self.on_change:
            self.on_change()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idxs = sorted([int(self.tree.index(i)) for i in sel], reverse=True)
        for i in idxs:
            del self.profile.stores[i]
        self.refresh_table()
        if self.on_change:
            self.on_change()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for rec in self.profile.stores:
            self.tree.insert("", END, values=[rec.get(f, "") for f in STORE_FIELDS])

    def paste_stores(self, rows: list):
        """Called by main app after clipboard parsing."""
        self.profile.stores.extend(rows)
        self.refresh_table()
        if self.on_change:
            self.on_change()

    def load_stores(self, stores: list):
        self.profile.stores = stores
        self.refresh_table()
        if self.on_change:
            self.on_change()

    # ---------------------------------------------------------- helpers

    def _on_double_click(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.index(sel[0]))
        rec = self.profile.stores[idx]
        for f, entry in self.entries.items():
            entry.delete(0, END)
            entry.insert(0, rec.get(f, ""))

    def _clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, END)
        self._clear_errors()
        self.tree.selection_remove(*self.tree.selection())

    def _show_errors(self, errors: list, rec: dict):
        self._clear_errors()
        for err in errors:
            for field in STORE_FIELDS:
                if field in err:
                    self._error_labels[field].config(text="!")
                    self.entries[field].configure(bootstyle="danger")

    def _clear_errors(self):
        for field in STORE_FIELDS:
            self._error_labels[field].config(text="")
            self.entries[field].configure(bootstyle="info")

    def get_row_count(self) -> int:
        return len(self.profile.stores)
