# The World Today — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/plm34554a/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/plm34554a/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Built for the [make.fun bounty news-image-20261125](https://make.fun/bounty/news-image-20261125).

A front-page image summing up the world's news of **Wednesday 25 November
2026**, drawn entirely in code. `main.py` (Python 3.13 standard library only)
renders a 1024×1024 PNG newspaper front page and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`).

## The image

- **Masthead + date band** — "THE WORLD TODAY" over a red band naming the
  day: **WEDNESDAY 25 NOVEMBER 2026**.
- **Lead story — CIA & ODNI cyberattack.** A globe and padlock over a dark
  panel: the CIA and the Office of the Director of National Intelligence
  suffered a cyber intrusion affecting classified information, the latest in
  a string of US government breaches.
- **Huawei found guilty** — a US jury convicted Huawei on 10 of 12 counts,
  including trade-secret theft, after a three-month trial in New York.
- **Ukraine war at sea** — Kyiv's drone strike on a Russian cargo ship in
  the Gulf of Finland, Putin vowing retaliation, Ukraine sinking a Russian
  naval vessel in a Libyan port, and NATO early-warning aircraft for Poland.
- **Houthis strike Riyadh** — a drone hit the capital's tallest tower;
  11 wounded.
- **Trump / Thanksgiving eve** — Rudy Giuliani awarded the Presidential
  Medal of Freedom; Thanksgiving turkeys "Freedom" and "Feathers" pardoned.
- **India** — the BJP and Shiromani Akali Dal renewed their alliance for
  the 2027 Punjab elections after a six-year split; Nepal PM Balendra Shah's
  state visit to India.
- **Sport** — England beat Australia by 8 wickets in the 2nd T20I, chasing
  185 to level the series 1–1.
- **DRC** — WHO evacuated staff from a hospital in Ituri amid fierce
  fighting and the Ebola outbreak.
- **Ticker** — International Day for the Elimination of Violence against
  Women; GTA 6 out worldwide; Trump to meet NATO chief Mark Rutte; the US
  preparing new tariffs on global trading partners.

## How it is drawn

Everything is drawn with `main.py` using only the Python standard library
(`zlib`/`struct` for PNG encoding). The page is built from rectangles,
lines, circles and a small built-in 5×7 bitmap font written for this entry
— no external fonts, images or network access. The output is deterministic:
two runs write byte-identical files.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024 PNG, ~22 KB)
```

## License

MIT — see `LICENSE`.
