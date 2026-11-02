"""
Auto Typer v2 - types whatever you put in the textbox into any window
(Word, Google Docs, Notepad, chat apps...).

Features
  - Speed slider + Slow / Normal / Fast presets, human-like timing
  - Pause / Resume, Esc to stop, F9 global hotkey (start/pause/resume at cursor)
  - Time estimate + progress bar
  - Repeat N times, Plain mode (straightens curly quotes/dashes)
  - Saved snippets, settings remembered between sessions
  - Open .txt / .md / .docx files
  - Grammar & spelling check (LanguageTool, free)
  - Right-click a word for synonyms (Datamuse, free)
  - AI suggestions (Claude API - needs your own API key, set in Settings)
  - Dark mode, always-on-top toggle

Run from source:  pip install pynput   then   python auto_typer.py
"""

import base64
import json
import os
import random
import sys
import threading
import time
import tkinter as tk
import traceback
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from tkinter import filedialog, messagebox, simpledialog, ttk

from pynput.keyboard import Controller, Key, Listener

APP_NAME = "Auto Typer"
HOTKEY = Key.f9
HOTKEY_LABEL = "F9"
CONFIG_DIR = (os.path.join(os.environ["APPDATA"], "AutoTyper") if os.environ.get("APPDATA")
              else os.path.join(os.path.expanduser("~"), ".autotyper"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_MODEL = "claude-sonnet-5-5"

DEFAULTS = {
    "wpm": 60, "humanize": True, "delay": 3, "repeat": 1, "plain": False,
    "dark": False, "topmost": True, "api_key": "", "model": DEFAULT_MODEL,
    "snippets": {}, "last_text": "",
}

PRESETS = {"Slow": 30, "Normal": 60, "Fast": 120}

PLAIN_MAP = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
    "​": "", "•": "-",
}

AI_ACTIONS = {
    "Fix grammar & spelling": "Correct the grammar, spelling and punctuation. Keep the wording and meaning otherwise the same.",
    "Improve clarity": "Rewrite it to be clearer and easier to read, keeping the meaning and the writer's voice.",
    "Better vocabulary": "Replace weak, vague or repeated words with stronger, more precise ones. Keep everything else the same.",
    "More formal": "Rewrite it in a more formal, professional tone.",
    "More casual": "Rewrite it in a more relaxed, conversational tone.",
    "Shorter": "Make it more concise without losing important points.",
    "Expand": "Expand it with more detail and explanation, keeping the same voice.",
    "Feedback only (no rewrite)": None,
}

ICON_PNG_B64 = "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"

THEMES = {
    "light": dict(bg="#f3f3f3", panel="#ffffff", fg="#1a1a1a", muted="#666666",
                  field="#ffffff", sel="#cfe0ff", accent="#5b8def", border="#cccccc",
                  err="#d93025"),
    "dark": dict(bg="#1e1f22", panel="#2b2d31", fg="#e6e6e6", muted="#9a9a9a",
                 field="#2b2d31", sel="#3d5a99", accent="#5b8def", border="#3a3c42",
                 err="#ff6b6b"),
}

keyboard = Controller()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def load_settings():
    s = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            s.update(json.load(f))
    except (OSError, ValueError):
        pass
    return s


def save_settings(s):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except OSError:
        pass


def plainify(text):
    for k, v in PLAIN_MAP.items():
        text = text.replace(k, v)
    return text


def read_docx(path):
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = []
    for p in root.iter(ns + "p"):
        parts = []
        for el in p.iter():
            if el.tag == ns + "t" and el.text:
                parts.append(el.text)
            elif el.tag == ns + "tab":
                parts.append("\t")
            elif el.tag in (ns + "br", ns + "cr"):
                parts.append("\n")
        paras.append("".join(parts))
    return "\n".join(paras)


def http_json(url, data=None, headers=None, timeout=30):
    body = None
    if isinstance(data, dict) and headers and headers.get("content-type") == "application/json":
        body = json.dumps(data).encode()
    elif isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {},
                                 method="POST" if body is not None else "GET")
    req.add_header("User-Agent", "AutoTyper/2.0")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fmt_duration(sec):
    sec = int(round(sec))
    if sec < 60:
        return f"{sec} sec"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m} min {s} sec"
    h, m = divmod(m, 60)
    return f"{h} hr {m} min"


