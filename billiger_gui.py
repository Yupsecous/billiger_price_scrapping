"""Billiger.de Price Checker — GUI"""

import sys
import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pandas as pd

if getattr(sys, "frozen", False):
    _APP_DIR = os.path.dirname(sys.executable)
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _APP_DIR)

from billiger_price_checker import BilligerPriceChecker, _save_excel  # noqa: E402


class BilligerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Billiger.de Price Checker")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.file_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        self.is_running = False
        self.checker = None

        self._build_ui()

    # -- UI -------------------------------------------------------------------

    def _build_ui(self):
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main, text="Billiger.de Price Checker", font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 10))

        # File selection
        file_frame = ttk.LabelFrame(main, text="Input File", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        ttk.Button(file_frame, text="Browse...", command=self._browse).pack(side=tk.LEFT)

        # Options
        opts = ttk.LabelFrame(main, text="Options", padding="5")
        opts.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(opts)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Start from row:").pack(side=tk.LEFT)
        self.start_row = ttk.Spinbox(row1, from_=1, to=100_000, width=10)
        self.start_row.set(1)
        self.start_row.pack(side=tk.LEFT, padx=(5, 20))
        ttk.Label(row1, text="Limit (0=all):").pack(side=tk.LEFT)
        self.limit = ttk.Spinbox(row1, from_=0, to=100_000, width=10)
        self.limit.set(0)
        self.limit.pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(opts)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Save every N rows:").pack(side=tk.LEFT)
        self.save_interval = ttk.Spinbox(row2, from_=5, to=100, width=10)
        self.save_interval.set(10)
        self.save_interval.pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_btn = ttk.Button(btn_frame, text="Start Processing", command=self._start)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Progress
        prog_frame = ttk.Frame(main)
        prog_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100).pack(
            fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10)
        )
        ttk.Label(prog_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        # Log
        log_frame = ttk.LabelFrame(main, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=15, state="disabled", font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Stats
        stats = ttk.Frame(main)
        stats.pack(fill=tk.X, pady=(10, 0))
        self.stats_label = ttk.Label(stats, text="Processed: 0 | Found: 0 | Not Found: 0")
        self.stats_label.pack(side=tk.LEFT)

    # -- Helpers --------------------------------------------------------------

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Excel file with EAN codes",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if path:
            self.file_path.set(path)
            self._log(f"Selected: {path}")

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def _update_stats(self, processed: int, found: int, not_found: int):
        self.stats_label.config(
            text=f"Processed: {processed} | Found: {found} | Not Found: {not_found}"
        )

    # -- Processing -----------------------------------------------------------

    def _start(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        if not Path(self.file_path.get()).exists():
            messagebox.showerror("Error", "File not found.")
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        threading.Thread(target=self._process, daemon=True).start()

    def _stop(self):
        self.is_running = False
        self._log("Stopping \u2014 waiting for current request to finish ...")
        self.status_var.set("Stopping...")

    def _process(self):
        try:
            input_file = self.file_path.get()
            start = int(self.start_row.get()) - 1
            limit = int(self.limit.get())
            interval = int(self.save_interval.get())

            self._log(f"Reading {input_file}")
            df = pd.read_excel(input_file, dtype=str)
            total = len(df)
            self._log(f"Total rows: {total}")

            ean_col = None
            for col in df.columns:
                if any(k in col.lower() for k in ("ean", "gtin")):
                    ean_col = col
                    break
            if ean_col is None:
                ean_col = df.columns[0]
            self._log(f"EAN column: {ean_col}")

            to_drop = [c for c in df.columns if "unnamed" in c.lower() or c.strip() == ""]
            if to_drop:
                df.drop(columns=to_drop, inplace=True)

            for col in ("billiger", "eBay", "Timestamp", "Status"):
                if col not in df.columns:
                    df[col] = None

            price_idx = next(
                (i for i, c in enumerate(df.columns) if "price" in c.lower()), None
            )
            if price_idx is not None:
                cols = [
                    c for c in df.columns if c not in ("billiger", "eBay", "Timestamp", "Status")
                ]
                for j, nc in enumerate(("billiger", "eBay", "Timestamp", "Status")):
                    cols.insert(price_idx + 1 + j, nc)
                df = df[cols]

            end = min(start + limit, total) if limit > 0 else total
            rows_to_process = end - start
            self._log(f"Processing rows {start + 1} to {end}")

            self._log("Initializing browser ...")
            self.status_var.set("Initializing...")
            self.checker = BilligerPriceChecker(headless=False, delay_range=(1.0, 2.0))

            found, not_found, processed = 0, 0, 0

            for idx in range(start, end):
                if not self.is_running:
                    self._log("Stopped by user.")
                    break

                ean = str(df.iloc[idx][ean_col]).strip() if pd.notna(df.iloc[idx][ean_col]) else ""

                if not ean or ean.lower() == "nan" or len(ean) < 8:
                    df.at[idx, "Status"] = "Invalid EAN"
                    df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    processed += 1
                    not_found += 1
                    continue

                current = df.at[idx, "Status"]
                if pd.notna(current) and current not in ("", "None"):
                    continue

                self._log(f"[{idx + 1}/{end}] EAN: {ean}")
                self.status_var.set(f"Processing {idx + 1}/{end}")

                result = self.checker.get_price(ean)

                df.at[idx, "billiger"] = result.get("billiger_price")
                df.at[idx, "eBay"] = result.get("ebay_price")
                df.at[idx, "Status"] = result["status"]
                df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                processed += 1

                if result["status"] == "Found":
                    found += 1
                    price = result.get("billiger_price") or result.get("ebay_price")
                    self._log(f"  \u2192 {price} EUR ({result.get('source', '')})")
                else:
                    not_found += 1
                    self._log("  \u2192 NOT FOUND")

                progress = (processed / rows_to_process) * 100 if rows_to_process else 0
                self.progress_var.set(progress)
                self._update_stats(processed, found, not_found)

                if processed % interval == 0:
                    out = Path(input_file).parent / f"{Path(input_file).stem}_output{Path(input_file).suffix}"
                    _save_excel(df, str(out))
                    self._log(f"Progress saved ({found}/{processed} found)")

            out = Path(input_file).parent / f"{Path(input_file).stem}_output{Path(input_file).suffix}"
            _save_excel(df, str(out))

            self._log("=" * 50)
            self._log("COMPLETED")
            self._log(f"Processed: {processed}  |  Found: {found}  |  Not Found: {not_found}")
            self._log(f"Output: {out}")
            self._log("=" * 50)

            self.status_var.set("Completed!")
            messagebox.showinfo(
                "Complete",
                f"Done!\n\nProcessed: {processed}\nFound: {found}\n"
                f"Not Found: {not_found}\n\nOutput:\n{out}",
            )

        except Exception as exc:
            self._log(f"Error: {exc}")
            self.status_var.set("Error")
            messagebox.showerror("Error", str(exc))
        finally:
            if self.checker:
                self.checker.close()
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    try:
        root.iconbitmap("icon.ico")
    except tk.TclError:
        pass
    BilligerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
