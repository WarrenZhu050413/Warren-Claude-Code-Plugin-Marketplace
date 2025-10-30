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


class TestEmailBodyParserHTML:
    """Test suite for HTML email parsing."""

    def test_extract_new_content_from_gmail_html_reply(self):
        """Should extract only new content from Gmail HTML reply, removing blockquotes.

        Test data taken from real Gmail reply email (message_id: 19a2e13c601f2565).
        """
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        # Real Gmail HTML reply with blockquote
        body = (
            '<div dir="auto">Look at other language research or things like that.\xa0</div>'
            '<div><br><div class="gmail_quote gmail_quote_container">'
            '<div dir="ltr" class="gmail_attr">El El mar, 28 oct 2025 a la(s) 23:47, Warren Zhu &lt;'
            '<a href="mailto:wzhu@college.harvard.edu">wzhu@college.harvard.edu</a>&gt; escribió:<br></div>'
            '<blockquote class="gmail_quote" style="margin:0px 0px 0px 0.8ex;border-left-width:1px;'
            'border-left-style:solid;padding-left:1ex;border-left-color:rgb(204,204,204)">'
            'searching about how long it takes to learn different languages fully as a fluent english '
            'and mandarin speaker\xa0\r\n</blockquote></div></div>\r\n'
        )

        parser = EmailBodyParser()
        result = parser.extract_new_content_html(body)

        # Should extract only the new content
        assert 'Look at other language research or things like that' in result
        # Should not include the attribution
        assert 'El El mar' not in result
        assert 'escribió' not in result
        # Should not include quoted content
        assert 'searching about how long' not in result


    def test_extract_html_handles_empty_body(self):
        """Should return empty string when HTML body is empty."""
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        parser = EmailBodyParser()
        result = parser.extract_new_content_html('')

        assert result == ''


    def test_extract_html_handles_no_quotes(self):
        """Should return full text when there are no blockquotes."""
        from gmaillm.helpers.domain.email_parser import EmailBodyParser

        body = '<div>This is an original message with no quotes.</div>'

        parser = EmailBodyParser()
        result = parser.extract_new_content_html(body)

        assert 'This is an original message with no quotes' in result
