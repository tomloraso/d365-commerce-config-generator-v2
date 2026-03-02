"""
Settings dialog: tabbed editor for all project-level configurable values.
Changes are held in a working copy until Apply/OK is clicked.
"""

import copy
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..config.defaults import (
    SETTINGS_SCHEMA, SETTINGS_LABELS, TAB_LABELS,
    D365_TIMEZONES, WINDOWS_TIMEZONES, get_default_settings,
)


class SettingsDialog(tk.Toplevel):

    def __init__(self, master, profile, on_apply=None):
        super().__init__(master)
        self.title("Project Settings")
        self.resizable(True, True)
        self.minsize(640, 520)
        self.grab_set()  # modal

        self.profile = profile
        self.on_apply = on_apply
        # Work on a deep copy so Cancel truly discards
        self._working = copy.deepcopy(profile.settings)
        self._entries = {}  # {(category, key): widget}

        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        # Header
        hdr = ttk.Frame(self, padding=(16, 12, 16, 8))
        hdr.pack(fill=X)
        ttk.Label(hdr, text="Project Settings", font=("", 14, "bold")).pack(side=LEFT)
        ttk.Label(hdr, text="Changes apply to this profile only",
                  foreground="#888").pack(side=LEFT, padx=(12, 0))

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X)

        # Notes area
        notes_frame = ttk.LabelFrame(self, text="Project Notes")
        notes_frame.pack(fill=X, padx=16, pady=(10, 0))
        self._notes_text = tk.Text(notes_frame, height=3, wrap=WORD, font=("", 9), padx=6, pady=6)
        self._notes_text.insert("1.0", self.profile.notes)
        self._notes_text.pack(fill=X)

        # Notebook
        self._notebook = ttk.Notebook(self, bootstyle="info")
        self._notebook.pack(fill=BOTH, expand=True, padx=16, pady=10)

        for category, keys in SETTINGS_SCHEMA.items():
            tab = self._build_tab(category, keys)
            label = TAB_LABELS.get(category, category.title())
            self._notebook.add(tab, text=label)

        # Footer buttons
        footer = ttk.Frame(self, padding=(16, 8))
        footer.pack(fill=X)

        ttk.Button(footer, text="Reset Tab to Defaults",
                   bootstyle="secondary-outline",
                   command=self._reset_tab).pack(side=LEFT)
        ttk.Button(footer, text="Reset All to Defaults",
                   bootstyle="warning-outline",
                   command=self._reset_all).pack(side=LEFT, padx=8)

        ttk.Button(footer, text="Cancel",
                   bootstyle="secondary",
                   command=self.destroy).pack(side=RIGHT)
        ttk.Button(footer, text="OK",
                   bootstyle="success",
                   command=self._ok).pack(side=RIGHT, padx=8)
        ttk.Button(footer, text="Apply",
                   bootstyle="primary",
                   command=self._apply).pack(side=RIGHT)

    def _build_tab(self, category: str, keys: dict) -> ttk.Frame:
        outer = ttk.Frame(self._notebook)
        canvas = tk.Canvas(outer, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        inner = ttk.Frame(canvas, padding=(12, 8))
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor=NW)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)

        labels = SETTINGS_LABELS.get(category, {})

        for row_idx, key in enumerate(keys):
            label_text = labels.get(key, key)
            ttk.Label(inner, text=label_text, anchor=W).grid(
                row=row_idx, column=0, sticky=EW, padx=(0, 12), pady=4
            )

            # Special widgets for timezone fields
            if key == "site_timezone" or key == "channel_timezone":
                var = tk.StringVar(value=self._working.get(category, {}).get(key, ""))
                widget = ttk.Combobox(inner, textvariable=var, values=D365_TIMEZONES,
                                      state="normal", width=44, bootstyle="info")
                widget.grid(row=row_idx, column=1, sticky=EW, pady=4)
                self._entries[(category, key)] = var

            elif key == "channel_timezone_info_id":
                var = tk.StringVar(value=self._working.get(category, {}).get(key, ""))
                widget = ttk.Combobox(inner, textvariable=var, values=WINDOWS_TIMEZONES,
                                      state="normal", width=44, bootstyle="info")
                widget.grid(row=row_idx, column=1, sticky=EW, pady=4)
                self._entries[(category, key)] = var

            elif key in ("price_includes_sales_tax",):
                var = tk.StringVar(value=self._working.get(category, {}).get(key, "Yes"))
                widget = ttk.Combobox(inner, textvariable=var, values=["Yes", "No"],
                                      state="readonly", width=44, bootstyle="info")
                widget.grid(row=row_idx, column=1, sticky=EW, pady=4)
                self._entries[(category, key)] = var

            else:
                var = tk.StringVar(value=self._working.get(category, {}).get(key, ""))
                entry = ttk.Entry(inner, textvariable=var, width=46, bootstyle="info")
                entry.grid(row=row_idx, column=1, sticky=EW, pady=4)
                self._entries[(category, key)] = var

            # Reset-to-default button per field
            default_val = SETTINGS_SCHEMA.get(category, {}).get(key, "")
            ttk.Button(
                inner, text="↺", bootstyle="secondary-link", width=3,
                command=lambda c=category, k=key, d=default_val: self._reset_field(c, k, d),
            ).grid(row=row_idx, column=2, pady=4, padx=(4, 0))

        inner.grid_columnconfigure(1, weight=1)
        return outer

    def _reset_field(self, category, key, default_val):
        entry_var = self._entries.get((category, key))
        if entry_var:
            entry_var.set(default_val)

    def _reset_tab(self):
        current_tab = self._notebook.index(self._notebook.select())
        category = list(SETTINGS_SCHEMA.keys())[current_tab]
        defaults = get_default_settings()
        for key, default_val in defaults.get(category, {}).items():
            entry_var = self._entries.get((category, key))
            if entry_var:
                entry_var.set(default_val)

    def _reset_all(self):
        defaults = get_default_settings()
        for (category, key), var in self._entries.items():
            default_val = defaults.get(category, {}).get(key, "")
            var.set(default_val)

    def _collect(self):
        """Pull current widget values back into _working dict."""
        for (category, key), var in self._entries.items():
            if category not in self._working:
                self._working[category] = {}
            self._working[category][key] = var.get()

    def _apply(self):
        self._collect()
        self.profile.settings = copy.deepcopy(self._working)
        self.profile.notes = self._notes_text.get("1.0", "end-1c")
        if self.on_apply:
            self.on_apply()

    def _ok(self):
        self._apply()
        self.destroy()
