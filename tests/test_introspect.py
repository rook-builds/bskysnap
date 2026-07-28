"""Tests for bskysnap.introspect."""

import json

import pytest

from bskysnap.introspect import get_introspect_json, get_skill_md


class TestGetIntrospectJson:
    def test_is_valid_json(self):
        result = get_introspect_json()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tool_field(self):
        data = json.loads(get_introspect_json())
        assert data["tool"] == "bskysnap"

    def test_has_version(self):
        data = json.loads(get_introspect_json())
        assert "version" in data
        assert data["version"] == "0.1.0"

    def test_has_commands(self):
        data = json.loads(get_introspect_json())
        assert "commands" in data

    def test_has_default_command(self):
        data = json.loads(get_introspect_json())
        assert "default" in data["commands"]

    def test_default_has_limit_option(self):
        data = json.loads(get_introspect_json())
        options = data["commands"]["default"]["options"]
        assert "--limit" in options

    def test_default_has_output_option(self):
        data = json.loads(get_introspect_json())
        options = data["commands"]["default"]["options"]
        assert "--output" in options

    def test_output_has_choices(self):
        data = json.loads(get_introspect_json())
        choices = data["commands"]["default"]["options"]["--output"]["choices"]
        assert "text" in choices
        assert "json" in choices
        assert "table" in choices
        assert "csv" in choices

    def test_has_introspect_command(self):
        data = json.loads(get_introspect_json())
        assert "introspect" in data["commands"]

    def test_has_skill_command(self):
        data = json.loads(get_introspect_json())
        assert "skill" in data["commands"]


class TestGetSkillMd:
    def test_starts_with_yaml_frontmatter(self):
        result = get_skill_md()
        assert result.startswith("---")

    def test_has_name(self):
        result = get_skill_md()
        assert "name: bskysnap" in result

    def test_has_description(self):
        result = get_skill_md()
        assert "description:" in result

    def test_has_core_usage_section(self):
        result = get_skill_md()
        assert "## Core usage" in result

    def test_has_exit_codes_section(self):
        result = get_skill_md()
        assert "## Exit codes" in result

    def test_has_agent_discovery_section(self):
        result = get_skill_md()
        assert "## Agent discovery" in result

    def test_mentions_no_auth(self):
        result = get_skill_md()
        assert "No authentication" in result or "no auth" in result.lower()
