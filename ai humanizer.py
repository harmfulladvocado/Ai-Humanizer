import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import unicodedata

_REPLACEMENTS = {
    'leverage': 'use', 'utilize': 'use', 'utilizing': 'using', 'synergize': 'work together', 'synergy': 'teamwork',
    'data-driven': 'based on data', 'cutting-edge': 'new', 'state-of-the-art': 'advanced', 'innovative': 'new',
    'groundbreaking': 'new', 'robust': 'strong', 'scalable': 'expandable', 'framework': 'setup',
    'pipeline': 'process', 'architecture': 'design', 'fine-tune': 'adjust', 'train': 'teach', 'model': 'system',
    'dataset': 'data', 'parameters': 'settings', 'outputs': 'results', 'input': 'data', 'outputs': 'results',
    'contextualize': 'explain', 'delve into': 'look at', 'in this context': 'here', 'perform': 'do', 'execute': 'do',
    'facilitate': 'help', 'enable': 'allow', 'empower': 'help', 'assist': 'help', 'endeavor': 'try',
    'attempt': 'try', 'conceptualize': 'think of', 'operationalize': 'put into action', 'implement': 'do',
    'conduct': 'do', 'achieve': 'reach', 'obtain': 'get', 'ascertain': 'find out', 'determine': 'find out',
    'evaluate': 'check', 'assess': 'check', 'analyze': 'look at', 'generate': 'make', 'produce': 'make',
    'demonstrate': 'show', 'illustrate': 'show', 'provide': 'give', 'supply': 'give', 'submit': 'send',
    'disclose': 'tell', 'communicate': 'say', 'express': 'say', 'specify': 'say', 'indicate': 'show',
    'stipulate': 'say', 'notify': 'tell', 'enhance': 'improve', 'optimize': 'improve', 'streamline': 'simplify',
    'maximize': 'increase', 'minimize': 'reduce', 'impactful': 'meaningful', 'ensure': 'make sure',
    'realize': 'see', 'enable': 'let', 'commence': 'start', 'terminate': 'end', 'finalize': 'finish',
    'objective': 'goal', 'approach': 'way', 'methodology': 'method', 'scenario': 'situation', 'domain': 'area',
    'application': 'use', 'capability': 'ability', 'functionality': 'feature', 'entity': 'thing', 'entities': 'things',
    'in order to': 'to', 'at this point in time': 'now', 'at the end of the day': 'ultimately',
    'it should be noted that': '', 'it is important to note that': '', 'for the purpose of': 'for',
    'to a certain extent': 'somewhat', 'as previously mentioned': 'as mentioned earlier',
    'in terms of': 'about', 'with respect to': 'about', 'regarding': 'about', 'pertaining to': 'about',
    'via': 'through', 'for instance': 'for example', 'for example': 'like', 'by means of': 'by',
    'therefore': 'so', 'thus': 'so', 'hence': 'so', 'consequently': 'so', 'as a result': 'so', 'accordingly': 'so',
    'however': 'but', 'nonetheless': 'still', 'nevertheless': 'still', 'yet': 'but', 'notwithstanding': 'despite',
    'although': 'although', 'though': 'though', 'even though': 'even though', 'whereas': 'while',
    'subsequently': 'after that', 'thereafter': 'after that', 'prior to': 'before', 'preceding': 'before',
    'initially': 'at first', 'previously': 'before', 'forthwith': 'immediately', 'hereafter': 'after this',
    'hitherto': 'until now', 'currently': 'now', 'forthcoming': 'coming', 'at the earliest convenience': 'soon',
    'hereby': 'by this', 'heretofore': 'until now', 'whereby': 'where', 'therein': 'in it', 'thereof': 'of that',
    'herein': 'in this',
    'aforementioned': 'mentioned earlier', 'aforesaid': 'mentioned earlier', 'pursuant to': 'under',
    'in accordance with': 'according to', 'as per': 'according to', 'in the event that': 'if',
    'for the avoidance of doubt': 'to be clear', 'in relation to': 'about',
    'substantial': 'big', 'considerable': 'big', 'significant': 'important', 'major': 'big', 'pronounced': 'strong',
    'marked': 'strong', 'paramount': 'important', 'crucial': 'important', 'critical': 'important',
    'essential': 'important', 'vital': 'important', 'pertinent': 'relevant', 'relevant': 'related', 'optimal': 'best',
    'adequate': 'good enough', 'sufficient': 'enough', 'insufficient': 'not enough', 'suboptimal': 'not ideal',
    'preliminary': 'first', 'initial': 'first', 'subsequent': 'next', 'interim': 'temporary',
    'temporary': 'short-term', 'final': 'last', 'ultimate': 'last', 'approximate': 'about', 'rough': 'about',
    'numerous': 'many', 'various': 'many', 'diverse': 'many', 'different': 'other', 'additional': 'extra',
    'supplementary': 'extra', 'respective': 'each', 'individual': 'each', 'collective': 'all', 'mutual': 'shared',
    'separate': 'different', 'cognizant': 'aware', 'expedite': 'speed up',
    'artificial intelligence': 'AI', 'machine learning': 'ML', 'deep learning': 'DL', 'natural language processing': 'NLP',
    'large language model': 'AI model', 'foundation model': 'AI model', 'language model': 'AI model', 'open-source': 'public',
    'closed-source': 'private', 'synthetic data': 'made-up data', 'augmentation': 'extra data', 'fine-tuning': 'adjustment',
    'prompt engineering': 'prompt crafting', 'multi-modal': 'multi-type', 'real-world': 'everyday', 'human-centric': 'human-focused',
    'stakeholders': 'people', 'collaboration': 'teamwork', 'transparent': 'clear', 'transparency': 'clarity', 'alignment': 'agreement',
    'ethical': 'fair', 'bias': 'unfairness', 'mitigate': 'reduce', 'address': 'handle', 'issue': 'problem',
    'method': 'way', 'procedure': 'step', 'mechanism': 'system', 'process': 'way', 'metrics': 'measures',
    'benchmark': 'standard', 'accuracy': 'precision', 'precision': 'exactness', 'recall': 'retrieval',
    'deployment': 'release', 'implementation': 'setup', 'iteration': 'version', 'feedback loop': 'cycle',
    'output': 'result', 'input data': 'data', 'context window': 'memory span', 'token': 'word piece',
    'parameter tuning': 'adjusting settings', 'scalability': 'growth ability', 'usability': 'ease of use',
    'efficiency': 'speed', 'effectiveness': 'usefulness', 'collaborate': 'work together', 'synthesize': 'combine',
    'aggregate': 'combine', 'integrate': 'combine', 'disseminate': 'share', 'propagate': 'spread',
    'validate': 'check', 'verification': 'check', 'evaluation': 'review', 'assessment': 'check',
    'accuracy rate': 'correctness', 'prediction': 'guess', 'forecast': 'prediction', 'trend': 'pattern',
    'hypothesis': 'idea', 'correlation': 'connection', 'causation': 'cause', 'derive': 'get', 'obtain': 'get',
    'capture': 'get', 'extract': 'pull', 'embed': 'insert', 'embedding': 'representation', 'representation': 'form'
}

