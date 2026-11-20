#!/usr/bin/env python3
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://wutheringwaves.fandom.com/api.php"
IMAGE_OUTPUT_DIR = ROOT / "resonators"
CHARACTER_IMAGE_DIR = ROOT / "src/lib/images/characters"
CHARACTER_DATA_FILE = ROOT / "src/lib/data/characters.ts"
USER_AGENT = "wuwa-team-randomizer-resonator-importer/1.0"

WEAPONS = {"broadblade", "gauntlet", "sword", "pistol", "rectifier"}
ATTRIBUTES = {"fusion", "glacio", "aero", "electro", "spectro", "havoc"}
GENDERS = {"male", "female"}


def normalize_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def request_json(params):
    url = f"{API_URL}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"MediaWiki API request failed: {error}") from error
    if "error" in data:
        raise RuntimeError(f"MediaWiki API error: {data['error'].get('info', data['error'])}")
    return data


def find_page(data):
    pages = data.get("query", {}).get("pages", {})
    if isinstance(pages, dict):
        pages = list(pages.values())
    if not pages or pages[0].get("missing") is not None:
        raise RuntimeError("The requested page was not found on the wiki.")
    return pages[0]


def fetch_resonator_metadata(name):
    page_data = request_json(
        {
            "action": "query",
            "titles": name,
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "format": "json",
        }
    )
    page = find_page(page_data)
    revisions = page.get("revisions", [])
    if not revisions:
        raise RuntimeError(f"No page content was returned for '{name}'.")
    revision = revisions[0]
    main_slot = revision.get("slots", {}).get("main", {})
    wikitext = revision.get("*") or main_slot.get("*") or main_slot.get("content")
    if not wikitext:
        raise RuntimeError(f"No page content was returned for '{name}'.")

    infobox = re.search(
        r"(?ims)^\{\{\s*Resonator\s+Infobox\b(.*?)^\}\}",
        wikitext,
    )
    if not infobox:
        raise RuntimeError(f"No Resonator Infobox was found on the page for '{name}'.")

    fields = {}
    for line in infobox.group(1).splitlines():
        match = re.match(r"\s*\|\s*([a-zA-Z]+)\s*=\s*(.*?)\s*$", line)
        if match:
            fields[match.group(1).lower()] = clean_wikitext(match.group(2))

    required = ("name", "weapon", "rarity", "attribute", "gender")
    missing = [field for field in required if not fields.get(field)]
    if missing:
        raise RuntimeError(
            f"Missing {', '.join(missing)} in the Resonator Infobox for '{name}'."
        )

    return {
        "displayName": fields["name"],
        "weapon": parse_enum(fields["weapon"], WEAPONS, "weapon"),
        "rarity": parse_rarity(fields["rarity"]),
        "attribute": parse_enum_list(fields["attribute"], ATTRIBUTES, "attribute"),
        "gender": parse_enum_list(fields["gender"], GENDERS, "gender"),
    }


def clean_wikitext(value):
    value = re.sub(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"<[^>]*>", "", value)
    return value.strip()


def parse_enum(value, allowed, field):
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise RuntimeError(f"Unsupported {field} '{value}'. Expected one of: {', '.join(sorted(allowed))}.")
    return normalized


def parse_enum_list(value, allowed, field):
    values = re.split(r"[,;/]|\band\b", value.lower())
    parsed = []
    for item in values:
        item = item.strip()
        if not item:
            continue
        if item not in allowed:
            raise RuntimeError(
                f"Unsupported {field} '{item}'. Expected values from: {', '.join(sorted(allowed))}."
            )
        if item not in parsed:
            parsed.append(item)
    if not parsed:
        raise RuntimeError(f"No {field} values were found.")
    return parsed


def parse_rarity(value):
    match = re.search(r"\b([45])\b", value)
    if not match:
        raise RuntimeError(f"Unsupported rarity '{value}'. Expected 4 or 5.")
    return int(match.group(1))


def fetch_image_url(name):
    wiki_name = name.replace(" ", "_")
    title = f"File:Resonator_{wiki_name}.png"
    data = request_json(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        }
    )
    page = find_page(data)
    image_info = page.get("imageinfo", [])
    if not image_info:
        raise RuntimeError(f"Image '{title}' was not found on the wiki.")
    return image_info[0]["url"]


