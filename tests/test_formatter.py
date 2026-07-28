"""Tests for bskysnap.formatter."""

import csv
import io
import json

import pytest

from bskysnap.formatter import to_csv, to_json, to_table, to_text


class TestToText:
    def test_includes_handle(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "@bsky.app" in result

    def test_includes_display_name(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "Bluesky" in result

    def test_includes_description(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "AT Protocol" in result

    def test_includes_follower_count(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "119,916" in result

    def test_includes_post_text(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "Hello from Bluesky!" in result

    def test_includes_engagement_counts(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "42" in result   # likes
        assert "5" in result    # replies

    def test_includes_web_url(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "https://bsky.app/profile/bsky.app/post/rkey001" in result

    def test_repost_marked(self, sample_profile, sample_posts):
        result = to_text(sample_profile, sample_posts)
        assert "repost" in result.lower()

    def test_empty_posts(self, sample_profile, empty_posts):
        result = to_text(sample_profile, empty_posts)
        assert "No posts found" in result


class TestToJson:
    def test_is_valid_json(self, sample_profile, sample_posts):
        result = to_json(sample_profile, sample_posts)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tool_field(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert data["tool"] == "bskysnap"

    def test_has_posts_array(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert "posts" in data
        assert isinstance(data["posts"], list)
        assert len(data["posts"]) == 2

    def test_post_has_uri(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert "uri" in data["posts"][0]

    def test_post_has_text(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert data["posts"][0]["text"] == "Hello from Bluesky!"

    def test_post_has_like_count(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert data["posts"][0]["like_count"] == 42

    def test_post_has_is_repost(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert data["posts"][0]["is_repost"] is False
        assert data["posts"][1]["is_repost"] is True

    def test_post_has_web_url(self, sample_profile, sample_posts):
        data = json.loads(to_json(sample_profile, sample_posts))
        assert "web_url" in data["posts"][0]


class TestToTable:
    def test_has_date_header(self, sample_posts):
        result = to_table(sample_posts)
        assert "date" in result

    def test_has_likes_header(self, sample_posts):
        result = to_table(sample_posts)
        assert "likes" in result

    def test_includes_truncated_text(self, sample_posts):
        result = to_table(sample_posts)
        assert "Hello from Bluesky!" in result

    def test_empty_posts(self, empty_posts):
        result = to_table(empty_posts)
        assert "No posts found" in result


class TestToCsv:
    def test_first_line_is_header(self, sample_posts):
        result = to_csv(sample_posts)
        reader = csv.reader(io.StringIO(result))
        header = next(reader)
        assert "date" in header
        assert "text" in header
        assert "url" in header

    def test_second_line_has_post_data(self, sample_posts):
        result = to_csv(sample_posts)
        reader = csv.reader(io.StringIO(result))
        next(reader)  # skip header
        row = next(reader)
        assert "Hello from Bluesky!" in row

    def test_handles_commas_in_text(self, sample_posts):
        # The second post has commas — csv quoting should handle it
        result = to_csv(sample_posts)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 3  # header + 2 posts

    def test_correct_column_count(self, sample_posts):
        result = to_csv(sample_posts)
        reader = csv.reader(io.StringIO(result))
        header = next(reader)
        data_row = next(reader)
        assert len(data_row) == len(header)
