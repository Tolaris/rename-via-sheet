# rename-via-sheets.py

Given a set of source,destination filename pairs in a Google Sheet, rename the
files.

## Creating the Google Sheet

Create your sheet with a header row in this format:

| Source  | Destination |
|---------|-------------|
| foo.txt | bar.txt     |
| baz.txt | qux.txt     |
| qux.txt | baz.txt     |

What is ignored:

 * The first row, regardless of content
 * Columns C and beyond, regardless of content
 * Any row where cell A or B is empty

## How renames are done

Pseudocode:

 * for each pair:
   * generate a unique tempfile
 * for each pair in row order from to bottom:
   * rename source to tempfile
   * rename tempfile to destination

Therefore you can swap baz.txt and qux.txt without risk of overwriting each
other.

Renames are performed **relative to the current working directory**, using
[os.replace()](https://docs.python.org/3/library/os.html#os.replace).

## Example usage

Dry run:

```
cd /path/to/files
/home/tjwagner/Private/src/rename-via-sheet/rename-via-sheet.py -s
1yaaa-aaaaaaaaaaaaaaaaaaaaaaaaaaaaa-aaaaaaaa -n
```

Actually rename:

```
/home/tjwagner/Private/src/rename-via-sheet/rename-via-sheet.py -s
1yaaa-aaaaaaaaaaaaaaaaaaaaaaaaaaaaa-aaaaaaaa
```

## Getting a Google Sheets API key

Follow the [Google Sheets Python API
Quickstart](https://developers.google.com/sheets/api/quickstart/python) to
generate an API key. Store it in credentials.json alongside the python script.
