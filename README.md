# Multi-Source Candidate Data Transformer

**Eightfold Engineering Intern Assignment · Jul–Dec 2026**

Transforms messy, multi-source candidate data (CSV, ATS JSON, GitHub profiles, resumes, recruiter notes) into one clean canonical JSON profile per candidate — with provenance tracking, confidence scoring, and a runtime-configurable output schema.

---

## Architecture

```
Input Sources
    │
    ▼
[Adapter Layer]          one adapter per source type → RawRecord objects
    │
    ▼
[Normalizer Layer]       phones → E.164 · dates → YYYY-MM · country → ISO-3166 · skills → canonical
    │
    ▼
[Identity Matcher]       groups RawRecords belonging to the same person
    │
    ▼
[Merger + Conflict Resolver]  one CanonicalProfile per group · provenance populated
    │
    ▼
[Confidence Scorer]      per-field and overall_confidence
    │
    ▼
[CanonicalProfile]       clean internal record — never exposed directly
    │
    ▼
[Projection Layer]       reshapes per runtime config (field selection, rename, normalize)
    │
    ▼
[Output Validator]       validates result against config-declared schema
    │
    ▼
JSON output (stdout or file)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline (CLI)

```bash
# Default schema — all canonical fields, printed to stdout
python -m src.cli sample_inputs/recruiter.csv sample_inputs/notes.txt

# Add a resume — merged with CSV and notes for the same candidate
python -m src.cli sample_inputs/recruiter.csv \
  sample_inputs/notes.txt \
  sample_inputs/sample_resume.docx

# Include a LinkedIn export
python -m src.cli sample_inputs/recruiter.csv \
  sample_inputs/linkedin_export.json \
  sample_inputs/notes.txt

# Custom config — minimal output with field renames
python -m src.cli sample_inputs/recruiter.csv sample_inputs/notes.txt --config configs/example_custom_config.json

# Skills-only config — candidate_id, name, and canonicalized skill list
python -m src.cli sample_inputs/recruiter.csv sample_inputs/notes.txt --config configs/skills_only_config.json

# Write output to file
python -m src.cli sample_inputs/recruiter.csv sample_inputs/notes.txt \
  --config configs/default_config.json \
  --output sample_outputs/default_output.json


```

### 3. Run tests

```bash
pytest tests/ -v
```

---

## CLI Options

```
Usage: python -m src.cli [OPTIONS] INPUT...

  Multi-Source Candidate Data Transformer.

Options:
  -c, --config PATH         Runtime output config JSON (default schema if omitted).
  -o, --output PATH         Write JSON to file instead of stdout.
  --pretty / --compact      Pretty-print (default) or compact JSON.
  --ats-field-map PATH      JSON file mapping ATS field names to canonical names.
  --github-token TEXT       GitHub PAT for higher API rate limits (or GITHUB_TOKEN env var).
  -v, --verbose             Enable INFO-level logging.
  -h, --help                Show this message and exit.
```

---

## Supported Input Sources

| Source | Type | Format |
|---|---|---|
| Recruiter CSV | Structured | `.csv` with name / email / phone / company / title columns |
| ATS JSON blob | Structured | `.json` with non-canonical field names (configurable via `--ats-field-map`) |
| GitHub profile | Unstructured | `https://github.com/<username>` URL |
| LinkedIn export | Unstructured | Pre-exported `.json` file — see note below |
| Resume | Unstructured | `.pdf` or `.docx` |
| Recruiter notes | Unstructured | `.txt` free text |

> **LinkedIn note:** LinkedIn has no public API and scraping violates their ToS.
> This adapter accepts a pre-exported JSON file in LinkedIn data-export format.
> In production, a licensed data provider (e.g. Proxycurl, People Data Labs) would be used.

---

## Output Schema (default)

