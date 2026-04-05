"""Entry point to run the portfolio parser and write Person to output_portfolio.md.

Run from project root: python -m parsers.run_portfolio
Uses Gemini 2.0 Flash; load .env for GEMINI_API_KEY or GOOGLE_API_KEY.
"""

from pathlib import Path

from dotenv import load_dotenv
from llm import GeminiClient

from parsers.portfolio.parser import PortfolioParser, _person_to_md

if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    _url = "https://www.hellonish.dev"
    _out_path = Path(__file__).resolve().parent / "portfolio" / "output_portfolio.md"
    llm = GeminiClient()
    person = PortfolioParser().parse_with_skill(_url, llm, model="gemini-2.0-flash")
    _out_path.write_text(_person_to_md(person), encoding="utf-8")
    print(f"Wrote {_out_path}")