# ---------------------------------------------------------------------------
# app
# ---------------------------------------------------------------------------
class AutoTyper:
    def __init__(self, root):
        self.root = root
        self.cfg = load_settings()

        # typing state
        self.state = "idle"            # idle | countdown | typing | paused
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pending_countdown = 0
        self.payload = ""
        self.pos = 0

        # grammar matches: tag -> (message, [replacements])
        self.matches = {}

        root.title(APP_NAME)
        root.geometry("900x640")
        root.minsize(720, 520)
        try:
            self._icon = tk.PhotoImage(data=ICON_PNG_B64)
            root.iconphoto(True, self._icon)
        except tk.TclError:
            pass

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Tk variables (mirrored to plain attributes for the typing thread)
        self.v_wpm = tk.IntVar(value=self.cfg["wpm"])
        self.v_humanize = tk.BooleanVar(value=self.cfg["humanize"])
        self.v_delay = tk.IntVar(value=self.cfg["delay"])
        self.v_repeat = tk.IntVar(value=self.cfg["repeat"])
        self.v_plain = tk.BooleanVar(value=self.cfg["plain"])
        self.v_dark = tk.BooleanVar(value=self.cfg["dark"])
        self.v_topmost = tk.BooleanVar(value=self.cfg["topmost"])
        self.wpm_now = self.cfg["wpm"]
        self.humanize_now = self.cfg["humanize"]

        self._build_ui()
        self.text.insert("1.0", self.cfg.get("last_text", ""))
        self.text.edit_modified(False)
        self._refresh_snippets()
        self.apply_theme()
        self.apply_topmost()
        self.update_estimate()

        for v in (self.v_wpm, self.v_humanize, self.v_repeat, self.v_plain):
            v.trace_add("write", lambda *a: self._on_setting_change())

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.listener = Listener(on_press=self._on_global_key)
        self.listener.daemon = True
        self.listener.start()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        root = self.root
        self.main = ttk.Frame(root, padding=10)
        self.main.pack(fill="both", expand=True)
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        # toolbar
        tb = ttk.Frame(self.main)
        tb.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(tb, text="Open file", command=self.open_file).pack(side="left")
        ttk.Button(tb, text="Check grammar", command=self.check_grammar).pack(side="left", padx=4)
        ttk.Button(tb, text="AI suggestions", command=self.open_ai_dialog).pack(side="left")
        ttk.Button(tb, text="Clear", command=self.clear_text).pack(side="left", padx=4)
        ttk.Button(tb, text="Settings", command=self.open_settings).pack(side="right")
        ttk.Checkbutton(tb, text="Dark mode", variable=self.v_dark,
                        command=self.apply_theme).pack(side="right", padx=8)
        ttk.Checkbutton(tb, text="Always on top", variable=self.v_topmost,
                        command=self.apply_topmost).pack(side="right")

        # text box
        box = ttk.Frame(self.main)
        box.grid(row=1, column=0, sticky="nsew")
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        self.text = tk.Text(box, wrap="word", font=("Segoe UI", 11), undo=True,
                            height=8, relief="flat", borderwidth=8)
        sb = ttk.Scrollbar(box, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Button-1>", self._on_text_click, add="+")
        self.text.bind("<Button-3>", self._on_right_click)

        # snippets panel
        sp = ttk.LabelFrame(self.main, text="Snippets", padding=6)
        sp.grid(row=1, column=1, sticky="ns", padx=(10, 0))
        self.snip_list = tk.Listbox(sp, width=24, height=12, activestyle="none",
                                    relief="flat", borderwidth=4, exportselection=False)
        self.snip_list.pack(fill="both", expand=True)
        self.snip_list.bind("<Double-Button-1>", lambda e: self.load_snippet())
        for label, cmd in (("Save current text", self.save_snippet),
                           ("Load into box", self.load_snippet),
                           ("Type it", self.type_snippet),
                           ("Delete", self.delete_snippet)):
            ttk.Button(sp, text=label, command=cmd).pack(fill="x", pady=(4, 0))

        # controls
        ctl = ttk.Frame(self.main)
        ctl.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ctl.columnconfigure(1, weight=1)

        ttk.Label(ctl, text="Speed:").grid(row=0, column=0, sticky="w")
        ttk.Scale(ctl, from_=10, to=600, variable=self.v_wpm,
                  command=lambda v: self.v_wpm.set(int(float(v)))
                  ).grid(row=0, column=1, sticky="ew", padx=8)
        self.wpm_label = ttk.Label(ctl, width=8)
        self.wpm_label.grid(row=0, column=2)
        pf = ttk.Frame(ctl)
        pf.grid(row=0, column=3, padx=(8, 0))
        for name, val in PRESETS.items():
            ttk.Button(pf, text=name, width=7,
                       command=lambda v=val: self.v_wpm.set(v)).pack(side="left", padx=1)

        opts = ttk.Frame(ctl)
        opts.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Checkbutton(opts, text="Human-like timing", variable=self.v_humanize).pack(side="left")
        ttk.Checkbutton(opts, text="Plain mode (straight quotes)",
                        variable=self.v_plain).pack(side="left", padx=12)
        ttk.Label(opts, text="Repeat:").pack(side="left")
        ttk.Spinbox(opts, from_=1, to=999, width=5, textvariable=self.v_repeat
                    ).pack(side="left", padx=(4, 12))
        ttk.Label(opts, text="Start delay (sec):").pack(side="left")
        ttk.Spinbox(opts, from_=0, to=30, width=5, textvariable=self.v_delay
                    ).pack(side="left", padx=4)

        btns = ttk.Frame(ctl)
        btns.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self.start_btn = ttk.Button(btns, text="Start", command=self.on_start_button)
        self.start_btn.pack(side="left")
        self.pause_btn = ttk.Button(btns, text="Pause", command=self.pause, state="disabled")
        self.pause_btn.pack(side="left", padx=6)
        self.stop_btn = ttk.Button(btns, text="Stop (Esc)", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left")
        ttk.Label(btns, text=f"   {HOTKEY_LABEL} = start / pause / resume at your cursor",
                  style="Muted.TLabel").pack(side="left")

        pr = ttk.Frame(ctl)
        pr.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        pr.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(pr, mode="determinate", maximum=1)
        self.progress.grid(row=0, column=0, sticky="ew")
        self.estimate_label = ttk.Label(pr, width=34, anchor="e")
        self.estimate_label.grid(row=0, column=1, padx=(10, 0))

        self.status = ttk.Label(ctl, text="Ready.", style="Muted.TLabel")
        self.status.grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))

    # --------------------------------------------------------------- theme
    def apply_theme(self):
        t = THEMES["dark" if self.v_dark.get() else "light"]
        s = self.style
        self.root.configure(bg=t["bg"])
        s.configure(".", background=t["bg"], foreground=t["fg"], fieldbackground=t["field"],
                    bordercolor=t["border"], lightcolor=t["bg"], darkcolor=t["bg"],
                    troughcolor=t["panel"], focuscolor=t["accent"])
        s.configure("TButton", background=t["panel"], padding=(10, 4))
        s.map("TButton", background=[("active", t["sel"]), ("disabled", t["bg"])],
              foreground=[("disabled", t["muted"])])
        s.configure("TCheckbutton", background=t["bg"], indicatorbackground=t["field"])
        s.map("TCheckbutton", background=[("active", t["bg"])],
              indicatorbackground=[("selected", t["accent"])])
        s.configure("TLabelframe", background=t["bg"], bordercolor=t["border"])
        s.configure("TLabelframe.Label", background=t["bg"], foreground=t["fg"])
        s.configure("TSpinbox", fieldbackground=t["field"], foreground=t["fg"],
                    arrowcolor=t["fg"], background=t["panel"])
        s.configure("Horizontal.TProgressbar", background=t["accent"], troughcolor=t["panel"])
        s.configure("Horizontal.TScale", background=t["accent"], troughcolor=t["panel"])
        s.configure("Muted.TLabel", foreground=t["muted"])
        s.configure("Vertical.TScrollbar", background=t["panel"], arrowcolor=t["fg"],
                    troughcolor=t["bg"])
        self.text.configure(bg=t["field"], fg=t["fg"], insertbackground=t["fg"],
                            selectbackground=t["sel"], selectforeground=t["fg"])
        self.snip_list.configure(bg=t["field"], fg=t["fg"], selectbackground=t["sel"],
                                 selectforeground=t["fg"], highlightthickness=0)
        for tag in self.matches:
            self.text.tag_configure(tag, underline=True, foreground=t["err"])
        self.theme = t
        self.cfg["dark"] = self.v_dark.get()

    def apply_topmost(self):
        self.root.attributes("-topmost", self.v_topmost.get())
        self.cfg["topmost"] = self.v_topmost.get()

    def make_menu(self):
        t = self.theme
        return tk.Menu(self.root, tearoff=0, bg=t["panel"], fg=t["fg"],
                       activebackground=t["sel"], activeforeground=t["fg"],
                       disabledforeground=t["muted"])

    # ------------------------------------------------------------- helpers
    def set_status(self, msg):
        self.root.after(0, lambda: self.status.config(text=msg))

    def get_text(self):
        return self.text.get("1.0", "end-1c")

    def _on_text_modified(self, _e=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.update_estimate()

    def _on_setting_change(self):
        try:
            self.wpm_now = max(int(self.v_wpm.get()), 1)
        except (tk.TclError, ValueError):
            pass
        self.humanize_now = self.v_humanize.get()
        self.update_estimate()

    def _build_payload(self):
        text = self.get_text()
        if self.v_plain.get():
            text = plainify(text)
        try:
            n = max(1, int(self.v_repeat.get()))
        except (tk.TclError, ValueError):
            n = 1
        sep = "" if text.endswith(("\n", " ")) else "\n"
        return sep.join([text] * n) if n > 1 else text

    def _mean_delay(self, ch, base):
        if not self.humanize_now:
            return base
        extra = 4.5 if ch in ".!?" else 2 if ch in ",;:" else 6 if ch == "\n" else 0
        return base * (1 + extra)

    def update_estimate(self):
        try:
            wpm = max(int(self.v_wpm.get()), 1)
        except (tk.TclError, ValueError):
            wpm = 60
        self.wpm_label.config(text=f"{wpm} WPM")
        payload = self.payload if self.state != "idle" else self._build_payload()
        start = self.pos if self.state != "idle" else 0
        base = 60.0 / (wpm * 5)
        rest = payload[start:]
        secs = sum(self._mean_delay(c, base) for c in rest)
        n = len(payload)
        if self.state == "idle":
            self.estimate_label.config(text=f"{n:,} chars  ~ {fmt_duration(secs)}")
        else:
            self.estimate_label.config(text=f"{self.pos:,}/{n:,}  ~ {fmt_duration(secs)} left")

    def _delay_for(self, ch):
        base = 60.0 / (self.wpm_now * 5)
        if not self.humanize_now:
            return base
        d = base * random.uniform(0.5, 1.5)
        if ch in ".!?":
            d += base * random.uniform(3, 6)
        elif ch in ",;:":
            d += base * random.uniform(1, 3)
        elif ch == "\n":
            d += base * random.uniform(4, 8)
        return d

    def _set_buttons(self):
        st = self.state
        def upd():
            self.start_btn.config(text="Resume" if st == "paused" else "Start",
                                  state="disabled" if st in ("typing", "countdown") else "normal")
            self.pause_btn.config(state="normal" if st == "typing" else "disabled")
            self.stop_btn.config(state="disabled" if st == "idle" else "normal")
        self.root.after(0, upd)

    # --------------------------------------------------------- typing core
    def on_start_button(self):
        # clicking the button moves focus to this window, so always count down
        if self.state == "paused":
            self.resume(countdown=True)
        elif self.state == "idle":
            self.start(countdown=True)

    def start(self, countdown=True, text=None):
        if self.state != "idle":
            return
        payload = text if text is not None else self._build_payload()
        if not payload:
            self.set_status("Nothing to type - the box is empty.")
            return
        self.payload, self.pos = payload, 0
        self.stop_event.clear()
        self.pause_event.clear()
        try:
            self.pending_countdown = max(0, int(self.v_delay.get())) if countdown else 0
        except (tk.TclError, ValueError):
            self.pending_countdown = 3 if countdown else 0
        self.state = "countdown"
        self.root.after(0, lambda: self.progress.config(maximum=len(payload), value=0))
        self._set_buttons()
        threading.Thread(target=self._type_loop, daemon=True).start()

    def pause(self):
        if self.state == "typing":
            self.pause_event.set()
            self.state = "paused"
            self._set_buttons()
            self.set_status(f"Paused at {self.pos}/{len(self.payload)}. "
                            f"Click Resume, or put your cursor back and press {HOTKEY_LABEL}.")

    def resume(self, countdown=True):
        if self.state != "paused":
            return
        try:
            self.pending_countdown = max(0, int(self.v_delay.get())) if countdown else 0
        except (tk.TclError, ValueError):
            self.pending_countdown = 3 if countdown else 0
        self.state = "countdown"
        self._set_buttons()
        self.pause_event.clear()

    def stop(self):
        if self.state != "idle":
            self.stop_event.set()
            self.pause_event.clear()

    def _countdown(self, secs):
        for s in range(secs, 0, -1):
            self.set_status(f"Starting in {s}... click where you want to type.")
            end = time.time() + 1
            while time.time() < end:
                if self.stop_event.is_set():
                    return False
                time.sleep(0.05)
        return True

    def _type_loop(self):
        total = len(self.payload)
        while self.pos < total:
            if self.stop_event.is_set():
                break
            if self.pause_event.is_set():
                time.sleep(0.05)
                continue
            if self.pending_countdown:
                n, self.pending_countdown = self.pending_countdown, 0
                if not self._countdown(n):
                    break
            if self.state == "countdown":
                self.state = "typing"
                self._set_buttons()

            ch = self.payload[self.pos]
            if ch == "\n":
                keyboard.tap(Key.enter)
            elif ch == "\t":
                keyboard.tap(Key.tab)
            else:
                keyboard.type(ch)
            self.pos += 1

            if self.pos % 5 == 0 or self.pos == total:
                p = self.pos
                self.root.after(0, lambda p=p: (self.progress.config(value=p),
                                                self.update_estimate()))
                self.set_status(f"Typing... {p}/{total}  (Esc stop, {HOTKEY_LABEL} pause)")

            end = time.time() + self._delay_for(ch)
            while time.time() < end and not self.stop_event.is_set() \
                    and not self.pause_event.is_set():
                time.sleep(min(0.05, max(0.0, end - time.time())))

        done = self.pos >= total and not self.stop_event.is_set()
        msg = (f"Done! Typed {total:,} characters." if done
               else f"Stopped at {self.pos:,}/{total:,} characters.")
        self.state = "idle"
        self.payload, self.pos = "", 0
        self._set_buttons()
        self.set_status(msg)
        self.root.after(0, lambda: (self.progress.config(value=self.progress["maximum"] if done else 0),
                                    self.update_estimate()))

    def _on_global_key(self, key):
        if key == Key.esc and self.state != "idle":
            self.stop()
        elif key == HOTKEY:
            # hotkey acts at the current cursor - no countdown needed
            if self.state == "idle":
                self.root.after(0, self._hotkey_start)
            elif self.state == "typing":
                self.pause()
            elif self.state == "paused":
                self.resume(countdown=False)

    def _hotkey_start(self):
        # don't type into our own window - the user must be in the target app
        if self.root.focus_displayof() is not None:
            self.set_status(f"Click into the app you want to type in, then press {HOTKEY_LABEL}.")
            return
        self.start(countdown=False)

    # ------------------------------------------------------------ snippets
    def _refresh_snippets(self):
        self.snip_list.delete(0, "end")
        for name in sorted(self.cfg["snippets"], key=str.lower):
            self.snip_list.insert("end", name)

    def _selected_snippet(self):
        sel = self.snip_list.curselection()
        if not sel:
            self.set_status("Pick a snippet in the list first.")
            return None
        return self.snip_list.get(sel[0])

    def save_snippet(self):
        text = self.get_text()
        if not text.strip():
            self.set_status("Type something in the box first, then save it as a snippet.")
            return
        name = simpledialog.askstring("Save snippet", "Name for this snippet:", parent=self.root)
        if not name:
            return
        name = name.strip()
        if name in self.cfg["snippets"] and not messagebox.askyesno(
                "Replace?", f'A snippet called "{name}" exists. Replace it?', parent=self.root):
            return
        self.cfg["snippets"][name] = text
        save_settings(self.cfg)
        self._refresh_snippets()
        self.set_status(f'Saved snippet "{name}".')

    def load_snippet(self):
        name = self._selected_snippet()
        if name:
            self.text.delete("1.0", "end")
            self.text.insert("1.0", self.cfg["snippets"][name])
            self.set_status(f'Loaded "{name}".')

    def type_snippet(self):
        name = self._selected_snippet()
        if name and self.state == "idle":
            self.load_snippet()
            self.start(countdown=True)

    def delete_snippet(self):
        name = self._selected_snippet()
        if name and messagebox.askyesno("Delete snippet", f'Delete "{name}"?', parent=self.root):
            self.cfg["snippets"].pop(name, None)
            save_settings(self.cfg)
            self._refresh_snippets()

    # --------------------------------------------------------------- files
    def open_file(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Open a file",
            filetypes=[("Text & Word files", "*.txt *.md *.docx"), ("All files", "*.*")])
        if not path:
            return
        try:
            if path.lower().endswith(".docx"):
                content = read_docx(path)
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Couldn't open file", str(e), parent=self.root)
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.set_status(f"Opened {os.path.basename(path)}")

    def clear_text(self):
        self.text.delete("1.0", "end")
        self._clear_grammar()

    # ------------------------------------------------------------- grammar
    def _clear_grammar(self):
        for tag in list(self.matches):
            self.text.tag_delete(tag)
        self.matches.clear()

    def check_grammar(self):
        text = self.get_text()
        if not text.strip():
            self.set_status("Nothing to check.")
            return
        if len(text) > 18000:
            self.set_status("Text is too long for the free checker (about 18,000 characters max).")
            return
        self.set_status("Checking grammar and spelling...")

        def work():
            try:
                res = http_json("https://api.languagetool.org/v2/check",
                                data={"text": text, "language": "en-US"}, timeout=30)
                self.root.after(0, lambda: self._show_grammar(text, res.get("matches", [])))
            except Exception as e:  # noqa: BLE001
                self.set_status(f"Grammar check failed: {e}")
        threading.Thread(target=work, daemon=True).start()

    def _show_grammar(self, checked_text, matches):
        if self.get_text() != checked_text:
            self.set_status("Text changed while checking - click Check grammar again.")
            return
        self._clear_grammar()
        for i, m in enumerate(matches):
            tag = f"gerr{i}"
            start = f"1.0 + {m['offset']} chars"
            end = f"1.0 + {m['offset'] + m['length']} chars"
            self.text.tag_add(tag, start, end)
            self.text.tag_configure(tag, underline=True, foreground=self.theme["err"])
            reps = [r["value"] for r in m.get("replacements", [])[:6]]
            self.matches[tag] = (m.get("message", "Possible issue"), reps)
        n = len(matches)
        self.set_status("No issues found!" if n == 0 else
                        f"Found {n} possible issue{'s' if n != 1 else ''} - click underlined text to fix.")

    def _on_text_click(self, event):
        idx = self.text.index(f"@{event.x},{event.y}")
        tags = [t for t in self.text.tag_names(idx) if t in self.matches]
        if not tags:
            return
        tag = tags[0]
        msg, reps = self.matches[tag]
        menu = self.make_menu()
        menu.add_command(label=msg[:90], state="disabled")
        menu.add_separator()
        for r in reps:
            menu.add_command(label=r if r.strip() else "(remove)",
                             command=lambda r=r, t=tag: self._apply_fix(t, r))
        if not reps:
            menu.add_command(label="(no suggestion)", state="disabled")
        menu.add_separator()
        menu.add_command(label="Ignore", command=lambda t=tag: self._ignore_fix(t))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _apply_fix(self, tag, replacement):
        rng = self.text.tag_ranges(tag)
        if rng:
            self.text.delete(rng[0], rng[1])
            self.text.insert(rng[0], replacement)
        self._ignore_fix(tag)

    def _ignore_fix(self, tag):
        self.text.tag_delete(tag)
        self.matches.pop(tag, None)

    # ---------------------------------------------------------- vocabulary
    def _on_right_click(self, event):
        try:
            start, end = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            idx = self.text.index(f"@{event.x},{event.y}")
            start, end = self.text.index(f"{idx} wordstart"), self.text.index(f"{idx} wordend")
        word = self.text.get(start, end).strip()
        menu = self.make_menu()
        menu.add_command(label="Cut", command=lambda: self.text.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self.text.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self.text.event_generate("<<Paste>>"))
        if not word or not any(c.isalpha() for c in word) or len(word) > 40:
            menu.tk_popup(event.x_root, event.y_root)
            return "break"
        self.text.mark_set("vstart", start)
        self.text.mark_set("vend", end)
        self.text.mark_gravity("vstart", "left")
        self.text.mark_gravity("vend", "right")
        self.set_status(f'Looking up words like "{word}"...')
        x, y = event.x_root, event.y_root

        def work():
            try:
                q = urllib.parse.quote(word)
                res = http_json(f"https://api.datamuse.com/words?ml={q}&max=12", timeout=8)
                syns = [r["word"] for r in res]
            except Exception:  # noqa: BLE001
                syns = None
            self.root.after(0, lambda: show(syns))

        def show(syns):
            menu.add_separator()
            if syns is None:
                menu.add_command(label="(couldn't load synonyms)", state="disabled")
            elif not syns:
                menu.add_command(label="(no synonyms found)", state="disabled")
            else:
                menu.add_command(label=f'Replace "{word}" with:', state="disabled")
                for s in syns:
                    s2 = s.capitalize() if word[:1].isupper() else s
                    menu.add_command(label=s2, command=lambda s2=s2: self._replace_word(s2))
            self.set_status("Ready.")
            menu.tk_popup(x, y)

        threading.Thread(target=work, daemon=True).start()
        return "break"

    def _replace_word(self, new):
        self.text.delete("vstart", "vend")
        self.text.insert("vstart", new)

    # ------------------------------------------------------------------ AI
    def open_ai_dialog(self):
        if not self.cfg.get("api_key"):
            if messagebox.askyesno(
                    "API key needed",
                    "AI suggestions need a Claude API key.\n\nOpen Settings to add one?",
                    parent=self.root):
                self.open_settings()
            return
        try:
            sel = (self.text.index("sel.first"), self.text.index("sel.last"))
        except tk.TclError:
            sel = None
        src = self.text.get(*sel) if sel else self.get_text()
        if not src.strip():
            self.set_status("Put some text in the box (or select part of it) first.")
            return
        if sel:
            self.text.mark_set("ai_start", sel[0])
            self.text.mark_set("ai_end", sel[1])
            self.text.mark_gravity("ai_start", "left")
            self.text.mark_gravity("ai_end", "right")

        t = self.theme
        win = tk.Toplevel(self.root)
        win.title("AI suggestions")
        win.geometry("640x520")
        win.configure(bg=t["bg"])
        win.attributes("-topmost", self.v_topmost.get())
        win.transient(self.root)
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(fill="x")
        ttk.Label(top, text="What should the AI do?").pack(side="left")
        action = tk.StringVar(value=list(AI_ACTIONS)[0])
        ttk.Combobox(top, textvariable=action, values=list(AI_ACTIONS), state="readonly",
                     width=28).pack(side="left", padx=6)
        go = ttk.Button(top, text="Generate")
        go.pack(side="left")
        ttk.Label(frm, text=("Working on: your selected text" if sel else "Working on: the whole text box"),
                  style="Muted.TLabel").pack(anchor="w", pady=(6, 4))

        out = tk.Text(frm, wrap="word", font=("Segoe UI", 11), relief="flat", borderwidth=8,
                      bg=t["field"], fg=t["fg"], insertbackground=t["fg"], height=10)
        out.pack(fill="both", expand=True)

        bot = ttk.Frame(frm)
        bot.pack(fill="x", pady=(8, 0))
        status = ttk.Label(bot, text="Pick an option and click Generate.", style="Muted.TLabel")
        status.pack(side="left")
        ttk.Button(bot, text="Close", command=win.destroy).pack(side="right")
        copy_btn = ttk.Button(bot, text="Copy", state="disabled",
                              command=lambda: (win.clipboard_clear(),
                                               win.clipboard_append(out.get("1.0", "end-1c"))))
        copy_btn.pack(side="right", padx=4)
        use_btn = ttk.Button(bot, text="Use this", state="disabled")
        use_btn.pack(side="right")

        def use():
            new = out.get("1.0", "end-1c")
            if sel:
                self.text.delete("ai_start", "ai_end")
                self.text.insert("ai_start", new)
            else:
                self.text.delete("1.0", "end")
                self.text.insert("1.0", new)
            self._clear_grammar()
            win.destroy()
            self.set_status("AI text placed in the box.")
        use_btn.config(command=use)

        def generate():
            act = action.get()
            instr = AI_ACTIONS[act]
            if instr is None:
                system = ("You are a helpful writing coach. Give short, specific, bulleted "
                          "suggestions to improve the text (grammar, clarity, word choice, "
                          "structure). Do not rewrite the whole thing.")
                user = f"Give feedback on this text:\n\n{src}"
            else:
                system = ("You are a careful writing assistant. Reply with ONLY the revised "
                          "text - no intro, no notes, no quotation marks around it.")
                user = f"{instr}\n\nText:\n{src}"
            go.config(state="disabled")
            use_btn.config(state="disabled")
            status.config(text="Thinking...")

            def work():
                try:
                    res = http_json(
                        "https://api.anthropic.com/v1/messages",
                        data={"model": self.cfg.get("model") or DEFAULT_MODEL,
                              "max_tokens": 4000, "system": system,
                              "messages": [{"role": "user", "content": user}]},
                        headers={"content-type": "application/json",
                                 "x-api-key": self.cfg["api_key"],
                                 "anthropic-version": "2023-06-01"},
                        timeout=120)
                    txt = "".join(b.get("text", "") for b in res.get("content", [])
                                  if b.get("type") == "text").strip()
                    err = None
                except urllib.error.HTTPError as e:
                    txt = ""
                    try:
                        err = json.loads(e.read().decode()).get("error", {}).get("message", str(e))
                    except Exception:  # noqa: BLE001
                        err = str(e)
                except Exception as e:  # noqa: BLE001
                    txt, err = "", str(e)

                def done():
                    if not win.winfo_exists():
                        return
                    go.config(state="normal")
                    if err:
                        status.config(text=f"Error: {err[:90]}")
                        return
                    out.delete("1.0", "end")
                    out.insert("1.0", txt)
                    copy_btn.config(state="normal")
                    if instr is not None:
                        use_btn.config(state="normal")
                    status.config(text="Edit it if you like, then click Use this." if instr
                                  else "Feedback ready.")
                self.root.after(0, done)
            threading.Thread(target=work, daemon=True).start()
        go.config(command=generate)

    # ------------------------------------------------------------ settings
    def open_settings(self):
        t = self.theme
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=t["bg"])
        win.attributes("-topmost", self.v_topmost.get())
        win.transient(self.root)
        win.resizable(False, False)
        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Claude API key (for AI suggestions):").grid(row=0, column=0, sticky="w")
        key = tk.StringVar(value=self.cfg.get("api_key", ""))
        key_entry = ttk.Entry(frm, textvariable=key, width=48, show="*")
        key_entry.grid(row=1, column=0, sticky="ew", pady=(2, 2))
        show = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Show", variable=show,
                        command=lambda: key_entry.config(show="" if show.get() else "*")
                        ).grid(row=1, column=1, padx=6)
        ttk.Label(frm, text="Get one at console.anthropic.com > API Keys. "
                            "It's saved on this PC only.",
                  style="Muted.TLabel").grid(row=2, column=0, columnspan=2, sticky="w")

        ttk.Label(frm, text="AI model:").grid(row=3, column=0, sticky="w", pady=(12, 0))
        model = tk.StringVar(value=self.cfg.get("model", DEFAULT_MODEL))
        ttk.Entry(frm, textvariable=model, width=48).grid(row=4, column=0, sticky="ew")

        ttk.Label(frm, text=f"Hotkeys: {HOTKEY_LABEL} start/pause/resume at cursor  -  Esc stop",
                  style="Muted.TLabel").grid(row=5, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Label(frm, text=f"Settings file: {CONFIG_PATH}",
                  style="Muted.TLabel").grid(row=6, column=0, columnspan=2, sticky="w")

        def save():
            self.cfg["api_key"] = key.get().strip()
            self.cfg["model"] = model.get().strip() or DEFAULT_MODEL
            save_settings(self.cfg)
            win.destroy()
            self.set_status("Settings saved.")
        b = ttk.Frame(frm)
        b.grid(row=7, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(b, text="Cancel", command=win.destroy).pack(side="right")
        ttk.Button(b, text="Save", command=save).pack(side="right", padx=6)

    # --------------------------------------------------------------- close
    def on_close(self):
        self.stop()
        try:
            self.cfg.update(wpm=int(self.v_wpm.get()), humanize=self.v_humanize.get(),
                            delay=int(self.v_delay.get()), repeat=int(self.v_repeat.get()),
                            plain=self.v_plain.get(), dark=self.v_dark.get(),
                            topmost=self.v_topmost.get())
        except (tk.TclError, ValueError):
            pass
        self.cfg["last_text"] = self.get_text()[:100000]
        save_settings(self.cfg)
        self.root.destroy()


def _crash_log_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        AutoTyper(root)
        root.mainloop()
    except Exception:  # noqa: BLE001
        with open(os.path.join(_crash_log_dir(), "auto_typer_error.txt"), "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        try:
            messagebox.showerror(APP_NAME, "Auto Typer crashed. Details were saved to "
                                           "auto_typer_error.txt next to the app.")
        except Exception:  # noqa: BLE001
            pass
