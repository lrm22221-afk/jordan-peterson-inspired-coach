# Self-critic review

| # | Finding | Fix |
|---|---------|-----|
| 1 | The Hebrew triggers "מחיר" (price) and "שכר" (salary) were too broad: any mention of a price started a role-play. | Narrowed them to negotiation verbs. Added false-positive tests. |
| 2 | The procrastination regex `avoid(ing)? it` matched innocent sentences. | Narrowed it to `avoiding (it\|this\|that)`. Test added. |
| 3 | Pattern counting and the FIRM stance could fire during a crisis. | SAFETY short-circuits before any counting. A test checks that counts don't change and that neither FIRM nor ROLEPLAY fires. |
| 4 | Crisis resources depended on the LLM repeating them. | The CLI always prints them on SAFETY, regardless of the model's reply. Test added. |
| 5 | Risk of invented quotes and impersonation. | The persona forbids both. Every direct quote was checked against the transcripts. Principles are labelled as paraphrases. A test requires every principle source id to exist in REPORT.md. |
| 6 | Risk of copying the commercial Self-Authoring wording. | All questions are original. The structure is credited to S1. |
| 7 | YouTube blocked transcript access from the server, and the full books are not legally available. | Disclosed in REPORT §1. The blocked items are listed. Book claims stay at rule level. |
| 8 | Role-play could repeat on every turn. | It is offered once per scenario per session. Test added. |
| 9 | Secrets could leak into the repo. | The API key is read from env vars only. `.env` and profiles are gitignored, and the profile file is chmod 600. |
| 10 | Pattern regexes are heuristic and cover only English and Hebrew. | Documented limitation. An LLM classifier is a possible later step. |

## Second pass (after extended research)
| # | Finding | Fix |
|---|---------|-----|
| 11 | The Rule 4 "small step" phrasing was unverified. | Verified against the book excerpt and against JBP's own words in L13 [00:33:42, 00:35:28] and L15 [00:44:46]. The principle was rewritten to match. |
| 12 | Assertiveness and negotiation rested on a single clip (L4). | Now grounded in the full Personality 17 lecture (L9) and L18. Added a new principle, `agreeable_negotiation`, linked from the pushover and resentment patterns. |
| 13 | Guest speech in the Voss episode could be misattributed to Peterson. | L17 is used only as a source of negotiation ideas. The caveat is in the notes. |
| 14 | Quotes needed reproducible verification. | Added `tools/verify_quotes.py`. All transcript quotes match. The only quotes it can't confirm are the L4 clip and the book excerpts, which come from secondary sources. |
| 15 | Copyright. | Full transcripts are kept outside the repo. Only short, timestamped excerpts are included. |
| 16 | Every lecture id must be documented. | Test added: each L-id has its own section in transcript_notes.md. |
