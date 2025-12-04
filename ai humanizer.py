import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import unicodedata

_INVISIBLE_CHARS = ['\u200b', '\u200d', '\u2060']

# small set of common words to avoid over-simplifying very short/ordinary tokens
_COMMON_WORDS = set("""
the be and of a in to have it I that for you he with on do say this they at but we his from
not by she or as what go their can who get if would her all my make about know will as up one
time there year so think when which them some me people take out into just see him your come could
now than like other how then its our two more these want way look first also new because day more
use no man find here thing give many well only those tell very even back any good woman through
us life child
""".split())

# hedging / filler phrases that humanizers typically strip
_FILLER_PHRASES = [
    "it should be noted that",
    "it is important to note that",
    "in order to",
    "at this point in time",
    "at the end of the day",
    "for the purpose of",
    "to a certain extent",
    "as previously mentioned",
    "for the avoidance of doubt",
    "in the event that",
    "with respect to",
    "in terms of",
    "in relation to",
    "by means of",
    "for the most part",
    "in many cases",
    "there is a need to",
    "it is worth noting that",
]

# contractions to prefer (simple, safe set)
_CONTRACTIONS = {
    "do not": "don't",
    "does not": "doesn't",
    "did not": "didn't",
    "cannot": "can't",
    "can not": "can't",
    "will not": "won't",
    "is not": "isn't",
    "are not": "aren't",
    "were not": "weren't",
    "has not": "hasn't",
    "have not": "haven't",
    "had not": "hadn't",
    "it is": "it's",
    "that is": "that's",
    "there is": "there's",
    "I am": "I'm",
    "we are": "we're",
    "they are": "they're",
    "you are": "you're",
    "I have": "I've",
}

# simple list of conjunctions to use when breaking long sentences
_CONJUNCTIONS = [",", ";", " and ", " but ", " however ", " although ", " because ", " therefore "]


def _preserve_case(orig: str, new: str) -> str:
    if orig.isupper():
        return new.upper()
    if orig and orig[0].isupper():
        return new.capitalize()
    return new


