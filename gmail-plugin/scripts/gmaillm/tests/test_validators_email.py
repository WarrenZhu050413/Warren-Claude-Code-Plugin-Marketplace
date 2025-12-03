"""Tests for gmaillm.validators.email module."""

import pytest
from pathlib import Path

from gmaillm.validators.email import (
    validate_email,
    validate_email_list,
    validate_attachment_paths,
    validate_label_name,
    validate_editor
)


class TestValidateEmail:
    """Tests for validate_email function."""

    def test_valid_emails(self):
        """Test that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "user123@example.co.uk",
            "user@subdomain.example.com",
            "a@b.co",
        ]
        for email in valid_emails:
            assert validate_email(email), f"{email} should be valid"

    def test_invalid_emails(self):
        """Test that invalid email addresses fail validation."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user",
            "user@.com",
            "user@example",
            "",
            "user @example.com",  # Space
            "user@example .com",  # Space
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"{email} should be invalid"


class TestValidateEmailList:
    """Tests for validate_email_list function."""

    def test_valid_email_list(self):
        """Test that valid email lists pass validation."""
        emails = ["user1@example.com", "user2@example.com"]
        # Should not raise
        validate_email_list(emails)

    def test_group_references_allowed(self):
        """Test that group references (starting with #) are allowed."""
        emails = ["#team", "user@example.com"]
        # Should not raise
        validate_email_list(emails)

    def test_invalid_email_in_list(self):
        """Test that invalid emails in list raise typer.Exit."""
        import typer
        emails = ["valid@example.com", "invalid-email"]
        with pytest.raises(typer.Exit):
            validate_email_list(emails)

    def test_custom_field_name(self):
        """Test custom field name in error message."""
        import typer
        emails = ["invalid"]
        with pytest.raises(typer.Exit):
            validate_email_list(emails, field_name="recipient")


class TestValidateAttachmentPaths:
    """Tests for validate_attachment_paths function."""

    def test_none_attachments(self):
        """Test that None returns None."""
        assert validate_attachment_paths(None) is None

    def test_empty_list(self):
        """Test that empty list returns None."""
        assert validate_attachment_paths([]) is None

    def test_valid_file_paths(self, temp_dir):
        """Test that valid file paths are validated and resolved."""
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.pdf"
        file1.write_text("test")
        file2.write_text("test")

        paths = [str(file1), str(file2)]
        result = validate_attachment_paths(paths)

        assert result is not None
        assert len(result) == 2
        assert all(Path(p).is_absolute() for p in result)

    def test_nonexistent_file(self, temp_dir):
        """Test that nonexistent file raises typer.Exit."""
        import typer
        paths = [str(temp_dir / "nonexistent.txt")]
        with pytest.raises(typer.Exit):
            validate_attachment_paths(paths)

    def test_directory_not_file(self, temp_dir):
        """Test that directory path raises typer.Exit."""
        import typer
        paths = [str(temp_dir)]
        with pytest.raises(typer.Exit):
            validate_attachment_paths(paths)


class TestValidateLabelName:
    """Tests for validate_label_name function."""

    def test_valid_label_names(self):
        """Test that valid label names pass validation."""
        valid_names = [
            "my-label",
            "Work",
            "Project_A",
            "1234",
            "a",
            "Label with spaces",
        ]
        for name in valid_names:
            # Should not raise
            validate_label_name(name)

    def test_empty_label_name(self):
        """Test that empty label name raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_label_name("")

    def test_label_name_too_long(self):
        """Test that label name exceeding max length raises typer.Exit."""
        import typer
        # Default max is 225 chars
        long_name = "a" * 226
        with pytest.raises(typer.Exit):
            validate_label_name(long_name)

    def test_invalid_characters(self):
        """Test that invalid characters raise typer.Exit."""
        import typer
        invalid_names = [
            "label<test>",
            "label&test",
            'label"test',
            "label'test",
            "label`test",
        ]
        for name in invalid_names:
            with pytest.raises(typer.Exit):
                validate_label_name(name)


class TestValidateEditor:
    """Tests for validate_editor function."""

    def test_valid_editors(self):
        """Test that valid editor names pass validation."""
        valid_editors = [
            "vim",
            "emacs",
            "nano",
            "code",
            "subl",
            "nvim",
        ]
        for editor in valid_editors:
            # Should not raise
            validate_editor(editor)

    def test_invalid_editor_with_space(self):
        """Test that editor with space raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("vim -R")

    def test_invalid_editor_with_semicolon(self):
        """Test that editor with semicolon raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("vim;ls")

    def test_invalid_editor_with_pipe(self):
        """Test that editor with pipe raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("vim|cat")

    def test_invalid_editor_with_ampersand(self):
        """Test that editor with ampersand raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("vim&")

    def test_invalid_editor_with_dollar(self):
        """Test that editor with dollar raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("$EDITOR")

    def test_invalid_editor_with_backtick(self):
        """Test that editor with backtick raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_editor("vim`whoami`")
