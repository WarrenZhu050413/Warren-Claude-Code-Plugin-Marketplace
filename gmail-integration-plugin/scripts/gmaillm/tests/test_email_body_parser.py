"""Tests for email body parsing and quote stripping.

Tests use real email data from Gmail to ensure accurate parsing.
"""



class TestEmailBodyParser:
    """Test suite for EmailBodyParser class."""

    def test_extract_new_content_from_gmail_plain_text_reply(self):
        """Should extract only new content from Gmail plain text reply, removing quoted text.

        Test data taken from real Gmail reply email (message_id: 19a2e13c601f2565).
        """
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        # Real Gmail reply body with Spanish attribution line
        body = (
            'Look at other language research or things like that.\r\n\r\n'
            'El El mar, 28 oct 2025 a la(s) 23:47, Warren Zhu <wzhu@college.harvard.edu>\r\n'
            'escribió:\r\n\r\n'
            '> searching about how long it takes to learn different languages fully as a\r\n'
            '> fluent english and mandarin speaker\r\n'
        )

        parser = EmailBodyParser()
        result = parser.extract_new_content_plain(body)

        # Should extract only the new content
        assert result == 'Look at other language research or things like that.'
        # Should not include the attribution line
        assert 'El El mar' not in result
        # Should not include quoted content
        assert 'searching about how long' not in result


    def test_extract_new_content_handles_empty_body(self):
        """Should return empty string when body is empty."""
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        parser = EmailBodyParser()
        result = parser.extract_new_content_plain('')

        assert result == ''


    def test_extract_new_content_handles_no_quotes(self):
        """Should return full body when there are no quotes."""
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        body = 'This is an original message with no quotes.'

        parser = EmailBodyParser()
        result = parser.extract_new_content_plain(body)

        assert result == 'This is an original message with no quotes.'
