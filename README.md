# Wuthering Waves Team Randomizer

> Simple app to randomize your teams in Wuthering Waves

## Usage

Select or deselect character cards and click "Generate teams."

## Features

- Settings are locally saved

## Importing resonators

> [!IMPORTANT]
> Scripts are created using copilot, please read the script in its entirety before running it!

The resonator importer requires Python 3 and ImageMagick (`convert`). It retrieves
resonator metadata and artwork from the Wuthering Waves wiki:

```sh
./download-resonators.sh "Hsin" "Yangyang Xuanling"
```

The importer validates metadata against the app's supported types, uses lowercase
hyphenated slugs for image filenames, and adds or updates entries in
`src/lib/data/characters.ts`. Images are saved in both `resonators/` and
`src/lib/images/characters/`.

The older image-only downloader is available as `download-resonators-legacy.sh`.
It saves images only to `resonators/` and does not update character data.

## Motivation

I wanted to learn Svelte and built this app. It is inspired by [Genshin Impact Team Randomizer](https://genshin-impact-team-randomizer.pages.dev/).

## Changelog

[CHANGELOG](CHANGELOG.md)

## License

[MIT](LICENSE)
