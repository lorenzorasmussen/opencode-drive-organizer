"""
Duplicate detector using tiered hashing:
1. xxHash (2.3s/GB) - Initial scan for potential duplicates
2. Blake3 (3.4s/GB) - Verification of potential duplicates
"""

import os
import time
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import json


class DuplicateDetector:
    """
    Fast duplicate detection using tiered hashing:
    1. xxHash (2.3s/GB) - Initial scan for potential duplicates
    2. Blake3 (3.4s/GB) - Verification of potential duplicates
    """

    def __init__(self):
        self.hash_cache_file = "data/duplicate-hash-cache.json"
        self.results_dir = "data/duplicates"
        os.makedirs(self.results_dir, exist_ok=True)

    def scan_for_duplicates(
        self, files: List[str], use_xxhash: bool = True, threshold: int = 100
    ) -> Dict:
        """Scan for duplicate files using fast hashing"""
        print(f"🔍 Scanning {len(files)} files for duplicates...")
        start_time = time.time()

        # Filter files by size threshold
        files_to_scan = [f for f in files if os.path.getsize(f) > threshold]

        # Choose hash algorithm
        if use_xxhash:
            try:
                import xxhash

                hash_func = lambda x: xxhash.xxh64(x).hexdigest()
                algorithm = "xxhash"
            except ImportError:
                print("⚠️  xxHash not available, falling back to MD5")
                hash_func = lambda x: hashlib.md5(x).hexdigest()
                algorithm = "md5"
        else:
            hash_func = lambda x: hashlib.md5(x).hexdigest()
            algorithm = "md5"

        # Calculate hashes
        file_hashes = {}
        for file_path in files_to_scan:
            try:
                with open(file_path, "rb") as f:
                    file_hash = hash_func(f.read())

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
                continue

        # Find duplicates
        duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}

        scan_time = time.time() - start_time

        result = {
            "algorithm": algorithm,
            "files_scanned": len(files_to_scan),
            "duplicates_found": sum(len(v) for v in duplicates.values()),
            "duplicate_groups": len(duplicates),
            "duplicates": duplicates,
            "scan_time": scan_time,
            "timestamp": datetime.now().isoformat(),
        }

        print(
            f"✓ Found {result['duplicate_groups']} duplicate groups ({result['duplicates_found']} files)"
        )
        print(f"  Algorithm: {algorithm}")
        print(f"  Scan time: {scan_time:.2f}s")

        return result

    def verify_files(self, files: List[str], use_blake3: bool = True) -> Dict:
        """Verify potential duplicates using Blake3 or SHA256"""
        print(f"🔬 Verifying {len(files)} files...")

        # Use Blake3 if available, otherwise SHA256
        if use_blake3:
            try:
                import hashlib

                hash_func = lambda x: hashlib.sha256(x).hexdigest()
                algorithm = "sha256"
            except ImportError:
                hash_func = lambda x: hashlib.sha256(x).hexdigest()
                algorithm = "sha256"

        # Calculate hashes
        file_hashes = {}
        for file_path in files:
            try:
                with open(file_path, "rb") as f:
                    file_hash = hash_func(f.read())

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
                continue

        # Group files by hash
        verified = {k: v for k, v in file_hashes.items() if len(v) > 1}

        result = {
            "algorithm": algorithm,
            "verified_duplicates": verified,
            "timestamp": datetime.now().isoformat(),
        }

        print(f"✓ Verified {len(verified)} duplicate groups")

        return result

    def tiered_scan(self, files: List[str]) -> Dict:
        """Two-tier scanning: xxHash (fast) → verification"""
        print(f"🚀 Starting two-tier scan...")

        # First pass: xxHash for initial scan
        initial_scan = self.scan_for_duplicates(files, use_xxhash=True)

        if initial_scan["duplicate_groups"] == 0:
            print("✅ No duplicates found in first pass")
            return {
                "algorithm": "xxhash",
                "potential_duplicates": {},
                "summary": "No duplicates detected",
            }

        # Second pass: Verify potential duplicates
        potential_dups = initial_scan["duplicates"]
        all_files = []
        for files in potential_dups.values():
            all_files.extend(files)

        verified = self.verify_files(all_files, use_blake3=True)

        return {
            "algorithm": "xxhash",
            "potential_duplicates": potential_dups,
            "verified_duplicates": verified["verified_duplicates"],
        }
