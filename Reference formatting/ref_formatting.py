#!/usr/bin/env python3
"""
Reformat BibTeX entries into a fixed template and *sanitize* TeX conditionals
(e.g. \ifmmode...\else...\fi) so natbib/revtex won't choke when building .bbl.

Usage:
  1) Put your raw bibtex in input.bib
  2) python reformat_bib.py
  3) Use output.bib in LaTeX
"""

from __future__ import annotations
import re
from typing import Dict, List, Tuple, Optional

# Extend as needed.
JOURNAL_MAP = {
    "Science": "Science",
    "Science Advances": "Sci. Adv.",
    "Nature": "Nature",
    "Nature Physics": "Nat. Phys.",
    "Nature Communications": "Nat. Commun.",
    "Nano Letters": "Nano Lett.",
    "Proceedings of the National Academy of Sciences": "Proc. Natl. Acad. Sci. U.S.A.",
    "Proceedings of the National Academy of Sciences of the United States of America": "Proc. Natl. Acad. Sci. U.S.A.",
    "Phys. Rev. Appl.": "Phys. Rev. Appl.",
    "Phys. Rev. Lett.": "Phys. Rev. Lett.",
    "Phys. Rev. X": "Phys. Rev. X",
    "Phys. Rev. B": "Phys. Rev. B",
    "Phys. Rev. A": "Phys. Rev. A",
    "Phys. Rev. D": "Phys. Rev. D",
    "Phys. Rev. Res.": "Phys. Rev. Res.",
    "Rev. Mod. Phys.": "Rev. Mod. Phys.",
    "Nanotechnology": "Nanotechnology",
    "MRS Bulletin": "MRS Bull.",
    "Journal of Applied Physics": "J. Appl. Phys.",
    "Applied Physics Letters": "Appl. Phys. Lett.",
    "Reports on Progress in Physics": "Rep. Prog. Phys.",
    "AVS Quantum Science": "AVS Quantum Sci.",
    "Communications Chemistry": "Commun. Chem.",
    "ACS Nano": "ACS Nano",
    "ACS Central Science": "ACS Cent. Sci.",
    "Scientific Reports": "Sci. Rep.",
    "Chem. Commun.": "Chem. Commun.",
    "Org. Biomol. Chem.": "Org. Biomol. Chem.",
    "Phys. Chem. Chem. Phys.": "Phys. Chem. Chem. Phys.",
    "Journal of Magnetic Resonance": "J. Magn. Reson.",
    "Magnetic Resonance": "Magn. Reson.",
    "Molecules": "Molecules",
    "Crystals": "Crystals",
    "npj Quantum Information": "npj Quantum Inf.",
    "Light: Science & Applications": "Light Sci. Appl.",
    "National Science Review": "Natl. Sci. Rev.",
    "Photonics Research": "Photonics Res.",
    "Nature Reviews Materials": "Nat. Rev. Mater.",
    "Nature Nanotechnology": "Nat. Nanotechnol.",
    "Progress in Nuclear Magnetic Resonance Spectroscopy": "Prog. Nucl. Magn. Reson. Spectrosc.",
    "Annual Review of Physical Chemistry": "Annu. Rev. Phys. Chem.",
    "Biophysical Journal": "Biophys. J.",
    "Chemistry – A European Journal": "Chem. Eur. J.",
    "Chemistry - A European Journal": "Chem. Eur. J.",
    "ChemBioChem": "ChemBioChem",
    "Biochimica et Biophysica Acta (BBA) - Biomembranes": "Biochim. Biophys. Acta Biomembr.",
    "Biological Chemistry": "Biol. Chem.",
    "Journal of Physics: Photonics": "J. Phys. Photonics",
    "Advanced Photonics": "Adv. Photonics",
}

SMALL_WORDS = {
    "a","an","the","and","or","nor","but","for","so","yet",
    "as","at","by","in","of","on","per","to","up","via","with","from","into","near","over","under"
}

# Name particles that are usually part of the surname.
PARTICLES = {"de","del","della","di","da","du","van","von","der","den","la","le","dos","das","de","las"}

# -------------------- TeX sanitization --------------------

def _strip_tex_ifmmode(s: str) -> str:
    """
    Replace occurrences of:
        \\ifmmode <math-branch> \\else <text-branch> \\fi{}
    with <text-branch>.
    This prevents natbib/revtex conditional nesting errors (Extra \\fi / Extra \\else).
    """
    while True:
        start = s.find(r"\ifmmode")
        if start == -1:
            return s
        i = start + len(r"\ifmmode")

        else_pos = s.find(r"\else", i)
        if else_pos == -1:
            return s  # can't safely rewrite
        fi_pos = s.find(r"\fi", else_pos + len(r"\else"))
        if fi_pos == -1:
            return s  # can't safely rewrite

        text_branch = s[else_pos + len(r"\else"):fi_pos]

        # consume optional spaces and optional trailing "{}" after \fi
        k = fi_pos + len(r"\fi")
        while k < len(s) and s[k].isspace():
            k += 1
        if s.startswith("{}", k):
            k += 2

        s = s[:start] + text_branch + s[k:]


