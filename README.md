# OSIx
Open Source Intelligence eXplorer

By: Th3 0bservator

----

OSIx is a Python tool to Explore the Open Source Intelligence Data. 

Created using a Modular Architecture, the OSIx easily allow to add new modules to enrich the available functionalities.

> Compatible with Python 3.7.6+

----

# Download

---

# Available Modules

 * [Bitcoin Wallet Info & Transactions](docs/module_btc_waller.md)
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