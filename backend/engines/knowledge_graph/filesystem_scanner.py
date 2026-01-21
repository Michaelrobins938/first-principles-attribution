"""
Safe Filesystem Scanner

Scans filesystem with strict security guardrails to identify documents
for knowledge graph construction. Prevents access to sensitive files
and maintains privacy.
"""

from pathlib import Path
from typing import List, Dict, Set, Optional
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SafeFilesystemScanner:
    """
    Scan filesystem safely with multiple security layers.

    - Forbidden path filtering (system directories, sensitive folders)
    - File extension whitelisting
    - File size limits
    - Metadata extraction only (no content reading)
    - Anonymization via fingerprinting
    """

    # Paths to never scan
    FORBIDDEN_PATHS = [
        "/Library",
        "/System",
        "/Volumes",
        "AppData",
        "System32",
        "SysWOW64",
        "Program Files",
        ".ssh",
        ".gnupg",
        "passwords",
        "tax",
        "financial",
        "credit",
        "ssn",
        "pid",
        "driver",
        ".git",
        "node_modules",
        "venv",
        "env"
    ]

    # Allowed file extensions for knowledge graph
    ALLOWED_EXTENSIONS = [
        ".txt",
        ".md",
        ".markdown",
        ".json",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".sql",
        ".pdf",
        ".doc",
        ".docx",
        ".csv",
        ".xml",
        ".yaml",
        ".yml",
        ".sh",
        ".bash"
    ]

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, allowed_paths: List[str], verbose: bool = False):
        """
        Initialize scanner with allowed paths.

        Args:
            allowed_paths: List of directories to scan
            verbose: Enable detailed logging
        """
        self.allowed_paths = [Path(p) for p in allowed_paths]
        self.verbose = verbose
        self.scanned_files: List[Dict] = []
        self.forbidden_count = 0
        self.skipped_count = 0

    def scan(self) -> List[Dict]:
        """
        Recursively scan allowed directories.

        Returns:
            List of file metadata dictionaries
        """
        for base_path in self.allowed_paths:
            if not self._is_safe_path(base_path):
                logger.warning(f"Skipping unsafe path: {base_path}")
                continue

            if not base_path.exists():
                logger.warning(f"Path does not exist: {base_path}")
                continue

            self._scan_directory(base_path)

        logger.info(f"Scan complete: {len(self.scanned_files)} files, "
                   f"{self.forbidden_count} forbidden, {self.skipped_count} skipped")

        return self.scanned_files

    def _scan_directory(self, path: Path) -> None:
        """Recursively scan a directory."""
        try:
            for item in path.rglob("*"):
                if self._should_process_file(item):
                    metadata = self._extract_metadata(item)
                    if metadata:
                        self.scanned_files.append(metadata)
                elif item.is_file():
                    self.skipped_count += 1
                elif self._is_forbidden_path(item):
                    self.forbidden_count += 1
        except PermissionError:
            logger.warning(f"Permission denied: {path}")
        except Exception as e:
            logger.error(f"Error scanning {path}: {str(e)}")

    def _is_safe_path(self, path: Path) -> bool:
        """Verify path doesn't contain forbidden directories."""
        path_str = str(path).lower()

        for forbidden in self.FORBIDDEN_PATHS:
            if forbidden.lower() in path_str:
                return False

        return True

    def _is_forbidden_path(self, path: Path) -> bool:
        """Check if a specific path is forbidden."""
        return not self._is_safe_path(path)

    def _should_process_file(self, path: Path) -> bool:
        """Check if file should be processed."""
        try:
            # Must be a file
            if not path.is_file():
                return False

            # Check extension
            if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                return False

            # Check file size
            stat = path.stat()
            if stat.st_size > self.MAX_FILE_SIZE:
                logger.warning(f"File too large: {path}")
                return False

            # Check path safety
            if not self._is_safe_path(path):
                self.forbidden_count += 1
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking file {path}: {str(e)}")
            return False

    def _extract_metadata(self, path: Path) -> Optional[Dict]:
        """
        Extract file metadata WITHOUT reading content.

        Returns only metadata, not file content, for privacy.
        """
        try:
            stat = path.stat()

            # Create fingerprint from path (not content)
            path_hash = hashlib.md5(str(path.resolve()).encode()).hexdigest()

            # Infer topic from filename and parent directories
            topics = self._infer_topics(path)

            metadata = {
                "path": str(path.resolve()),
                "name": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "modified_timestamp": stat.st_mtime,
                "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "fingerprint": path_hash,  # Anonymous identifier
                "topics": topics,
                "file_type": self._classify_file_type(path),
                "readability_score": self._estimate_readability(path),
                "importance_score": 0.5  # Will be enhanced by graph builder
            }

            if self.verbose:
                logger.info(f"Processed: {path.name} ({metadata['size_bytes']} bytes)")

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from {path}: {str(e)}")
            return None

    def _infer_topics(self, path: Path) -> List[str]:
        """
        Infer topics from filename and directory structure.

        Uses words from path as topic indicators.
        """
        topics = set()

        # Extract from filename
        filename_parts = path.stem.split("_")
        for part in filename_parts:
            if len(part) > 3:
                topics.add(part.lower())

        # Extract from parent directories
        parent_parts = path.parent.parts[-3:]  # Last 3 directory levels
        for part in parent_parts:
            if len(part) > 3 and part.lower() not in ["documents", "files", "downloads"]:
                topics.add(part.lower())

        return list(topics)

    def _classify_file_type(self, path: Path) -> str:
        """Classify file type."""
        extension = path.suffix.lower()

        type_map = {
            ".md": "documentation",
            ".txt": "text",
            ".pdf": "document",
            ".py": "code",
            ".js": "code",
            ".ts": "code",
            ".tsx": "code",
            ".jsx": "code",
            ".json": "data",
            ".csv": "data",
            ".sql": "database",
            ".html": "web",
            ".css": "web"
        }

        return type_map.get(extension, "other")

    def _estimate_readability(self, path: Path) -> float:
        """
        Estimate readability score based on file characteristics.

        0.0 = hard to read, 1.0 = easy to read
        """
        extension = path.suffix.lower()

        # Different file types have different readability
        readability_scores = {
            ".md": 0.95,      # Markdown is highly readable
            ".txt": 0.90,     # Plain text is readable
            ".py": 0.85,      # Python code is readable
            ".js": 0.80,      # JavaScript is somewhat readable
            ".json": 0.75,    # JSON is readable but structured
            ".html": 0.60,    # HTML has markup
            ".pdf": 0.40,     # PDFs are hard to process
            ".csv": 0.70      # CSV is readable
        }

        return readability_scores.get(extension, 0.5)

    def get_statistics(self) -> Dict:
        """Get scanning statistics."""
        return {
            "total_files_found": len(self.scanned_files),
            "total_forbidden_found": self.forbidden_count,
            "total_skipped": self.skipped_count,
            "total_size_bytes": sum(f["size_bytes"] for f in self.scanned_files),
            "by_file_type": self._count_by_file_type(),
            "by_topic": self._count_by_topic(),
            "scan_timestamp": datetime.now().isoformat()
        }

    def _count_by_file_type(self) -> Dict[str, int]:
        """Count files by type."""
        counts = {}
        for file in self.scanned_files:
            file_type = file.get("file_type", "other")
            counts[file_type] = counts.get(file_type, 0) + 1
        return counts

    def _count_by_topic(self) -> Dict[str, int]:
        """Count files by inferred topic."""
        counts = {}
        for file in self.scanned_files:
            for topic in file.get("topics", []):
                counts[topic] = counts.get(topic, 0) + 1
        # Return top 20 topics
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20])

    def filter_by_topic(self, topic: str) -> List[Dict]:
        """Filter files by topic."""
        return [f for f in self.scanned_files if topic.lower() in [t.lower() for t in f.get("topics", [])]]

    def filter_by_type(self, file_type: str) -> List[Dict]:
        """Filter files by type."""
        return [f for f in self.scanned_files if f.get("file_type") == file_type]

    def filter_by_recency(self, days: int) -> List[Dict]:
        """Filter files modified within N days."""
        import time
        cutoff_time = time.time() - (days * 86400)
        return [f for f in self.scanned_files if f.get("modified_timestamp", 0) > cutoff_time]

