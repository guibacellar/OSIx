"""OSIx Root."""
from OSIx.core.dir_manager import DirectoryManagerUtils

DirectoryManagerUtils.ensure_dir_struct('data/')
DirectoryManagerUtils.ensure_dir_struct('data/export/')