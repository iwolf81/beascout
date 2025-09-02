#!/bin/zsh

# Usage: ./search_phrases.zsh phrases.txt /path/to/search/dir

phrase_file="$1"
search_dir="$2"

if [[ ! -f "$phrase_file" ]]; then
  echo "Error: phrase file '$phrase_file' not found"
  exit 1
fi

if [[ ! -d "$search_dir" ]]; then
  echo "Error: search directory '$search_dir' not found"
  exit 1
fi

while IFS= read -r phrase
do
  # Skip empty lines
  [[ -z "$phrase" ]] && continue

  echo "🔎 Searching for: \"$phrase\""
  grep -R -l "$phrase" "$search_dir"/* || echo "   (no matches found)"
  echo
done < "$phrase_file"
