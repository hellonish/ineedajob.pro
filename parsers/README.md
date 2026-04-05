# Parsers

Resume (PDF/DOCX, file or stream) and portfolio (URL) parsers that use the extract-person skill and output a `Person` to Markdown.

## Running the parsers

From project root, use the runner scripts to avoid the `RuntimeWarning` and use Gemini 2.0 Flash:

```bash
python -m parsers.run_resume      # writes parsers/resume/output_resume.md
python -m parsers.run_portfolio  # writes parsers/portfolio/output_portfolio.md
```

Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in `.env` (or export it).

## About the RuntimeWarning

If you run `python -m parsers.resume.parser` or `python -m parsers.portfolio.parser`, you may see:

```
RuntimeWarning: 'parsers.portfolio.parser' found in sys.modules after import of package 'parsers.portfolio', but prior to execution of 'parsers.portfolio.parser'
```

That happens because Python loads the package `parsers.portfolio` (which imports `parser.py`) to resolve the module name, then runs that same `parser.py` as `__main__`. The same file is both a normal module and the main script, which Python warns about. Using `python -m parsers.run_portfolio` (or `run_resume`) avoids this: the runner is a separate module and does not get imported by the package.
