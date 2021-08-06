# OSIx - 0.0.2
Open Source Intelligence eXplorer

**By:** Th3 0bservator

**Repo:** [https://github.com/guibacellar/OSIx](https://github.com/guibacellar/OSIx)

----

OSIx is a Python tool to Explore the Open Source Intelligence Data, created to help Researchers, Investigators and Law Enforcement Agents to Collect and Process OSINT Data.

Created using a Modular Architecture, the OSIx easily allows to add new modules to enrich the available functionalities.

# Requirements
 
 * Python 3.7.6+
 * Windows, Linux or Mac OS

# Roadmap

 * Username Search
 * Email Search
 * Social Network Account Search

----

# Download

TBD

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
