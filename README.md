# Auto Typer

A desktop app that types out any text you give it into whatever window is active (Word, Google Docs, Notepad, chat apps, and so on), at a speed you choose.

Built with Python, Tkinter and [pynput](https://github.com/moses-palmer/pynput).

## Features

- **Adjustable speed**: 10–600 WPM slider, plus Slow / Normal / Fast presets
- **Human-like timing**: random variation, with pauses after punctuation and new lines
- **Pause / Resume / Stop**: press **F9** to start, pause or resume at your cursor; press **Esc** to stop
- **Time estimate and progress bar**
- **Repeat** the text any number of times
- **Plain mode**: turns curly quotes, long dashes and ellipses into plain characters
- **Snippets**: save text you use often and type it with one click
- **Open files**: load `.txt`, `.md` or `.docx`
- **Grammar and spelling check**: uses the free [LanguageTool](https://languagetool.org) API; click an underlined mistake to fix it
- **Synonyms**: right-click a word for alternatives, from the free [Datamuse](https://www.datamuse.com/api/) API
- **AI suggestions** (optional): fix grammar, improve clarity, change tone, shorten, expand, or get feedback, using the Claude API with your own key
- **Dark mode** and an **always-on-top** toggle
- Settings are saved between sessions

## Getting started

### Option 1: download the app (Windows)
Download `Auto Typer.exe` from the [Releases](../../releases) page and double-click it. You don't need Python.

### Option 2: run from source (Windows, macOS, Linux)
```bash
pip install -r requirements.txt
python auto_typer.py
```

On **macOS**, give your terminal (or the app) permission under System Settings → Privacy & Security → **Accessibility** and **Input Monitoring**.

### Build the Windows .exe yourself
Double-click `build_windows.bat`. The app is saved to `dist\Auto Typer.exe`.

## How to use

1. Paste your text into the box and choose a speed.
2. Click **Start**, then click into the app you want to type in before the countdown ends.
   *Or* put your cursor where you want the text and press **F9**.
3. Press **F9** to pause or resume, and **Esc** to stop.

**Tip:** Word and Google Docs may auto-format as the text is typed (numbered lists, smart quotes). You can turn this off in Word's AutoCorrect options or under Docs → Tools → Preferences.

## AI suggestions setup

1. Create an API key at [console.anthropic.com](https://console.anthropic.com).
2. In Auto Typer, open **Settings**, paste the key, and click **Save**.

The key is stored only on your computer, in your user settings folder (`%APPDATA%\AutoTyper\settings.json` on Windows, `~/.autotyper/` on macOS and Linux), and it is **never** stored in this repository.

## Privacy

- Typing happens entirely on your computer.
- The grammar check, synonyms and AI suggestions send the text you check to LanguageTool, Datamuse or Anthropic, and only when you use those buttons.

## Limitations

- It doesn't work on phones, tablets or Chromebooks, because those systems don't let one app type into another.
- Apps running as administrator won't receive the keystrokes unless Auto Typer also runs as administrator.
- Some antivirus programs flag apps that send keystrokes. If yours does, allow the file.

## License

[MIT](LICENSE)
