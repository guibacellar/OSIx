# OSIx - **O**pen **S**ource **I**ntelligence e**X**plorer 

**Version:** 0.0.2

**By:** Th3 0bservator

[![QA](https://github.com/guibacellar/OSIx/actions/workflows/qa.yml/badge.svg?branch=develop)](https://github.com/guibacellar/OSIx/actions/workflows/qa.yml)
![](https://img.shields.io/github/last-commit/guibacellar/OSIx)
![](https://img.shields.io/github/languages/code-size/guibacellar/OSIx)
![](https://img.shields.io/badge/Python-3.7.6+-green.svg)
![](https://img.shields.io/badge/maintainer-Th3%200bservator-blue)
----

OSIx is a Python tool to Explore the Open Source Intelligence Data, created to help Researchers, Investigators and Law Enforcement Agents to Collect and Process OSINT Data.

Created using a Modular Architecture, the OSIx easily allows to add new modules to enrich the available functionalities.

----

# Download & Install

## Release
```bash
wget https://github.com/guibacellar/OSIx/archive/master.zip
unzip -o master.zip
mv OSIx-master/ OSIx
pip3 install -r OSIx/requirements.txt
rm -rf master.zip
```

## Develop
```bash
wget https://github.com/guibacellar/OSIx/archive/develop.zip
unzip -o develop.zip
mv OSIx-develop/ OSIx
pip3 install -r OSIx/requirements.txt
rm -rf develop.zip
```

---

# Available Modules

 * [Bitcoin Wallet Info & Transactions](docs/module_btc_waller.md)
 * Username Search (TBD Documentation)
---

# Basic Command Line

### Jobname

The *job_name* parameter allow to specify a job name to the executor and the executor will save a state file with all parameters and configurations.

```bash
python OSIx.py --job_name MY_JOB
```

### Purge All Temporary Files

The *purge_temp_files* parameter tell's to the executor to cleanup all generated temporary files.

```bash
python OSIx.py --purge_temp_files
```

# Output Example
```bash
python3 OSIx.py --job_name dev_001 \
        --username marcos --username_allow_nsfw_scan \
        --username_print_result --username_enable_dump_file


OSIx - Open Source Intelligence eXplorer
Version: 0.0.2
By: Th3 0bservator

[*] Loading Configurations:
[*] Installed Modules:
	bitcoin_wallet.py
	bitcoin_wallet_graph.py
	http_navigation_manager.py
	input_args_handler.py
	state_file_handler.py
	temp_file_manager.py
	username_handler.py
[*] Executing Pipeline:
	[+] input_args_handler.InputArgsHandler
		job_name = dev_001
		purge_temp_files = False
		btc_wallet = 
		btc_get_transactions = 
		export_btc_transactions_as_graphml = False
		export_btc_transactions_as_gephi = True
		username = marcos
		username_allow_nsfw_scan = True
		username_print_result = True
		username_show_all = False
		username_enable_dump_file = True
	[+] temp_file_manager.TempFileManager
 		Checking Age data/temp/state for 31557600 seconds
 		Checking Age data/temp/bitcoin_wallet for 604800 seconds
 		Checking Age data/temp/username_search for 604800 seconds
	[+] state_file_handler.LoadStateFileHandler
	[+] http_navigation_manager.HttpNavigationManagerHandler
	[+] bitcoin_wallet.BitcoinWalletInfoDownloader
		Target BTC Wallet Empty.
	[+] bitcoin_wallet.BitcoinWalletTransactionsDownloader
	[+] bitcoin_wallet_graph.BitcoinWalletGraphGenerator
		Target BTC Wallet Empty.
	[+] username_handler.UsernameScanner
		NSFW Sites Allowed.
		Starting Scan with 20 Workers.
		7Cups: Claimed > https://www.7cups.com/@marcos
		9GAG: Claimed > https://www.9gag.com/u/marcos
		About.me: Claimed > https://about.me/marcos
		Academia.edu: Claimed > https://independent.academia.edu/marcos
		Asciinema: Claimed > https://asciinema.org/~marcos
		AskFM: Claimed > https://ask.fm/marcos
		Atom Discussions: Claimed > https://discuss.atom.io/u/marcos/summary
		Audiojungle: Claimed > https://audiojungle.net/user/marcos
		Avizo: Claimed > https://www.avizo.cz/marcos/
		BLIP.fm: Claimed > https://blip.fm/marcos
		Bandcamp: Claimed > https://www.bandcamp.com/marcos
		Behance: Claimed > https://www.behance.net/marcos
		BitBucket: Claimed > https://bitbucket.org/marcos/
		Blogger: Claimed > https://marcos.blogspot.com
		BodyBuilding: Claimed > https://bodyspace.bodybuilding.com/marcos
		Bookcrossing: Claimed > https://www.bookcrossing.com/mybookshelf/marcos/
		BuzzFeed: Claimed > https://buzzfeed.com/marcos
		CNET: Claimed > https://www.cnet.com/profiles/marcos/
		CapFriendly: Claimed > https://www.capfriendly.com/users/marcos
		Carbonmade: Claimed > https://marcos.carbonmade.com
		Career.habr: Claimed > https://career.habr.com/marcos
		Championat: Claimed > https://www.championat.com/user/marcos
		Chatujme.cz: Claimed > https://profil.chatujme.cz/marcos
		Cloob: Claimed > https://www.cloob.com/name/marcos
		Codecademy: Claimed > https://www.codecademy.com/profiles/marcos
		Codechef: Claimed > https://www.codechef.com/users/marcos
		Coroflot: Claimed > https://www.coroflot.com/marcos
		DEV Community: Claimed > https://dev.to/marcos
		Designspiration: Claimed > https://www.designspiration.net/marcos/
		DeviantART: Claimed > https://marcos.deviantart.com
	[+] state_file_handler.SaveStateFileHandler


```