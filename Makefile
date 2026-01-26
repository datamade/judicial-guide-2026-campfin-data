YEAR=2026

all: clean data/final/campfin-${YEAR}.json

# don't automatically clean receipts.txt because
# it takes a long time to download.
# manually delete that file if you want to get uploaded data
.PHONY:
clean:
	rm -f data/final/campfin-${YEAR}.json \
		data/final/campfin-${YEAR}-pretty.json \
		data/raw/receipts-trimmed.txt

# condense and drop keys we don't need in prd
data/final/campfin-${YEAR}.json: data/final/campfin-${YEAR}-pretty.json
	jq -c 'map(del(.contributions))' $< > $@

data/final/campfin-${YEAR}-pretty.json: data/intermediate/receipts-trimmed.txt
	time python3 scripts/process_receipts.py $< > $@

data/intermediate/receipts-trimmed.txt: data/raw/receipts-header.txt data/raw/receipts-end.txt
	head -n 1 data/raw/receipts-header.txt >> $@
	tail -n +2 data/raw/receipts-end.txt >> $@

# The receipts file contains donations starting in 1994!
# Only fetch the last ~50MB of the file
data/raw/receipts-end.txt:
	curl --range -50000000 "https://www.elections.il.gov/CampaignDisclosureDataFiles/Receipts.txt" -o $@  

# Fetch enough of the beginning of the file to get the CSV header
data/raw/receipts-start.txt:
	curl --range 0-1000 "https://www.elections.il.gov/CampaignDisclosureDataFiles/Receipts.txt" -o $@
