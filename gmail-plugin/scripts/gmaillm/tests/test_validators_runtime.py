"""Tests for runtime type validation decorators.

This module tests the @validate_types and @validate_pydantic decorators
that provide runtime type checking to catch type mismatches early.
"""

import pytest
from typing import List
from pydantic import BaseModel

from gmaillm.validators.runtime import validate_types, validate_pydantic


# Test models
class Person(BaseModel):
    name: str
    age: int


class Employee(BaseModel):
    name: str
    employee_id: str


# ============ @validate_types Tests ============

class TestValidateTypesDecorator:
    """Test the @validate_types decorator for general type validation."""

    def test_validate_basic_types(self):
        """Test validation with basic Python types."""
        @validate_types
        def process(name: str, age: int, active: bool) -> str:
            return f"{name}, {age}, {active}"

        # Valid call
        result = process("Alice", 30, True)
        assert result == "Alice, 30, True"

    def test_validate_basic_types_fails(self):
        """Test validation catches basic type mismatches."""
        @validate_types
        def process(name: str, age: int) -> str:
            return f"{name}, {age}"

        # Invalid: passing str where int expected
        with pytest.raises(TypeError) as exc:
            process("Alice", "thirty")

        assert "expected <class 'int'>" in str(exc.value)
        assert "got str" in str(exc.value)

    def test_validate_list_types(self):
        """Test validation with List type hints."""
        @validate_types
        def process_names(names: List[str]) -> int:
            return len(names)

        # Valid call
        result = process_names(["Alice", "Bob", "Charlie"])
        assert result == 3

    def test_validate_list_types_fails_non_list(self):
        """Test validation catches non-list where List expected."""
        @validate_types
        def process_names(names: List[str]) -> int:
            return len(names)

        # Invalid: passing str where List[str] expected
        with pytest.raises(TypeError) as exc:
            process_names("not a list")

        assert "expected" in str(exc.value).lower()

    def test_validate_list_element_types(self):
        """Test validation checks list element types."""
        @validate_types
        def sum_numbers(numbers: List[int]) -> int:
            return sum(numbers)

        # Valid call
        result = sum_numbers([1, 2, 3, 4])
        assert result == 10

        # Invalid: list contains wrong element types
        with pytest.raises(TypeError):
            sum_numbers([1, "two", 3])

    def test_validate_pydantic_models(self):
        """Test validation with Pydantic models."""
        @validate_types
        def greet_person(person: Person) -> str:
            return f"Hello, {person.name}!"

        # Valid call
        person = Person(name="Alice", age=30)
        result = greet_person(person)
        assert result == "Hello, Alice!"

    def test_validate_pydantic_models_fails(self):
        """Test validation catches wrong Pydantic model type."""
        @validate_types
        def greet_person(person: Person) -> str:
            return f"Hello, {person.name}!"

        # Invalid: passing Employee where Person expected
        employee = Employee(name="Bob", employee_id="E123")
        with pytest.raises(TypeError) as exc:
            greet_person(employee)

        assert "expected" in str(exc.value).lower()

    def test_validate_optional_types(self):
        """Test validation handles Optional types (None allowed)."""
        from typing import Optional

        @validate_types
        def process(value: Optional[str]) -> str:
            return value if value else "default"

        # Valid: passing None
        result = process(None)
        assert result == "default"

        # Valid: passing str
        result = process("hello")
        assert result == "hello"

    def test_validate_skips_self(self):
        """Test validation skips 'self' parameter in methods."""
        class Calculator:
            @validate_types
            def add(self, a: int, b: int) -> int:
                return a + b

        calc = Calculator()
        result = calc.add(5, 3)
        assert result == 8


# ============ @validate_pydantic Tests ============

