"""Fetch NASA Astronomy Picture of the Day (APOD) via NASA API with retry logic."""
import os, sys, json, argparse, datetime as _dt, pathlib, time
import requests, urllib.request, shutil

API_URL = "https://api.nasa.gov/planetary/apod"

def fetch_apod(api_key: str, date: str | None = None, *, retries: int = 3, timeout: int = 120):
    """Return APOD metadata dict.

    Retries network timeouts, connection errors, and HTTP 5xx responses.
    Back-off schedule: 5 → 10 → 20 s (for default 3 attempts).
    """
    params = {"api_key": api_key}
    if date:
        params["date"] = date

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(API_URL, params=params, timeout=timeout)
            # Consider 5xx a transient error worth retrying.
            if 500 <= r.status_code < 600:
                raise requests.exceptions.HTTPError(
                    f"{r.status_code} Server Error", response=r
                )
            r.raise_for_status()
            return r.json()
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        ) as exc:
            last_exc = exc
            if attempt < retries:
                backoff = 5 * 2 ** (attempt - 1)
                print(
                    f"Attempt {attempt}/{retries} failed: {exc}. Retrying in {backoff}s…",
                    file=sys.stderr,
                )
                time.sleep(backoff)
            else:
                raise last_exc


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

    try:
        meta = fetch_apod(key, date)
    except requests.exceptions.RequestException as exc:
        print(f"Failed to fetch APOD metadata: {exc}", file=sys.stderr)
        sys.exit(0)

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
