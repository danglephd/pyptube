"""
Test suite for pyptube YouTube tracker application
"""
import unittest
import sqlite3
import re
import os
import tempfile
from datetime import datetime

# Test regex pattern
YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)


def is_youtube_link(text):
    if not text:
        return False
    return YOUTUBE_REGEX.match(text.strip()) is not None


class TestYouTubeRegex(unittest.TestCase):
    """Test YouTube URL detection"""

    def test_valid_youtube_urls(self):
        """Test valid YouTube URLs are detected"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "www.youtube.com/watch?v=abc123",
            "youtube.com/watch?v=abc123",
            "https://youtu.be/dQw4w9WgXcQ",
            "youtu.be/abc123",
            "https://www.youtube.com/channel/UCxxx",
            "https://www.youtube.com/playlist?list=xxx",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_youtube_link(url), f"Failed to detect: {url}")

    def test_invalid_urls(self):
        """Test non-YouTube URLs are rejected"""
        invalid_urls = [
            "https://www.google.com",
            "https://github.com",
            "https://vimeo.com/video",
            "youtube.com",  # No path
            "youtu.be",  # No path
            "not a url",
            "",
            "   ",
            None,
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_youtube_link(url), f"Wrongly detected: {url}")

    def test_youtube_with_whitespace(self):
        """Test YouTube URLs with whitespace are handled"""
        url_with_spaces = "  https://www.youtube.com/watch?v=abc123  "
        self.assertTrue(is_youtube_link(url_with_spaces))


class TestDatabase(unittest.TestCase):
    """Test SQLite database operations"""

    def setUp(self):
        """Create a temporary database for testing"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_path = self.db_file.name
        self.db_file.close()
        
        # Create connection and table
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            created_at TEXT
        )
        """)
        self.conn.commit()

    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_insert_link(self):
        """Test inserting a YouTube link"""
        url = "https://www.youtube.com/watch?v=test123"
        created_at = datetime.now().isoformat()
        
        self.cursor.execute(
            "INSERT INTO youtube_links (url, created_at) VALUES (?, ?)",
            (url, created_at)
        )
        self.conn.commit()
        
        # Verify insertion
        self.cursor.execute("SELECT url FROM youtube_links WHERE url = ?", (url,))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], url)

    def test_duplicate_link_raises_error(self):
        """Test that duplicate URLs raise IntegrityError"""
        url = "https://www.youtube.com/watch?v=test123"
        created_at = datetime.now().isoformat()
        
        # First insertion
        self.cursor.execute(
            "INSERT INTO youtube_links (url, created_at) VALUES (?, ?)",
            (url, created_at)
        )
        self.conn.commit()
        
        # Second insertion should fail
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                "INSERT INTO youtube_links (url, created_at) VALUES (?, ?)",
                (url, created_at)
            )
            self.conn.commit()

    def test_retrieve_all_links(self):
        """Test retrieving all saved links"""
        urls = [
            "https://www.youtube.com/watch?v=url1",
            "https://www.youtube.com/watch?v=url2",
            "https://youtu.be/url3",
        ]
        
        for url in urls:
            created_at = datetime.now().isoformat()
            self.cursor.execute(
                "INSERT INTO youtube_links (url, created_at) VALUES (?, ?)",
                (url, created_at)
            )
        self.conn.commit()
        
        # Retrieve all
        self.cursor.execute("SELECT url FROM youtube_links")
        results = self.cursor.fetchall()
        
        self.assertEqual(len(results), 3)
        retrieved_urls = [r[0] for r in results]
        self.assertEqual(set(retrieved_urls), set(urls))


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_workflow(self):
        """Test complete workflow"""
        # Create test database
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        db_path = db_file.name
        db_file.close()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            created_at TEXT
        )
        """)
        conn.commit()
        
        # Test: Save multiple links
        test_links = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Valid
            "https://youtu.be/RickRoll",  # Valid
            "https://www.google.com",  # Invalid - should not be saved
        ]
        
        saved = 0
        for link in test_links:
            if is_youtube_link(link):
                try:
                    cursor.execute(
                        "INSERT INTO youtube_links (url, created_at) VALUES (?, ?)",
                        (link, datetime.now().isoformat())
                    )
                    conn.commit()
                    saved += 1
                except sqlite3.IntegrityError:
                    pass
        
        self.assertEqual(saved, 2)
        
        # Verify only YouTube links were saved
        cursor.execute("SELECT COUNT(*) FROM youtube_links")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        
        # Cleanup
        conn.close()
        os.remove(db_path)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