def download_and_convert(image_url, output_path):
    request = Request(
        image_url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://wutheringwaves.fandom.com/",
        },
    )
    download_path = output_path.with_suffix(".source")
    try:
        with urlopen(request, timeout=60) as response, download_path.open("wb") as target:
            shutil.copyfileobj(response, target)
        subprocess.run(
            [
                "convert",
                str(download_path),
                "-filter",
                "Lanczos",
                "-resize",
                "128x128",
                "-quality",
                "95",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (HTTPError, URLError, TimeoutError, OSError, subprocess.CalledProcessError) as error:
        details = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
        raise RuntimeError(f"Failed to download or convert image: {details}") from error
    finally:
        download_path.unlink(missing_ok=True)


def record_blocks(source):
    return list(re.finditer(r"(?ms)^    \{\n.*?^    \},", source))


def get_record_slug(block):
    match = re.search(r'(?m)^        slug: ("(?:\\.|[^"\\])*"),$', block)
    return json.loads(match.group(1)) if match else None


def format_record(record_id, slug, display_name, metadata):
    return "\n".join(
        [
            "    {",
            f"        id: {record_id},",
            f"        slug: {json.dumps(slug)},",
            f"        displayName: {json.dumps(display_name, ensure_ascii=False)},",
            f"        weapon: {json.dumps(metadata['weapon'])},",
            f"        rarity: {metadata['rarity']},",
            f"        attribute: {json.dumps(metadata['attribute'])},",
            f"        gender: {json.dumps(metadata['gender'])},",
            "        selected: true,",
            "    },",
        ]
    )


def replace_field(block, field, value):
    replacement = f"        {field}: {value},"
    updated, count = re.subn(
        rf"(?m)^        {re.escape(field)}:.*,$",
        lambda _: replacement,
        block,
    )
    if count != 1:
        raise RuntimeError(f"Could not uniquely update '{field}' in an existing character record.")
    return updated


def apply_record(source, slug, metadata):
    blocks = record_blocks(source)
    ids = [
        int(match.group(1))
        for match in re.finditer(r"(?m)^\s*id: (\d+),$", source)
    ]
    if ids != list(range(len(ids))):
        raise RuntimeError("Existing character IDs are not consecutive; refusing to append records.")

    matches = [block for block in blocks if get_record_slug(block.group()) == slug]
    if len(matches) > 1:
        raise RuntimeError(
            f"Slug '{slug}' matches multiple existing records; refusing an ambiguous update."
        )
    if matches:
        match = matches[0]
        updated_block = match.group()
        values = {
            "displayName": json.dumps(metadata["displayName"], ensure_ascii=False),
            "weapon": json.dumps(metadata["weapon"]),
            "rarity": str(metadata["rarity"]),
            "attribute": json.dumps(metadata["attribute"]),
            "gender": json.dumps(metadata["gender"]),
        }
        for field, value in values.items():
            updated_block = replace_field(updated_block, field, value)
        return source[: match.start()] + updated_block + source[match.end() :]

    closing = re.search(r"(?m)^\];\s*$", source)
    if not closing:
        raise RuntimeError("Could not find the end of the characters array.")
    record = format_record(len(ids), slug, metadata["displayName"], metadata)
    return source[: closing.start()].rstrip() + "\n" + record + "\n" + source[closing.start() :]


def write_atomic(path, content):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary.flush()
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)
    finally:
        if temporary_path:
            temporary_path.unlink(missing_ok=True)


def import_resonators(names):
    slugs = [normalize_slug(name) for name in names]
    if any(not slug for slug in slugs):
        raise RuntimeError("Resonator names must not be empty.")
    if len(set(slugs)) != len(slugs):
        raise RuntimeError("The input contains duplicate names after slug normalization.")

    source = CHARACTER_DATA_FILE.read_text(encoding="utf-8")
    updated_source = source

    with tempfile.TemporaryDirectory(
        dir=CHARACTER_IMAGE_DIR,
        prefix=".resonator-import-",
    ) as temporary_dir:
        staged_images = []
        for name, slug in zip(names, slugs):
            print(f"Processing {name}...")
            metadata = fetch_resonator_metadata(name)
            image_url = fetch_image_url(name)
            staged_image = Path(temporary_dir) / f"{slug}.webp"
            download_and_convert(image_url, staged_image)
            updated_source = apply_record(updated_source, slug, metadata)
            staged_images.append((staged_image, f"{slug}.webp"))

        IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for staged_image, filename in staged_images:
            shutil.copy2(staged_image, IMAGE_OUTPUT_DIR / filename)
            shutil.copy2(staged_image, CHARACTER_IMAGE_DIR / filename)

    if updated_source != source:
        write_atomic(CHARACTER_DATA_FILE, updated_source)
    print(f"Imported {len(names)} resonator(s) and updated character data.")


def main():
    if len(sys.argv) < 2:
        print('Usage: download-resonators.sh "Name" "First Last" ...', file=sys.stderr)
        return 2
    try:
        import_resonators(sys.argv[1:])
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
