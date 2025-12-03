"""Group validation utilities for gmaillm."""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional

from gmaillm.validators.email import validate_email


@dataclass
class GroupValidationError:
    """Represents a group validation error."""
    group_name: str
    error_type: str  # 'invalid_email', 'duplicate', 'circular_ref', 'missing_group'
    message: str
    details: Optional[Dict] = None

    def __str__(self) -> str:
        """Format error message."""
        return f"[{self.group_name}] {self.error_type}: {self.message}"


class GroupValidator:
    """Validator for email distribution groups with circular reference detection."""

    def validate_group(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Validate a single group.

        Args:
            name: Group name
            emails: List of email addresses

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # 1. Check email formats
        errors.extend(self._validate_email_formats(name, emails))

        # 2. Check for duplicates
        errors.extend(self._validate_duplicates(name, emails))

        return errors

    def validate_all_groups(self, groups: Dict[str, List[str]]) -> List[GroupValidationError]:
        """Validate all groups and check for circular references.

        Args:
            groups: Dictionary mapping group names to email lists

        Returns:
            List of validation errors (empty if all groups valid)
        """
        errors = []

        # Validate each group
        for name, emails in groups.items():
            if name.startswith("_"):
                continue  # Skip metadata keys
            errors.extend(self.validate_group(name, emails))

        # Check for circular references (#group1 → #group2 → #group1)
        errors.extend(self._check_circular_references(groups))

        # Check for references to non-existent groups
        errors.extend(self._check_missing_group_refs(groups))

        return errors

    def _validate_email_formats(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Check all emails are valid format.

        Args:
            name: Group name
            emails: List of email addresses

        Returns:
            List of validation errors for invalid emails
        """
        errors = []

        for email in emails:
            # Skip group references
            if email.startswith("#"):
                continue

            if not validate_email(email):
                errors.append(GroupValidationError(
                    group_name=name,
                    error_type="invalid_email",
                    message=f"Invalid email address: {email}",
                    details={"email": email}
                ))

        return errors

    def _validate_duplicates(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Check for duplicate emails in a group.

        Args:
            name: Group name
            emails: List of email addresses

        Returns:
            List of validation errors for duplicates
        """
        errors = []
        seen = set()
        duplicates = set()

        for email in emails:
            if email in seen:
                duplicates.add(email)
            seen.add(email)

        for dup in duplicates:
            errors.append(GroupValidationError(
                group_name=name,
                error_type="duplicate",
                message=f"Duplicate email: {dup}",
                details={"email": dup}
            ))

        return errors

    def _check_circular_references(self, groups: Dict[str, List[str]]) -> List[GroupValidationError]:
        """Detect circular group references using DFS.

        Examples of circular references:
        - #group1 contains #group2, #group2 contains #group1
        - #a → #b → #c → #a

        Args:
            groups: Dictionary mapping group names to email lists

        Returns:
            List of validation errors for circular references
        """
        errors = []

        def has_cycle(group_name: str, visited: Set[str], rec_stack: Set[str]) -> Optional[List[str]]:
            """DFS to detect cycles. Returns cycle path if found."""
            visited.add(group_name)
            rec_stack.add(group_name)

            # Get emails for this group
            if group_name not in groups:
                return None

            # Check all group references in this group
            for email in groups[group_name]:
                if email.startswith("#"):
                    ref_group = email[1:]  # Remove # prefix

                    if ref_group not in visited:
                        cycle = has_cycle(ref_group, visited, rec_stack)
                        if cycle:
                            return [group_name] + cycle
                    elif ref_group in rec_stack:
                        # Found cycle
                        return [group_name, ref_group]

            rec_stack.remove(group_name)
            return None

        visited = set()

        for group_name in groups.keys():
            if group_name.startswith("_"):
                continue

            if group_name not in visited:
                cycle = has_cycle(group_name, visited, set())
                if cycle:
                    cycle_str = " → ".join(f"#{g}" for g in cycle)
                    errors.append(GroupValidationError(
                        group_name=cycle[0],
                        error_type="circular_ref",
                        message=f"Circular reference detected: {cycle_str}",
                        details={"cycle": cycle}
                    ))

        return errors

    def _check_missing_group_refs(self, groups: Dict[str, List[str]]) -> List[GroupValidationError]:
        """Check for references to non-existent groups.

        Args:
            groups: Dictionary mapping group names to email lists

        Returns:
            List of validation errors for missing group references
        """
        errors = []

        for group_name, emails in groups.items():
            if group_name.startswith("_"):
                continue

            for email in emails:
                if email.startswith("#"):
                    ref_group = email[1:]  # Remove # prefix

                    if ref_group not in groups:
                        errors.append(GroupValidationError(
                            group_name=group_name,
                            error_type="missing_group",
                            message=f"References non-existent group: #{ref_group}",
                            details={"referenced_group": ref_group}
                        ))

        return errors
