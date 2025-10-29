"""Tests for gmaillm.validators.groups module."""

import pytest

from gmaillm.validators.groups import GroupValidator, GroupValidationError


class TestGroupValidationError:
    """Test GroupValidationError dataclass."""

    def test_error_creation(self):
        """Test creating a validation error."""
        error = GroupValidationError(
            group_name="team",
            error_type="invalid_email",
            message="Invalid email format",
            details={"email": "invalid"}
        )
        assert error.group_name == "team"
        assert error.error_type == "invalid_email"
        assert error.message == "Invalid email format"
        assert error.details == {"email": "invalid"}

    def test_error_str_representation(self):
        """Test string representation of error."""
        error = GroupValidationError(
            group_name="team",
            error_type="duplicate",
            message="Duplicate email found"
        )
        assert str(error) == "[team] duplicate: Duplicate email found"

    def test_error_without_details(self):
        """Test error creation without details."""
        error = GroupValidationError(
            group_name="group1",
            error_type="circular_ref",
            message="Circular reference detected"
        )
        assert error.details is None


class TestGroupValidator:
    """Test GroupValidator class."""

    def test_validator_initialization(self):
        """Test creating a GroupValidator instance."""
        validator = GroupValidator()
        assert validator is not None


class TestValidateGroup:
    """Test validate_group method."""

    def test_valid_group_with_emails(self):
        """Test validating a group with valid emails."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "alice@example.com",
            "bob@example.com"
        ])
        assert errors == []

    def test_valid_group_with_group_references(self):
        """Test validating a group with group references (not validated here)."""
        validator = GroupValidator()
        errors = validator.validate_group("all", [
            "#team",
            "#clients"
        ])
        # Group references are skipped in single group validation
        assert errors == []

    def test_valid_group_mixed_emails_and_groups(self):
        """Test validating a group with mixed emails and group refs."""
        validator = GroupValidator()
        errors = validator.validate_group("mixed", [
            "alice@example.com",
            "#team",
            "bob@example.com"
        ])
        assert errors == []

    def test_invalid_email_format(self):
        """Test group with invalid email format."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "valid@example.com",
            "invalid-email",
            "another@example.com"
        ])

        assert len(errors) == 1
        assert errors[0].group_name == "team"
        assert errors[0].error_type == "invalid_email"
        assert "invalid-email" in errors[0].message
        assert errors[0].details == {"email": "invalid-email"}

    def test_multiple_invalid_emails(self):
        """Test group with multiple invalid emails."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "valid@example.com",
            "invalid1",
            "invalid2",
            "also-bad"
        ])

        assert len(errors) == 3
        invalid_emails = {err.details["email"] for err in errors}
        assert invalid_emails == {"invalid1", "invalid2", "also-bad"}

    def test_duplicate_emails(self):
        """Test group with duplicate emails."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "alice@example.com",
            "bob@example.com",
            "alice@example.com"  # Duplicate
        ])

        assert len(errors) == 1
        assert errors[0].error_type == "duplicate"
        assert errors[0].details == {"email": "alice@example.com"}

    def test_multiple_duplicates(self):
        """Test group with multiple duplicate emails."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "alice@example.com",
            "bob@example.com",
            "alice@example.com",  # Duplicate
            "bob@example.com",    # Duplicate
            "charlie@example.com"
        ])

        assert len(errors) == 2
        duplicate_emails = {err.details["email"] for err in errors}
        assert duplicate_emails == {"alice@example.com", "bob@example.com"}

    def test_same_email_three_times(self):
        """Test email appearing three times (should report once)."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "alice@example.com",
            "alice@example.com",
            "alice@example.com"
        ])

        # Should report duplicate once
        assert len(errors) == 1
        assert errors[0].error_type == "duplicate"

    def test_invalid_email_and_duplicate(self):
        """Test group with both invalid format and duplicates."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "alice@example.com",
            "invalid-email",
            "alice@example.com",  # Duplicate
            "invalid-email"       # Both invalid and duplicate
        ])

        # Should have both error types
        error_types = {err.error_type for err in errors}
        assert "invalid_email" in error_types
        assert "duplicate" in error_types

    def test_empty_group(self):
        """Test validating an empty group."""
        validator = GroupValidator()
        errors = validator.validate_group("empty", [])
        assert errors == []


class TestValidateAllGroups:
    """Test validate_all_groups method."""

    def test_all_valid_groups(self):
        """Test multiple valid groups."""
        validator = GroupValidator()
        groups = {
            "team": ["alice@example.com", "bob@example.com"],
            "clients": ["client1@example.com", "client2@example.com"]
        }
        errors = validator.validate_all_groups(groups)
        assert errors == []

    def test_skips_metadata_keys(self):
        """Test that groups starting with _ are skipped."""
        validator = GroupValidator()
        groups = {
            "team": ["alice@example.com"],
            "_comment": ["This should be ignored"],
            "_metadata": ["invalid-email"]  # Would error if not skipped
        }
        errors = validator.validate_all_groups(groups)
        assert errors == []

    def test_validates_all_groups(self):
        """Test that all groups are validated."""
        validator = GroupValidator()
        groups = {
            "team1": ["invalid1"],
            "team2": ["invalid2"],
            "team3": ["valid@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        # Should have 2 errors (one for each invalid email)
        assert len(errors) == 2
        error_groups = {err.group_name for err in errors}
        assert error_groups == {"team1", "team2"}


class TestCircularReferences:
    """Test circular reference detection."""

    def test_simple_circular_reference(self):
        """Test simple A → B → A cycle."""
        validator = GroupValidator()
        groups = {
            "group1": ["#group2"],
            "group2": ["#group1"]
        }
        errors = validator.validate_all_groups(groups)

        assert len(errors) == 1
        assert errors[0].error_type == "circular_ref"
        assert "Circular reference detected" in errors[0].message
        # Cycle should be in details - includes the return path so it's 3 elements
        cycle = errors[0].details["cycle"]
        assert len(cycle) >= 2  # At least the two groups involved
        assert "group1" in cycle and "group2" in cycle

    def test_three_way_circular_reference(self):
        """Test A → B → C → A cycle."""
        validator = GroupValidator()
        groups = {
            "a": ["#b"],
            "b": ["#c"],
            "c": ["#a"]
        }
        errors = validator.validate_all_groups(groups)

        assert len(errors) == 1
        assert errors[0].error_type == "circular_ref"
        cycle = errors[0].details["cycle"]
        assert len(cycle) >= 3  # At least the three groups involved
        assert "a" in cycle and "b" in cycle and "c" in cycle

    def test_self_reference(self):
        """Test group referencing itself."""
        validator = GroupValidator()
        groups = {
            "group1": ["#group1"]
        }
        errors = validator.validate_all_groups(groups)

        assert len(errors) == 1
        assert errors[0].error_type == "circular_ref"

    def test_no_circular_reference_chain(self):
        """Test A → B → C (no cycle)."""
        validator = GroupValidator()
        groups = {
            "a": ["#b"],
            "b": ["#c"],
            "c": ["alice@example.com", "bob@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        # Should have no circular reference errors
        circular_errors = [e for e in errors if e.error_type == "circular_ref"]
        assert circular_errors == []

    def test_circular_reference_with_emails(self):
        """Test circular reference with mixed emails."""
        validator = GroupValidator()
        groups = {
            "group1": ["alice@example.com", "#group2"],
            "group2": ["bob@example.com", "#group1"]
        }
        errors = validator.validate_all_groups(groups)

        circular_errors = [e for e in errors if e.error_type == "circular_ref"]
        assert len(circular_errors) == 1

    def test_complex_circular_reference(self):
        """Test complex graph with cycle: A → B, A → C, B → D, D → A."""
        validator = GroupValidator()
        groups = {
            "a": ["#b", "#c"],
            "b": ["#d"],
            "c": ["charlie@example.com"],
            "d": ["#a"]  # Creates cycle: a → b → d → a
        }
        errors = validator.validate_all_groups(groups)

        circular_errors = [e for e in errors if e.error_type == "circular_ref"]
        assert len(circular_errors) == 1

    def test_multiple_independent_groups_no_cycle(self):
        """Test multiple independent group chains."""
        validator = GroupValidator()
        groups = {
            "team1": ["#team1-devs"],
            "team1-devs": ["alice@example.com"],
            "team2": ["#team2-devs"],
            "team2-devs": ["bob@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        circular_errors = [e for e in errors if e.error_type == "circular_ref"]
        assert circular_errors == []


class TestMissingGroupReferences:
    """Test detection of missing group references."""

    def test_reference_to_nonexistent_group(self):
        """Test group referencing non-existent group."""
        validator = GroupValidator()
        groups = {
            "team": ["#nonexistent"]
        }
        errors = validator.validate_all_groups(groups)

        missing_errors = [e for e in errors if e.error_type == "missing_group"]
        assert len(missing_errors) == 1
        assert missing_errors[0].group_name == "team"
        assert missing_errors[0].details["referenced_group"] == "nonexistent"

    def test_multiple_missing_references(self):
        """Test group with multiple missing references."""
        validator = GroupValidator()
        groups = {
            "team": ["#missing1", "#missing2"]
        }
        errors = validator.validate_all_groups(groups)

        missing_errors = [e for e in errors if e.error_type == "missing_group"]
        assert len(missing_errors) == 2
        referenced = {e.details["referenced_group"] for e in missing_errors}
        assert referenced == {"missing1", "missing2"}

    def test_valid_group_reference(self):
        """Test valid group references (no errors)."""
        validator = GroupValidator()
        groups = {
            "all": ["#team", "#clients"],
            "team": ["alice@example.com"],
            "clients": ["bob@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        missing_errors = [e for e in errors if e.error_type == "missing_group"]
        assert missing_errors == []

    def test_missing_reference_in_chain(self):
        """Test missing reference in a chain A → B → missing."""
        validator = GroupValidator()
        groups = {
            "a": ["#b"],
            "b": ["#missing"]
        }
        errors = validator.validate_all_groups(groups)

        missing_errors = [e for e in errors if e.error_type == "missing_group"]
        assert len(missing_errors) == 1
        assert missing_errors[0].group_name == "b"


class TestComplexValidationScenarios:
    """Test complex validation scenarios with multiple error types."""

    def test_all_error_types_together(self):
        """Test scenario with all error types."""
        validator = GroupValidator()
        groups = {
            "team1": [
                "alice@example.com",
                "invalid-email",      # Invalid format
                "alice@example.com",  # Duplicate
                "#team2"              # Circular reference
            ],
            "team2": [
                "#team1",             # Circular reference back
                "#missing"            # Missing group
            ]
        }
        errors = validator.validate_all_groups(groups)

        # Should have all error types
        error_types = {err.error_type for err in errors}
        assert "invalid_email" in error_types
        assert "duplicate" in error_types
        assert "circular_ref" in error_types
        assert "missing_group" in error_types

    def test_large_valid_group_structure(self):
        """Test large valid group structure."""
        validator = GroupValidator()
        groups = {
            "everyone": ["#engineering", "#sales", "#support"],
            "engineering": ["#backend", "#frontend"],
            "backend": ["alice@example.com", "bob@example.com"],
            "frontend": ["charlie@example.com", "diana@example.com"],
            "sales": ["eve@example.com"],
            "support": ["frank@example.com", "grace@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        assert errors == []

    def test_empty_groups_dict(self):
        """Test validating empty groups dictionary."""
        validator = GroupValidator()
        errors = validator.validate_all_groups({})
        assert errors == []

    def test_only_metadata_groups(self):
        """Test dict with only metadata groups."""
        validator = GroupValidator()
        groups = {
            "_comment": ["This is metadata"],
            "_version": ["1.0"]
        }
        errors = validator.validate_all_groups(groups)
        assert errors == []

    def test_group_with_only_valid_group_refs(self):
        """Test group containing only group references (all valid)."""
        validator = GroupValidator()
        groups = {
            "all": ["#team1", "#team2", "#team3"],
            "team1": ["alice@example.com"],
            "team2": ["bob@example.com"],
            "team3": ["charlie@example.com"]
        }
        errors = validator.validate_all_groups(groups)
        assert errors == []

    def test_deeply_nested_groups_no_cycle(self):
        """Test deeply nested group references without cycle."""
        validator = GroupValidator()
        groups = {
            "level1": ["#level2"],
            "level2": ["#level3"],
            "level3": ["#level4"],
            "level4": ["#level5"],
            "level5": ["alice@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        circular_errors = [e for e in errors if e.error_type == "circular_ref"]
        assert circular_errors == []

    def test_duplicate_group_references(self):
        """Test duplicate group references in a group."""
        validator = GroupValidator()
        groups = {
            "all": ["#team", "#team"],  # Duplicate group ref
            "team": ["alice@example.com"]
        }
        errors = validator.validate_all_groups(groups)

        # Duplicate group references should be caught
        duplicate_errors = [e for e in errors if e.error_type == "duplicate"]
        assert len(duplicate_errors) == 1
        assert duplicate_errors[0].details["email"] == "#team"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_email_with_hash_in_name_not_group_ref(self):
        """Test email containing # is not treated as group ref."""
        # Note: This would be invalid email anyway, but tests the logic
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "user#tag@example.com"  # Invalid email with #
        ])

        # Should be caught as invalid email, not as group reference
        assert len(errors) == 1
        assert errors[0].error_type == "invalid_email"

    def test_group_reference_case_sensitivity(self):
        """Test group references are case-sensitive."""
        validator = GroupValidator()
        groups = {
            "Team": ["alice@example.com"],
            "team": ["#Team"]  # Different case
        }
        errors = validator.validate_all_groups(groups)

        # Should find Team (case-sensitive match)
        missing_errors = [e for e in errors if e.error_type == "missing_group"]
        assert missing_errors == []

    def test_group_name_with_special_chars(self):
        """Test group names with hyphens and underscores."""
        validator = GroupValidator()
        groups = {
            "team-1": ["alice@example.com"],
            "team_2": ["bob@example.com"],
            "all": ["#team-1", "#team_2"]
        }
        errors = validator.validate_all_groups(groups)
        assert errors == []

    def test_very_long_email_list(self):
        """Test group with many emails."""
        validator = GroupValidator()
        emails = [f"user{i}@example.com" for i in range(100)]
        errors = validator.validate_group("large", emails)
        assert errors == []

    def test_unicode_in_email(self):
        """Test emails with unicode characters."""
        validator = GroupValidator()
        errors = validator.validate_group("team", [
            "test@例え.jp",  # Unicode domain
            "tëst@example.com"  # Unicode in local part
        ])

        # These should be valid in modern email standards
        # (depends on validate_email implementation)
        # At minimum, they shouldn't crash
        assert isinstance(errors, list)
