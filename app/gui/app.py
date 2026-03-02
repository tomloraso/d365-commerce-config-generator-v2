"""
Main application window.
"""

import os
import re
import csv
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd

from ..config.profile import ProjectProfile, STORE_FIELDS, ALL_FILES
from ..config.persistence import save_profile, load_profile, get_recent_profiles
from ..generators.registry import GENERATOR_REGISTRY
from ..utils.validation import validate_record, validate_all_stores
from .store_table import StoreTable
from .card_panel import CardPanel
from .file_panel import FilePanel
from .settings_dialog import SettingsDialog

APP_TITLE = "D365 Commerce Config Generator V2"
VERSION = "2.0.0"


class App(ttk.Window):

    def __init__(self):
        super().__init__(themename="cosmo")
        self.title(f"{APP_TITLE} — {VERSION}")
        self.geometry("1400x860")
        self.minsize(1100, 700)

        self.profile = ProjectProfile()
        self._current_file: Path | None = None
        self._unsaved = False

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

        self._refresh_status()
        self._refresh_title()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ================================================================ MENU

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Profile",        accelerator="Ctrl+N", command=self._new_profile)
        file_menu.add_command(label="Open Profile…",      accelerator="Ctrl+O", command=self._open_profile)
        file_menu.add_command(label="Save Profile",       accelerator="Ctrl+S", command=self._save_profile)
        file_menu.add_command(label="Save Profile As…",   accelerator="Ctrl+Shift+S", command=self._save_profile_as)
        file_menu.add_separator()
        self._recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Profiles", menu=self._recent_menu)
        self._rebuild_recent_menu()
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)

        # Data
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Data", menu=data_menu)
        data_menu.add_command(label="Paste from Clipboard", accelerator="Ctrl+V", command=self._paste_clipboard)
        data_menu.add_command(label="Import from Excel…",                          command=self._import_excel)
        data_menu.add_command(label="Save Store Data as CSV…",                     command=self._save_csv)
        data_menu.add_separator()
        data_menu.add_command(label="Clear All Stores",                            command=self._clear_stores)
        data_menu.add_command(label="Validate All Stores",                         command=self._validate_all)

        # Settings
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Project Settings…", accelerator="Ctrl+,", command=self._open_settings)

        # Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label=f"About {APP_TITLE}", command=self._show_about)

        # Keyboard shortcuts
        self.bind("<Control-n>", lambda _: self._new_profile())
        self.bind("<Control-o>", lambda _: self._open_profile())
        self.bind("<Control-s>", lambda _: self._save_profile())
        self.bind("<Control-S>", lambda _: self._save_profile_as())
        self.bind("<Control-v>", lambda _: self._paste_clipboard())
        self.bind("<Control-comma>", lambda _: self._open_settings())

    # ============================================================= TOOLBAR

    def _build_toolbar(self):
        tb = ttk.Frame(self, padding=(8, 4))
        tb.pack(fill=X, side=TOP)

        btn_cfg = {"bootstyle": "secondary-outline", "padding": (8, 4)}

        ttk.Button(tb, text="⊕  New",     command=self._new_profile,   **btn_cfg).pack(side=LEFT, padx=2)
        ttk.Button(tb, text="⊘  Open",    command=self._open_profile,   **btn_cfg).pack(side=LEFT, padx=2)
        ttk.Button(tb, text="⊛  Save",    command=self._save_profile,   **btn_cfg).pack(side=LEFT, padx=2)

        ttk.Separator(tb, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        ttk.Button(tb, text="⚙  Settings", command=self._open_settings,
                   bootstyle="info-outline", padding=(8, 4)).pack(side=LEFT, padx=2)

        ttk.Separator(tb, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        ttk.Button(tb, text="▶  Generate", command=self._generate,
                   bootstyle="success", padding=(8, 4)).pack(side=LEFT, padx=2)
        ttk.Button(tb, text="✔  Validate", command=self._validate_all,
                   bootstyle="info", padding=(8, 4)).pack(side=LEFT, padx=2)
        ttk.Button(tb, text="📁  Output Folder", command=self._open_output_folder,
                   bootstyle="secondary-outline", padding=(8, 4)).pack(side=LEFT, padx=2)

        ttk.Separator(tb, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)
        ttk.Button(tb, text="📋  Paste", command=self._paste_clipboard,
                   bootstyle="secondary-outline", padding=(8, 4)).pack(side=LEFT, padx=2)
        ttk.Button(tb, text="📂  Import Excel", command=self._import_excel,
                   bootstyle="secondary-outline", padding=(8, 4)).pack(side=LEFT, padx=2)

        # Profile name label on right
        self._profile_name_var = tk.StringVar(value=self.profile.profile_name)
        ttk.Label(tb, textvariable=self._profile_name_var,
                  font=("", 10, "bold"), foreground="#555").pack(side=RIGHT, padx=12)
        ttk.Label(tb, text="Profile:", foreground="#888").pack(side=RIGHT)

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X)

    # ================================================================ BODY

    def _build_body(self):
        body = ttk.Frame(self)
        body.pack(fill=BOTH, expand=True)

        # Left: store table (expandable)
        left = ttk.Frame(body)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(8, 4), pady=8)

        self._store_table = StoreTable(left, self.profile, on_change=self._on_data_change)
        self._store_table.pack(fill=BOTH, expand=True)

        # Right: fixed-width side panel
        right = ttk.Frame(body, width=320)
        right.pack(side=RIGHT, fill=Y, padx=(4, 8), pady=8)
        right.pack_propagate(False)

        self._card_panel = CardPanel(right, self.profile)
        self._card_panel.pack(fill=X, pady=(0, 8))

        self._file_panel = FilePanel(right, self.profile)
        self._file_panel.pack(fill=BOTH, expand=True)

    # =========================================================== STATUSBAR

    def _build_statusbar(self):
        bar = ttk.Frame(self, padding=(8, 3), bootstyle="secondary")
        bar.pack(fill=X, side=BOTTOM)

        self._status_left = tk.StringVar(value="Ready")
        self._status_mid = tk.StringVar(value="0 stores")
        self._status_right = tk.StringVar(value="No profile saved")

        ttk.Label(bar, textvariable=self._status_left,
                  foreground="white").pack(side=LEFT)
        ttk.Label(bar, textvariable=self._status_mid,
                  foreground="white").pack(side=LEFT, padx=20)
        ttk.Label(bar, textvariable=self._status_right,
                  foreground="#ccc").pack(side=RIGHT)

        self._progress = ttk.Progressbar(bar, length=180, bootstyle="success-striped",
                                          mode="determinate")
        self._progress.pack(side=RIGHT, padx=12)
        self._progress.pack_forget()  # hidden until generation

    # =========================================================== PROFILE OPS

    def _new_profile(self):
        if self._unsaved and not messagebox.askyesno(
            "Unsaved Changes", "Discard unsaved changes and create a new profile?"
        ):
            return
        self.profile = ProjectProfile()
        self._current_file = None
        self._unsaved = False
        self._reload_panels()
        self._refresh_status()
        self._refresh_title()

    def _open_profile(self):
        path = filedialog.askopenfilename(
            title="Open Profile",
            initialdir=Path(__file__).parent.parent.parent / "profiles",
            filetypes=[("D365 Profile", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self._load_profile_from(Path(path))

    def _load_profile_from(self, path: Path):
        try:
            self.profile = load_profile(path)
            self._current_file = path
            self._unsaved = False
            self._reload_panels()
            self._refresh_status()
            self._refresh_title()
            self._rebuild_recent_menu()
            self._set_status(f"Loaded: {path.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile:\n{e}")

    def _save_profile(self):
        if self._current_file:
            self._do_save(self._current_file)
        else:
            self._save_profile_as()

    def _save_profile_as(self):
        path = filedialog.asksaveasfilename(
            title="Save Profile As",
            initialdir=Path(__file__).parent.parent.parent / "profiles",
            defaultextension=".json",
            filetypes=[("D365 Profile", "*.json")],
            initialfile=f"{self.profile.profile_name}.json",
        )
        if not path:
            return
        self._do_save(Path(path))

    def _do_save(self, path: Path):
        try:
            save_profile(self.profile, path)
            self._current_file = path
            self._unsaved = False
            self._refresh_title()
            self._rebuild_recent_menu()
            self._set_status(f"Saved: {path.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile:\n{e}")

    def _rebuild_recent_menu(self):
        self._recent_menu.delete(0, END)
        recents = get_recent_profiles()
        for path_str in recents:
            p = Path(path_str)
            self._recent_menu.add_command(
                label=f"{p.name}  ({p.parent})",
                command=lambda ps=path_str: self._load_profile_from(Path(ps)),
            )
        if not recents:
            self._recent_menu.add_command(label="(none)", state=DISABLED)

    def _reload_panels(self):
        self._store_table.load_stores(self.profile.stores)
        self._card_panel.refresh()
        self._file_panel.refresh()
        self._profile_name_var.set(self.profile.profile_name)

    # ============================================================= DATA OPS

    def _paste_clipboard(self):
        try:
            txt = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("Clipboard", "Clipboard is empty or not accessible")
            return

        lines = [ln for ln in txt.splitlines() if ln.strip()]
        if not lines:
            messagebox.showwarning("Clipboard", "Nothing to paste")
            return

        valid, invalid = [], []
        existing_ids = [r["STOREID"] for r in self.profile.stores]

        for i, ln in enumerate(lines, 1):
            cols = ln.split("\t")
            if len(cols) != len(STORE_FIELDS):
                cols = ln.split(",")
            if len(cols) > len(STORE_FIELDS):
                cols = cols[:len(STORE_FIELDS)]
            elif len(cols) < len(STORE_FIELDS):
                cols.extend([""] * (len(STORE_FIELDS) - len(cols)))

            rec = {f: c.strip() for f, c in zip(STORE_FIELDS, cols)}
            errors = validate_record(rec, existing_ids)
            if errors:
                invalid.append(f"Row {i}: {'; '.join(errors)}")
            else:
                valid.append(rec)
                existing_ids.append(rec["STOREID"])

        if valid:
            self._store_table.paste_stores(valid)

        if valid and not invalid:
            self._set_status(f"Pasted {len(valid)} store(s)")
        elif valid and invalid:
            errors_text = "\n".join(invalid)
            messagebox.showwarning(
                "Partial Import",
                f"Imported {len(valid)} store(s).\n\nSkipped rows:\n{errors_text}"
            )
        else:
            errors_text = "\n".join(invalid)
            messagebox.showerror("Paste Failed", f"No valid rows found:\n{errors_text}")

    def _import_excel(self):
        path = filedialog.askopenfilename(
            title="Import Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            df = pd.read_excel(path, dtype={f: str for f in ["STOREID", "POSTCODE", "COUNTRYCODE"]})
            df = df.fillna("")

            # Add missing columns
            for col in STORE_FIELDS:
                if col not in df.columns:
                    df[col] = ""

            df = df[STORE_FIELDS]
            stores = df.to_dict("records")

            errors = validate_all_stores(stores)
            if errors:
                err_lines = []
                for idx, errs in errors.items():
                    store_id = stores[idx].get("STOREID", f"row {idx+2}")
                    err_lines.append(f"Store {store_id}: {'; '.join(errs)}")
                messagebox.showerror("Validation Errors", "\n".join(err_lines))
                return

            self._store_table.load_stores(stores)
            self._set_status(f"Imported {len(stores)} store(s) from {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import Excel:\n{e}")

    def _save_csv(self):
        if not self.profile.stores:
            messagebox.showinfo("No Data", "No store data to save")
            return
        path = filedialog.asksaveasfilename(
            title="Save Store Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="Master Values.csv",
        )
        if not path:
            return
        try:
            df = pd.DataFrame(self.profile.stores, columns=STORE_FIELDS)
            df.to_csv(path, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_NONNUMERIC)
            self._set_status(f"Saved store data to {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV:\n{e}")

    def _clear_stores(self):
        if not self.profile.stores:
            return
        if messagebox.askyesno("Clear Stores", "Remove all store data from this profile?"):
            self._store_table.load_stores([])
            self._set_status("All stores cleared")

    def _validate_all(self):
        if not self.profile.stores:
            messagebox.showinfo("Validate", "No stores to validate")
            return
        errors = validate_all_stores(self.profile.stores)
        if not errors:
            messagebox.showinfo("Validation Passed",
                                f"All {len(self.profile.stores)} store(s) are valid.")
            return

        lines = []
        for idx, errs in errors.items():
            store_id = self.profile.stores[idx].get("STOREID", f"Row {idx+1}")
            lines.append(f"Store {store_id}:")
            for e in errs:
                lines.append(f"  • {e}")
        messagebox.showwarning("Validation Issues", "\n".join(lines))

    # ============================================================= SETTINGS

    def _open_settings(self):
        SettingsDialog(self, self.profile, on_apply=self._on_settings_applied)

    def _on_settings_applied(self):
        self._unsaved = True
        self._refresh_title()
        self._set_status("Settings applied")

    # ============================================================= GENERATE

    def _generate(self):
        if not self.profile.stores:
            messagebox.showwarning("No Data", "Add at least one store before generating")
            return
        if not self.profile.selected_files:
            messagebox.showwarning("No Files", "Select at least one file to generate")
            return

        errors = validate_all_stores(self.profile.stores)
        if errors:
            count = len(errors)
            if not messagebox.askyesno(
                "Validation Issues",
                f"{count} store(s) have validation issues.\n\nGenerate anyway?"
            ):
                return

        # Determine output directory
        if self.profile.output_directory and Path(self.profile.output_directory).exists():
            output_dir = Path(self.profile.output_directory)
        else:
            output_dir = Path(__file__).parent.parent.parent / "output"

        output_dir.mkdir(parents=True, exist_ok=True)
        prefix = self.profile.get_output_prefix()

        # Run in thread to keep UI responsive
        self._progress.configure(maximum=len(self.profile.selected_files), value=0)
        self._progress.pack(side=RIGHT, padx=12)
        self._set_status("Generating...")

        threading.Thread(
            target=self._run_generation,
            args=(output_dir, prefix),
            daemon=True,
        ).start()

    def _run_generation(self, output_dir: Path, prefix: str):
        results = []
        errors = []
        stores = self.profile.stores
        done = 0

        for file_name in ALL_FILES:
            if file_name not in self.profile.selected_files:
                results.append((file_name, None, "SKIPPED"))
                continue

            gen_class = GENERATOR_REGISTRY.get(file_name)
            if not gen_class:
                errors.append(f"{file_name}: No generator registered")
                continue

            out_name = f"{prefix}_{file_name}"
            out_path = output_dir / out_name

            try:
                generator = gen_class(self.profile)
                rows = generator.generate(stores)
                result = generator.write(rows, out_path)
                results.append((file_name, result, "OK"))
            except Exception as e:
                results.append((file_name, None, f"ERROR: {e}"))
                errors.append(f"{file_name}: {e}")

            done += 1
            self.after(0, lambda v=done: self._progress.configure(value=v))

        self.after(0, lambda: self._on_generation_done(results, errors, output_dir))

    def _on_generation_done(self, results, errors, output_dir: Path):
        self._progress.pack_forget()

        generated = [(f, r) for f, r, s in results if s == "OK"]
        skipped = [f for f, r, s in results if s == "SKIPPED"]
        errs = [(f, s) for f, r, s in results if s.startswith("ERROR")]

        lines = ["Generation complete!\n"]
        for file_name, result in generated:
            lines.append(f"  ✓  {result.output_path.name}  ({result.row_count} rows)")
        if skipped:
            lines.append(f"\nSkipped {len(skipped)} file(s)")
        if errs:
            lines.append("\nErrors:")
            for f, err in errs:
                lines.append(f"  ✗  {f}: {err}")

        self._set_status(f"Generated {len(generated)} file(s)")

        msg = "\n".join(lines)
        if errs:
            messagebox.showwarning("Generation Complete (with errors)", msg)
        else:
            result_win = tk.Toplevel(self)
            result_win.title("Generation Complete")
            result_win.resizable(False, False)
            ttk.Label(result_win, text="Generation Complete",
                      font=("", 12, "bold"), padding=(16, 12)).pack()
            txt = tk.Text(result_win, width=64, height=len(lines) + 2,
                          font=("Consolas", 9), wrap=NONE)
            txt.insert("1.0", msg)
            txt.configure(state=DISABLED)
            txt.pack(padx=16, pady=(0, 8))

            btn_frame = ttk.Frame(result_win, padding=(16, 8))
            btn_frame.pack(fill=X)
            ttk.Button(btn_frame, text="Open Output Folder",
                       bootstyle="primary",
                       command=lambda: os.startfile(str(output_dir))).pack(side=LEFT)
            ttk.Button(btn_frame, text="Close",
                       bootstyle="secondary",
                       command=result_win.destroy).pack(side=RIGHT)

    # ============================================================= HELPERS

    def _open_output_folder(self):
        output_dir = Path(__file__).parent.parent.parent / "output"
        if self.profile.output_directory:
            output_dir = Path(self.profile.output_directory)
        if output_dir.exists():
            os.startfile(str(output_dir))
        else:
            messagebox.showinfo("Output Folder", f"Output folder not found:\n{output_dir}")

    def _on_data_change(self):
        self._unsaved = True
        self._refresh_status()
        self._refresh_title()

    def _refresh_status(self):
        count = len(self.profile.stores)
        self._status_mid.set(f"{count} store{'s' if count != 1 else ''}")
        self._status_right.set(
            str(self._current_file) if self._current_file else "Unsaved profile"
        )
        self._profile_name_var.set(self.profile.profile_name)

    def _refresh_title(self):
        dirty = " *" if self._unsaved else ""
        name = self.profile.profile_name
        self.title(f"{APP_TITLE} — {name}{dirty}")

    def _set_status(self, msg: str):
        self._status_left.set(msg)

    def _show_about(self):
        messagebox.showinfo(
            f"About {APP_TITLE}",
            f"{APP_TITLE}\nVersion {VERSION}\n\n"
            "Generates D365 Commerce DMF data entity CSV files\n"
            "for retail store onboarding.\n\n"
            "Built for D365 Commerce consultants."
        )

    def _on_close(self):
        if self._unsaved:
            resp = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if resp is None:
                return
            if resp:
                self._save_profile()
        self.destroy()