```json
{
  "candidate_id":       "string  — deterministic sha256 hash of email+name",
  "full_name":          "string",
  "emails":             "string[]",
  "phones":             "string[]  — E.164 format",
  "location":           {"city": "string", "region": "string", "country": "ISO-3166 alpha-2"},
  "links":              {"linkedin": "string|null", "github": "string|null", "portfolio": "string|null", "other": []},
  "headline":           "string|null",
  "years_experience":   "number|null",
  "skills":             [{"name": "string", "confidence": 0.0, "sources": ["string"]}],
  "experience":         [{"company": "string", "title": "string", "start": "YYYY-MM", "end": "YYYY-MM|null", "summary": "string|null"}],
  "education":          [{"institution": "string", "degree": "string", "field": "string", "end_year": 2024}],
  "provenance":         [{"field": "string", "source": "string", "method": "string"}],
  "overall_confidence": 0.0
}
```

---

## Runtime Config

Pass `--config` with a JSON file to reshape the output without any code changes:

```json
{
  "fields": [
    {"path": "full_name",      "type": "string",   "required": true},
    {"path": "primary_email",  "from": "emails[0]","type": "string",   "required": true},
    {"path": "phone",          "from": "phones[0]","type": "string",   "normalize": "E164"},
    {"path": "skills",         "from": "skills[].name", "type": "string[]", "normalize": "canonical"}
  ],
  "include_confidence": true,
  "on_missing": "null"
}
```

**Config options:**

| Key | Values | Default | Effect |
|---|---|---|---|
| `fields[].path` | string | required | Output key name |
| `fields[].from` | path expression | same as path | Canonical path to read: `field`, `field[N]`, `field[].subfield` |
| `fields[].type` | `string`, `string[]`, `number`, `object`, `object[]` | — | Type hint for validation |
| `fields[].required` | `true` / `false` | `false` | Whether absence triggers `on_missing` |
| `fields[].normalize` | `E164`, `canonical` | — | Post-resolve normalization |
| `include_confidence` | `true` / `false` | `false` | Append `overall_confidence` |
| `include_provenance` | `true` / `false` | `false` | Append `provenance` array |
| `on_missing` | `null`, `omit`, `error` | `null` | What to do when a field resolves to nothing |

---

## ATS Field Mapping

Every ATS vendor uses different field names. Supply a mapping file:

```json
{
  "candidate_name": "full_name",
  "primary_email":  "emails",
  "cell_phone":     "phones",
  "current_employer": "extra.current_company"
}
```

Pass it via `--ats-field-map path/to/map.json`.

---

## Project Structure

```
src/
├── adapters/          One adapter per source type (CSV, ATS JSON, GitHub, LinkedIn, resume, notes)
├── normalizers/       Phone (E.164), date (YYYY-MM), country (ISO-3166), skill canonicalization
├── merger/            Identity matching, field-level merge, conflict resolution
├── scoring/           Per-field and overall confidence scoring
├── projection/        Runtime config parsing, path evaluation, output reshaping, schema validation
├── models/            RawRecord (per-source) · CanonicalProfile (merged internal record)
├── pipeline.py        Orchestrator — wires all stages end-to-end
└── cli.py             Click-based CLI entry point
data/
└── skill_aliases.json  Alias → canonical name map (e.g. "JS" → "JavaScript")
sample_inputs/         Example inputs for each supported source type
sample_outputs/        Pre-generated outputs for each config mode
configs/               Default and example custom output configs
tests/                 pytest test suite
```

---

## Assumptions & Descoped Items

- **LinkedIn**: handled via pre-exported JSON (no live API).
- **Resume OCR**: scanned PDFs are not OCR'd — text-layer PDFs only. Add `pytesseract` + `pdf2image` for OCR if needed.
- **Scale**: single-threaded; processes candidates sequentially. No parallelism required for this scope.
- **`years_experience`**: computed from experience date ranges (union of intervals), not from a stated field.
- **`candidate_id`**: deterministic `sha256(email|name)[:16]`; UUID fallback if no identity fields.
- **Skill taxonomy**: bundled `data/skill_aliases.json`; add entries to expand coverage without code changes.