class TestValidatePydanticDecorator:
    """Test the @validate_pydantic decorator for Pydantic model validation."""

    def test_validate_correct_model(self):
        """Test validation passes with correct Pydantic model."""
        @validate_pydantic(Person)
        def process_person(person):
            return f"{person.name} is {person.age} years old"

        person = Person(name="Alice", age=30)
        result = process_person(person)
        assert result == "Alice is 30 years old"

    def test_validate_wrong_model_type(self):
        """Test validation catches wrong Pydantic model type."""
        @validate_pydantic(Person)
        def process_person(person):
            return f"{person.name} is {person.age} years old"

        # Invalid: passing Employee where Person expected
        employee = Employee(name="Bob", employee_id="E123")
        with pytest.raises(TypeError) as exc:
            process_person(employee)

        assert "expected Person" in str(exc.value)
        assert "got Employee" in str(exc.value)

    def test_validate_non_model_type(self):
        """Test validation catches non-Pydantic types."""
        @validate_pydantic(Person)
        def process_person(person):
            return f"{person.name} is {person.age} years old"

        # Invalid: passing dict where Person expected
        with pytest.raises(TypeError) as exc:
            process_person({"name": "Charlie", "age": 25})

        assert "expected Person" in str(exc.value)
        assert "got dict" in str(exc.value)

    def test_validate_method_with_self(self):
        """Test validation works correctly with class methods."""
        class PersonProcessor:
            @validate_pydantic(Person)
            def process(self, person):
                return f"Processing {person.name}"

        processor = PersonProcessor()
        person = Person(name="Alice", age=30)
        result = processor.process(person)
        assert result == "Processing Alice"

    def test_validate_method_fails_with_wrong_model(self):
        """Test validation catches wrong model in class methods."""
        class PersonProcessor:
            @validate_pydantic(Person)
            def process(self, person):
                return f"Processing {person.name}"

        processor = PersonProcessor()
        employee = Employee(name="Bob", employee_id="E123")

        with pytest.raises(TypeError) as exc:
            processor.process(employee)

        assert "expected Person" in str(exc.value)


# ============ Integration Tests ============

class TestRuntimeValidationIntegration:
    """Test runtime validation in realistic scenarios."""

    def test_formatter_type_validation(self):
        """Test type validation prevents EmailSummary/EmailFull confusion."""
        from gmaillm.models import EmailFull, EmailSummary, EmailAddress
        from gmaillm.formatters import RichFormatter
        from rich.console import Console
        from datetime import datetime, timezone

        console = Console()
        formatter = RichFormatter(console)

        # Create EmailFull object
        email_full = EmailFull(
            message_id="123",
            thread_id="456",
            subject="Test",
            from_=EmailAddress(name="Alice", email="alice@example.com"),
            to=[EmailAddress(email="bob@example.com")],
            date=datetime.now(timezone.utc),
            labels=["INBOX"],
            snippet="Test snippet",
            body_plain="Test body"
        )

        # Valid: print_email_full accepts EmailFull
        formatter.print_email_full(email_full)  # Should work

        # Create EmailSummary object
        email_summary = EmailSummary(
            message_id="789",
            thread_id="012",
            subject="Summary Test",
            from_=EmailAddress(email="alice@example.com"),
            date=datetime.now(timezone.utc),
            snippet="Summary snippet",
            is_unread=False,
            has_attachments=False
        )

        # Invalid: print_email_full should reject EmailSummary
        with pytest.raises(TypeError) as exc:
            formatter.print_email_full(email_summary)

        assert "expected EmailFull" in str(exc.value)
        assert "got EmailSummary" in str(exc.value)

    def test_list_validation_catches_mixed_types(self):
        """Test list validation catches mixed element types."""
        from gmaillm.models import EmailSummary, EmailAddress
        from gmaillm.formatters import RichFormatter
        from rich.console import Console
        from datetime import datetime, timezone

        console = Console()
        formatter = RichFormatter(console)

        # Create valid EmailSummary objects
        email1 = EmailSummary(
            message_id="1",
            thread_id="t1",
            subject="Test 1",
            from_=EmailAddress(email="alice@example.com"),
            date=datetime.now(timezone.utc),
            snippet="Snippet 1",
            is_unread=False,
            has_attachments=False
        )

        email2 = EmailSummary(
            message_id="2",
            thread_id="t2",
            subject="Test 2",
            from_=EmailAddress(email="bob@example.com"),
            date=datetime.now(timezone.utc),
            snippet="Snippet 2",
            is_unread=False,
            has_attachments=False
        )

        # Valid: list of EmailSummary objects
        formatter.print_email_list([email1, email2], folder="INBOX")  # Should work

        # Invalid: mixed list with wrong type
        with pytest.raises(TypeError):
            formatter.print_email_list([email1, "not an email", email2])
