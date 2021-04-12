# Instructions

## Options

|----|----|
|`--stats` | Print stats at beginning of session|
|`--sched` | Print upcoming schedule at beginning of session |
|`-v` | Print debug messages|
| `-n` | Add first 20 cards not currently in deck into deck |
|`-a` | Enter "Add mode" where you may add specific alphagrams to deck |
| `-h` | Print options |

## Word Data

To run this script, you will need the lexicon saved as `word_data.txt` within the same directory as the script.

`word_data.txt` should contain a single JSON object of the form:

```JSON
{
	"ADEINOR": [
		{
			"word": "ANEROID",
			"definition": "a type of barometer [n ANEROIDS]",
			"front_hooks": "",
			"back_hooks": "s",
			"probability_order": "1"
		}
	],
	"AEILNOR": [
		{
			"word": "AILERON",
			"definition": "a movable control surface on an airplane wing [n AILERONS]",
			"front_hooks": "",
			"back_hooks": "s",
			"probability_order": "2"
		},
		{
			"word": "ALIENOR",
			"definition": "one that transfers property [n ALIENORS]",
			"front_hooks": "",
			"back_hooks": "s",
			"probability_order": "3"
		}
	]
}
```