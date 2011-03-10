## torrent-search-console - search for torrents from command line

This is simple console application/command for finding torrents using plugins from [Torrent Search GUI application](http://torrent-search.sourceforge.net).

Output can be easily piped to other UNIX command line tools like grep, awk, cut... or similar for further processing.

### Requirements

* Torrent Search - <http://torrent-search.sourceforge.net/download> (tested with 0.9.2)

### Usage examples

Timeout set to 20secs:

    $ torrent-search-console -t 20 arch linux 2>/dev/null

	plugin: .../000001_BTSCENE
	plugin: .../000002_SUMO
	...
	result:|BTSCENE|176.57 MB|Arch Linux (2/5/10) NEW!|2010-02-07|4|1||
	result:|BTSCENE|311.15 MB|Arch Linux 2009 02 i686 iso|2009-02-18|0|0||
	...

Results on isoHunt sorted by number of seeders (descending):

	$ torrent-search-console -t 10 -p isohunt arch linux 2>/dev/null | grep ^result: | sort -r -n -k6 -t\| | column -t -s\|

From other Python code:

	$ python2 -c '
	import torrent_search_console as ts; from pprint import pprint
	pprint(ts.run_silently(*ts.parser.parse_args(["-t5", "-pisohunt", "arch", "linux"])))
	' 2>/dev/null

I had to redirect standard error to /dev/null because of huge amount of HTML parsing errors.

### License

WTFPL