def sanitize_tex_value(s: str) -> str:
    """
    Minimal, conservative cleanup aimed at avoiding *TeX errors* downstream
    (not trying to "prettify" BibTeX).
    """
    if not s:
        return s
    s = _strip_tex_ifmmode(s)
    # Collapse weird spacing introduced by stripping
    s = re.sub(r"\s+", " ", s).strip()
    return s

# -------------------- Title casing --------------------

def title_case_keep_braces(s: str) -> str:
    """
    Title-case while preserving {...} protected chunks verbatim.
    """
    if not s:
        return s
    parts = re.split(r"(\{[^{}]*\})", s)
    out: List[str] = []
    first_word = True

    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            out.append(part)
            continue

        words = re.split(r"(\s+)", part)
        for w in words:
            if not w or w.isspace():
                out.append(w)
                continue

            # Preserve TeX commands or tokens with digits (be conservative)
            if w.startswith("\\") or any(ch.isdigit() for ch in w):
                out.append(w)
                first_word = False
                continue

            bare = re.sub(r"[^\w\-]", "", w)
            if bare.isupper() and len(bare) >= 2:
                out.append(w)
                first_word = False
                continue

            # Title-case hyphenated segments
            segs = w.split("-")
            new_segs = []
            for seg in segs:
                if seg == "":
                    new_segs.append(seg)
                    continue
                low = seg.lower()
                if (not first_word) and (low in SMALL_WORDS):
                    new_segs.append(low)
                else:
                    new_segs.append(low[:1].upper() + low[1:])
                first_word = False
            out.append("-".join(new_segs))

    return "".join(out).strip()

# -------------------- Author formatting --------------------

_ALPHA_RE = re.compile(r"[A-Za-z]")

def _first_alpha_char(tok: str) -> str:
    m = _ALPHA_RE.search(tok)
    return m.group(0) if m else ""

def _initial_from_token(tok: str) -> str:
    tok = tok.strip()
    if not tok:
        return ""
    # If it already looks like an initial token, keep it (e.g. "J.-P.")
    if "." in tok and len(tok) <= 6:
        return tok
    # Hyphenated given names: Jean-Pierre -> J.-P.
    if "-" in tok:
        bits = [b for b in tok.split("-") if b]
        inits = []
        for b in bits:
            ch = _first_alpha_char(b)
            if ch:
                inits.append(ch.upper() + ".")
        return "-".join(inits)
    ch = _first_alpha_char(tok)
    return (ch.upper() + ".") if ch else ""

def format_one_name(name: str) -> str:
    """
    Convert to "A. B. FamilyName" form.
    Tries to keep common particles with the last name.
    """
    name = " ".join(name.split())
    if not name:
        return name

    if "," in name:
        last, given = [x.strip() for x in name.split(",", 1)]
    else:
        tokens = name.split()
        if len(tokens) == 1:
            return tokens[0]
        # Determine last name with particles
        last_tokens = [tokens[-1]]
        i = len(tokens) - 2
        while i >= 0 and tokens[i].lower() in PARTICLES:
            last_tokens.insert(0, tokens[i])
            i -= 1
        given_tokens = tokens[:i+1]
        last = " ".join(last_tokens)
        given = " ".join(given_tokens)

    initials = []
    for tok in re.split(r"\s+", given):
        init = _initial_from_token(tok)
        if init:
            initials.append(init)

    ini = " ".join(initials).strip()
    return (f"{ini} {last}").strip()

def format_author_field(author_raw: str) -> str:
    author_raw = sanitize_tex_value(author_raw)
    # Split on " and " at brace depth 0
    names = []
    buf = []
    depth = 0
    i = 0
    s = author_raw
    while i < len(s):
        if s[i] == "{":
            depth += 1
            buf.append(s[i])
            i += 1
            continue
        if s[i] == "}":
            depth = max(depth - 1, 0)
            buf.append(s[i])
            i += 1
            continue
        if depth == 0 and s.startswith(" and ", i):
            names.append("".join(buf).strip())
            buf = []
            i += 5
            continue
        buf.append(s[i])
        i += 1
    if buf:
        names.append("".join(buf).strip())

    return " and ".join(format_one_name(n) for n in names if n)