def ultra_clean(text: str) -> str:
    """Keep basic normalization, invisibles removal, punctuation fixes, and trimming."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', text)
    for ch in _INVISIBLE_CHARS:
        text = text.replace(ch, '')
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'-\s*\n\s*', '', text)  # join hyphenated breaks
    paragraphs = re.split(r'\n\s*\n', text)
    cleaned = []
    for p in paragraphs:
        p = ' '.join(ln.strip() for ln in p.splitlines() if ln.strip())
        p = re.sub(r'<[^>]+>', '', p)
        p = p.replace('&nbsp;', ' ').replace('&amp;', '&')
        p = p.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        p = re.sub(r'[–—−]', '-', p)
        p = re.sub(r'\.{2,}', '.', p)
        p = re.sub(r'([A-Za-z])\1{3,}', r'\1\1\1', p)
        p = re.sub(r'([!?]){2,}', r'\1', p)
        p = re.sub(r'\s*-\s*', ' - ', p)
        p = re.sub(r'\s+([,;:.!?%)\]])', r'\1', p)
        p = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), p)
        cleaned.append(p.strip())
    result = '\n\n'.join(cleaned)
    result = re.sub(r'\s{2,}', ' ', result)
    return result[0].upper() + result[1:] if result else result


def _split_sentences(text: str):
    # naive sentence split that keeps punctuation
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _shorten_long_sentence(sent: str) -> list:
    """Break a long sentence into shorter ones using commas, semicolons, and conjunctions."""
    if len(sent) <= 120:
        return [sent]
    # try to split at semicolons or long commas first
    for sep in [ ';', ', and ', ', but ', ', which ', ', which,', ',']:
        if sep in sent:
            pieces = [s.strip() for s in sent.split(sep) if s.strip()]
            # reattach potential trailing punctuation to pieces and ensure they end with a period
            out = []
            for i, pc in enumerate(pieces):
                if not re.search(r'[.!?]$', pc):
                    pc = pc.rstrip(',; ')
                    if i < len(pieces) - 1:
                        pc = pc + '.'
                out.append(pc)
            # if resulting pieces are reasonable length, return them
            if all(len(p) <= 160 for p in out) and len(out) <= 5:
                return out
    # fallback: hard split roughly in half on spaces
    words = sent.split()
    mid = len(words) // 2
    a = ' '.join(words[:mid]).rstrip(' ,;:')
    b = ' '.join(words[mid:]).capitalize()
    return [a + '.', b]


def _remove_fillers(sentence: str) -> str:
    s = sentence
    for ph in _FILLER_PHRASES:
        s = re.sub(r'\b' + re.escape(ph) + r'\b', '', s, flags=re.I)
    # common verbose connectors
    s = re.sub(r'\b(?:therefore|thus|hence|consequently|subsequently)\b', 'so', s, flags=re.I)
    s = re.sub(r'\b(?:in the event that|in case)\b', 'if', s, flags=re.I)
    s = re.sub(r'\b(?:prior to)\b', 'before', s, flags=re.I)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def _apply_contractions(sentence: str) -> str:
    s = sentence
    # contract only common phrases and avoid contracting when uppercase emphasis is present
    for long, short in _CONTRACTIONS.items():
        s = re.sub(r'\b' + re.escape(long) + r'\b', short, s, flags=re.I)
    return s


def _simplify_words(sentence: str) -> str:
    """
    Heuristic simplification:
    - If a word looks rare/long and not in _COMMON_WORDS, try to make it shorter:
      - Strip common nominalization suffixes when safe.
    - Avoid touching short common words.
    """
    def simplify_token(tok):
        core = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', tok)
        if not core:
            return tok
        if core.lower() in _COMMON_WORDS or len(core) <= 7:
            return tok
        lw = core.lower()
        # suffix heuristics
        if lw.endswith('ization'):
            new = core[:-7] + 'ize'
        elif lw.endswith('isation'):
            new = core[:-7] + 'ise'
        elif lw.endswith('izational'):
            new = core[:-10] + 'ize'
        elif lw.endswith('mentation'):
            new = core[:-9]
        elif lw.endswith('ization'):
            new = core[:-7] + 'ize'
        elif lw.endswith('ment') and len(core) > 8:
            new = core[:-4]
        elif lw.endswith('tion') and len(core) > 8:
            # try to get a verb-like stem: creation -> create, computation -> compute
            if lw.endswith('ation'):
                new = core[:-5] + 'e'
            else:
                new = core[:-4] + 'e'
        elif lw.endswith('ness') and len(core) > 8:
            new = core[:-4]
        elif lw.endswith('ity') and len(core) > 8:
            new = core[:-3]
        else:
            # try to split camelCase or hyphenated compounds
            if '-' in core:
                parts = core.split('-')
                # keep only the most meaningful short part
                parts = [p for p in parts if len(p) > 3]
                new = parts[0] if parts else core
            elif re.search(r'[A-Z][a-z]+', core):
                # camel case -> split into words
                parts = re.findall(r'[A-Z]?[a-z]+', core)
                new = ' '.join(parts)
            else:
                # as last resort, shorten by truncating to the first 8 letters
                new = core[:8]
        # preserve original punctuation/Case
        if core.istitle():
            new = new.capitalize()
        elif core.isupper():
            new = new.upper()
        # put back surrounding punctuation
        return tok.replace(core, new, 1)
    tokens = re.split(r'(\s+)', sentence)
    return ''.join(simplify_token(t) if not t.isspace() else t for t in tokens)


def _try_rewrite_passive(sentence: str) -> str:
    """
    Very conservative passive-to-active rewrites when pattern "X was VERBed by Y" is found.
    Produces "Y did VERB-base X" (grammatical though sometimes blunt), preserving capitalization.
    """
    pattern = re.compile(
        r'(?P<subj>[\w\-,\s]+?)\s+(?P<aux>was|were|is|are|been|being|has been|have been|had been|was being|were being)\s+'
        r'(?P<verb>\w+(?:ed|en|n)?)\s+by\s+(?P<agent>[\w\-,\s]+)',
        flags=re.I
    )
    def repl(m):
        subj = m.group('subj').strip(' ,')
        agent = m.group('agent').strip(' ,')
        verb = m.group('verb').strip()
        # heuristic base form
        base = verb
        if verb.lower().endswith('ed') and len(verb) > 3:
            base = verb[:-2]
        elif verb.lower().endswith('en') or verb.lower().endswith('n'):
            base = verb[:-1]
        base = base.lower()
        # produce "Agent did base subj"
        out = f"{agent.strip().capitalize()} did {base} {subj.strip().lower()}"
        # keep trailing period if original had it
        return out
    new = pattern.sub(repl, sentence)
    return new


def humanize_text(text: str) -> str:
    """
    Apply multiple heuristic, algorithmic passes to make the text more 'human'.
    This is rule-based and conservative: it shortens, removes filler, prefers contractions,
    and attempts safe nominalization reductions and sentence-shortening.
    """
    if not text:
        return ""
    text = ultra_clean(text)
    sentences = _split_sentences(text)
    out_sentences = []
    for s in sentences:
        s0 = s
        s = _remove_fillers(s)
        s = re.sub(r'\bfor example\b', 'for example,', s, flags=re.I)
        s = _apply_contractions(s)
        s = _try_rewrite_passive(s)
        s = _simplify_words(s)
        # split overly long sentences into smaller ones
        parts = _shorten_long_sentence(s)
        for p in parts:
            p = re.sub(r'\s{2,}', ' ', p).strip()
            # ensure sentence ends with punctuation
            if not re.search(r'[.!?]$', p):
                p = p.rstrip(' ,;:') + '.'
            # fix capitalization (first character)
            p = p[0].upper() + p[1:] if p else p
            out_sentences.append(p)
    # join with one blank line between paragraphs if input had multiple paragraphs
    result = ' '.join(out_sentences)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


class App:
    def __init__(self, root):
        self.root = root
        root.title("Algorithmic Humanizer")
        root.geometry("1100x700")

        txt_frame = ttk.Frame(root)
        txt_frame.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(txt_frame)
        left.pack(side="left", fill="both", expand=True, padx=(0,4))

        right = ttk.Frame(txt_frame)
        right.pack(side="left", fill="both", expand=True, padx=(4,0))

        ttk.Label(left, text="Original text:").pack(anchor="w")
        self.input_txt = scrolledtext.ScrolledText(left, wrap="word", height=25)
        self.input_txt.pack(fill="both", expand=True)

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Humanize", command=self.on_humanize).pack(side="left", padx=(0,6))
        ttk.Button(btns, text="Ultra Clean (no humanize)", command=self.on_ultraclean).pack(side="left")

        ttk.Label(right, text="Humanized text:").pack(anchor="w")
        self.cleaned_txt = scrolledtext.ScrolledText(right, wrap="word", height=25)
        self.cleaned_txt.pack(fill="both", expand=True)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(bottom, text="Save output...", command=self.save_cleaned).pack(side="left")
        ttk.Button(bottom, text="Copy to clipboard", command=self.copy_to_clipboard).pack(side="left", padx=6)

    def on_humanize(self):
        txt = self.input_txt.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("Empty", "Please paste or type text to humanize.")
            return
        out = humanize_text(txt)
        self.cleaned_txt.delete("1.0", "end")
        self.cleaned_txt.insert("1.0", out)
        messagebox.showinfo("Done", "Text humanized successfully.")

    def on_ultraclean(self):
        txt = self.input_txt.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("Empty", "Please paste or type text to clean.")
            return
        out = ultra_clean(txt)
        self.cleaned_txt.delete("1.0", "end")
        self.cleaned_txt.insert("1.0", out)
        messagebox.showinfo("Done", "Text cleaned successfully.")

    def save_cleaned(self):
        cleaned = self.cleaned_txt.get("1.0", "end").strip()
        if not cleaned:
            messagebox.showwarning("Empty", "No text to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                messagebox.showinfo("Saved", f"Saved text to {path}")
            except Exception as e:
                messagebox.showerror("Save error", str(e))

    def copy_to_clipboard(self):
        cleaned = self.cleaned_txt.get("1.0", "end").strip()
        if not cleaned:
            messagebox.showwarning("Empty", "No text to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(cleaned)
        messagebox.showinfo("Copied", "Humanized text copied to clipboard.")


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
