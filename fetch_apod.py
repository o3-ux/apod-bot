"""Fetch NASA Astronomy Picture of the Day (APOD) via NASA API.

Minimal scaffold; later extended with logging and chat posting.
"""
import os, sys, json, argparse, datetime as _dt, pathlib, requests, urllib.request, shutil

API_URL = "https://api.nasa.gov/planetary/apod"


def fetch_apod(api_key: str, date: str | None = None):
    params = {"api_key": api_key}
    if date:
        params["date"] = date
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--api-key")
    p.add_argument("--date")
    p.add_argument("--out-dir", default="data")
    args = p.parse_args(argv)
    key = args.api_key or os.getenv("APOD_API_KEY")
    if not key:
        sys.exit("Provide NASA API key with --api-key or APOD_API_KEY env var")
    date = args.date or _dt.date.today().isoformat()
    meta = fetch_apod(key, date)
    out_dir = pathlib.Path(args.out_dir) / date
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
    img_url = meta.get("hdurl") or meta["url"]
    img_name = img_url.split("/")[-1].split("?")[0]
    with urllib.request.urlopen(img_url) as resp, open(out_dir / img_name, "wb") as f:
        shutil.copyfileobj(resp, f)
    print(f"Saved APOD {date} to {out_dir}")


if __name__ == "__main__":
    main()
