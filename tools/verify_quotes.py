"""Check that every "quoted" string in research/transcript_notes.md appears verbatim in local transcripts.
Usage: python tools/verify_quotes.py /path/to/transcripts_dir   (transcripts are not distributed)."""
import glob, re, sys
d = sys.argv[1]
text = re.sub(r"\[\d\d:\d\d:\d\d\] ", "", " ".join(open(f).read().replace("\n", " ") for f in glob.glob(f"{d}/*.txt"))).lower()
notes = open("research/transcript_notes.md", encoding="utf-8").read()
miss = [q for q in re.findall(r'"([^"]{12,})"', notes) if q.lower() not in text]
print(f"{len(miss)} not found in transcripts (expected only for clip/book quotes from secondary sources):")
for q in miss: print(" -", q[:90])
