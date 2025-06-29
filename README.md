How to use
**STEP 0
Prerequisites**
Install the required Python libraries before you begin:
pip3 install --user tqdm colorama matplotlib

**STEP 1**
**hash_generator.py** quickstart
Compute SHA256 hashes for all .dat files under data/, writing results to hashes.txt using 4 parallel workers:
cli: python3 hash_generator.py data hashes.txt --workers 4
data — root folder containing your blockchain .dat files
hashes.txt — output file (<hash> <relative_path>)
--workers 4 — use 4 threads for hashing (with nvme samsung 970 evo plus and ryzen 5950x optimal is 4-6)

**STEP 2**
**comparehashes.py** quickstart
Compare two hash‐lists, generate a colored console summary, detailed report and histogram:

python3 comparehashes.py hashes_original.txt hashes.txt --output diff_report.txt --plot --bins 50
hashes_original.txt – donor (reference) hashes
hashes.txt – local hashes
--output diff_report.txt – write full report
--plot – save PNG (diff_histogram.png) & show ASCII chart
--bins 50 – number of histogram buckets

**STEP 3**
**generate_sync_list.py** quickstart
Produce a sync‐list of missing or mismatched files for rsync:

python3 generate_sync_list.py hashes_original.txt hashes.txt --output to_sync.txt
reads donor vs local hashes

writes relative paths (e.g. blocks/...) to to_sync.txt for selective syncing.

**STEP 3**
**use rsync **
rsync -avz --files-from=FILE_LIST user@host:/path/to/source/ /path/to/destination/
-a archive mode (preserves permissions, timestamps, etc.)
-v verbose output
-z compress data during transfer
--files-from=FILE_LIST list of relative paths to sync
user@host:/path/to/source/ remote user, host, and source directory
/path/to/destination/ local target directory