# -------------------- BibTeX parsing --------------------

def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i

def _read_braced(s: str, i: int) -> Tuple[str, int]:
    assert s[i] == "{"
    depth = 0
    j = i
    out = []
    while j < len(s):
        ch = s[j]
        out.append(ch)
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                # include closing brace in out, return inner content
                raw = "".join(out)
                return raw[1:-1], j + 1
        j += 1
    raise ValueError("Unbalanced braces while reading value.")

def _read_quoted(s: str, i: int) -> Tuple[str, int]:
    assert s[i] == '"'
    j = i + 1
    out = []
    while j < len(s):
        ch = s[j]
        if ch == '"' and (j == 0 or s[j-1] != "\\"):
            return "".join(out), j + 1
        out.append(ch)
        j += 1
    raise ValueError("Unbalanced quotes while reading value.")

def _read_bare(s: str, i: int) -> Tuple[str, int]:
    j = i
    while j < len(s) and s[j] not in ",\n\r}":
        j += 1
    return s[i:j].strip(), j

def _read_value(s: str, i: int) -> Tuple[str, int]:
    i = _skip_ws(s, i)
    if i >= len(s):
        return "", i
    if s[i] == "{":
        return _read_braced(s, i)
    if s[i] == '"':
        return _read_quoted(s, i)
    return _read_bare(s, i)

def parse_entries(bib: str) -> List[Tuple[str, str, Dict[str, str]]]:
    """
    Returns list of (entry_type, key, fields)
    """
    entries: List[Tuple[str, str, Dict[str, str]]] = []
    i = 0
    while True:
        m = re.search(r"@([A-Za-z]+)\s*\{", bib[i:])
        if not m:
            break
        entry_type = m.group(1).lower()
        start = i + m.start()
        j = i + m.end()  # position after '{'
        # read key until comma at depth 0
        key_start = j
        while j < len(bib) and bib[j].isspace():
            j += 1
            key_start = j
        while j < len(bib) and bib[j] != ",":
            j += 1
        key = bib[key_start:j].strip()
        j += 1  # skip comma

        fields: Dict[str, str] = {}
        depth = 1  # outer entry brace depth (we are inside it)
        while j < len(bib) and depth > 0:
            j = _skip_ws(bib, j)
            if j >= len(bib):
                break
            if bib[j] == "}":
                depth -= 1
                j += 1
                continue
            if bib[j] == "{":
                depth += 1
                j += 1
                continue
            # read field name
            name_m = re.match(r"([A-Za-z][A-Za-z0-9_\-]*)", bib[j:])
            if not name_m:
                # skip junk char
                j += 1
                continue
            fname = name_m.group(1).lower()
            j += len(name_m.group(1))
            j = _skip_ws(bib, j)
            if j < len(bib) and bib[j] == "=":
                j += 1
            else:
                continue
            val, j = _read_value(bib, j)
            fields[fname] = val.strip()
            j = _skip_ws(bib, j)
            if j < len(bib) and bib[j] == ",":
                j += 1

        entries.append((entry_type, key, fields))
        i = j
    return entries

# -------------------- Reformatting --------------------

def reformat_entry(entry_type: str, key: str, fields: Dict[str, str]) -> str:
    author = sanitize_tex_value(fields.get("author", ""))
    title = sanitize_tex_value(fields.get("title", ""))
    journal = sanitize_tex_value(fields.get("journal", ""))

    year = sanitize_tex_value(fields.get("year", ""))
    volume = sanitize_tex_value(fields.get("volume", ""))
    number = sanitize_tex_value(fields.get("number", "")) or sanitize_tex_value(fields.get("issue", ""))

    if author:
        author = format_author_field(author)
    if title:
        title = title_case_keep_braces(title)
    if journal:
        journal = JOURNAL_MAP.get(journal, journal)

    # Your requested fixed template:
    return (
        "@article{\n"
        f"{key},\n"
        f"author = {{{author}}},\n"
        f"title = {{\\textit{{{title}}}}},\n"
        f"journal = {{\\textit{{{journal}}}}},\n"
        f"volume = {{{volume}}},\n"
        f"number = {{{number}}},\n"
        f"year = {{{year}}}\n"
        "}\n"
    )

def main() -> None:
    with open("input.bib", "r", encoding="utf-8") as f:
        bib = f.read()

    entries = parse_entries(bib)

    out_blocks: List[str] = []
    for entry_type, key, fields in entries:
        out_blocks.append(reformat_entry(entry_type, key, fields))

    with open("output.bib", "w", encoding="utf-8") as f:
        f.write("\n".join(out_blocks).strip() + "\n")

if __name__ == "__main__":
    main()