_REPLACEMENTS = {k.lower(): v for k, v in _REPLACEMENTS.items()}
_PATTERN = re.compile(r'\b(' + '|'.join(map(re.escape, sorted(_REPLACEMENTS.keys(), key=len, reverse=True))) + r')\b', re.IGNORECASE)
_INVISIBLE_CHARS = ['\u200b', '\u200d', '\u2060']

def _preserve_case(orig: str, repl: str) -> str:
    if orig.isupper(): return repl.upper()
    if orig[0].isupper(): return repl.capitalize()
    return repl

def ultra_clean(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    for ch in _INVISIBLE_CHARS: text = text.replace(ch, '')
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'-\s*\n\s*', '', text)
    paragraphs = re.split(r'\n\s*\n', text)
    cleaned = []
    for p in paragraphs:
        p = ' '.join(ln.strip() for ln in p.splitlines() if ln.strip())
        p = re.sub(r'<[^>]+>', '', p)
        p = p.replace('&nbsp;', ' ').replace('&amp;', '&')
        p = p.replace('“','"').replace('”','"').replace('’',"'").replace('‘',"'")
        p = re.sub(r'[–—−]', '-', p)
        p = re.sub(r'\.{2,}', '.', p)
        p = re.sub(r'([A-Za-z])\1{3,}', r'\1\1\1', p)
        p = re.sub(r'([!?]){2,}', r'\1', p)
        p = re.sub(r'\s*-\s*', ' - ', p)
        p = re.sub(r'\s+([,;:.!?%)\]])', r'\1', p)
        p = _PATTERN.sub(lambda m: _preserve_case(m.group(0), _REPLACEMENTS.get(m.group(0).lower(), m.group(0))), p)
        p = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1)+' '+m.group(2).upper(), p)
        cleaned.append(p.strip())
    result = '\n\n'.join(cleaned)
    result = re.sub(r'\s{2,}', ' ', result)
    return result[0].upper() + result[1:] if result else result

class App:
    def __init__(self, root):
        self.root = root
        root.title("Ultra Text Cleaner")
        root.geometry("1920x1080")

        txt_frame = ttk.Frame(root)
        txt_frame.pack(fill="both", expand=True, padx=8)

        col1 = ttk.Frame(txt_frame)
        col1.pack(side="left", fill="both", expand=True, padx=(0,4))

        col2 = ttk.Frame(txt_frame)
        col2.pack(side="left", fill="both", expand=True, padx=(4,0))

        ttk.Label(col1, text="Original text:").pack(anchor="w")
        self.input_txt = scrolledtext.ScrolledText(col1, wrap="word", height=18)
        self.input_txt.pack(fill="both", expand=True)

        btns = ttk.Frame(col1)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Clean / Humanize", command=self.on_clean).pack(side="left")

        ttk.Label(col2, text="Cleaned text:").pack(anchor="w")
        self.cleaned_txt = scrolledtext.ScrolledText(col2, wrap="word", height=18)
        self.cleaned_txt.pack(fill="both", expand=True)

        ttk.Button(root, text="Save cleaned...", command=self.save_cleaned).pack(fill="x", padx=8, pady=6)

    def on_clean(self):
        txt = self.input_txt.get("1.0", "end").strip()
        self.cleaned_txt.delete("1.0", "end")
        self.cleaned_txt.insert("1.0", ultra_clean(txt))
        messagebox.showinfo("Done", "Text cleaned successfully.")

    def save_cleaned(self):
        cleaned = self.cleaned_txt.get("1.0", "end").strip()
        if not cleaned: messagebox.showwarning("Empty", "No cleaned text to save."); return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f: f.write(cleaned)
                messagebox.showinfo("Saved", f"Saved cleaned text to {path}")
            except Exception as e: messagebox.showerror("Save error", str(e))

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()