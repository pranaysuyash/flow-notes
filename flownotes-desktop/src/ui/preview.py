"""
Markdown Preview component for FlowNotes Desktop
Renders markdown with Mermaid diagram support
"""

try:
    from PySide6.QtWidgets import QTextBrowser
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtGui import QFont
except ImportError:
    print("PySide6 not installed")
    raise


class MarkdownPreview(QTextBrowser):
    """Markdown preview pane"""

    def __init__(self):
        super().__init__()

        self.setup_preview()

    def setup_preview(self):
        """Setup preview properties"""
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)

        # Font
        font = QFont("Georgia", 13)
        self.setFont(font)

        # Initial content
        self.setHtml(self.get_welcome_html())

    def update_preview(self, markdown_content: str):
        """
        Update preview with markdown content

        Args:
            markdown_content: Markdown text to render
        """
        if not markdown_content.strip():
            self.setHtml(self.get_welcome_html())
            return

        # Convert markdown to HTML
        html = self.markdown_to_html(markdown_content)
        self.setHtml(html)

    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert markdown to HTML

        Args:
            markdown_text: Markdown content

        Returns:
            HTML string
        """
        try:
            import markdown2
            html_content = markdown2.markdown(
                markdown_text,
                extras=["fenced-code-blocks", "tables", "header-ids"]
            )
        except ImportError:
            # Fallback to basic conversion if markdown2 not available
            html_content = markdown_text.replace('\n', '<br>')

        # Wrap in styled HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Georgia, serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #E0E0E6;
                    background-color: #262637;
                    padding: 20px;
                }}

                h1, h2, h3, h4, h5, h6 {{
                    color: #7C3AED;
                    margin-top: 24px;
                    margin-bottom: 12px;
                }}

                h1 {{ font-size: 28px; border-bottom: 2px solid #7C3AED; padding-bottom: 8px; }}
                h2 {{ font-size: 24px; }}
                h3 {{ font-size: 20px; }}

                p {{
                    margin: 12px 0;
                }}

                code {{
                    background-color: #1E1E2E;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'JetBrains Mono', 'Courier New', monospace;
                    font-size: 13px;
                    color: #EC4899;
                }}

                pre {{
                    background-color: #1E1E2E;
                    padding: 16px;
                    border-radius: 8px;
                    overflow-x: auto;
                    border-left: 4px solid #7C3AED;
                }}

                pre code {{
                    background-color: transparent;
                    padding: 0;
                    color: #10B981;
                }}

                blockquote {{
                    border-left: 4px solid #EC4899;
                    padding-left: 16px;
                    margin-left: 0;
                    font-style: italic;
                    color: #A0A0AB;
                }}

                a {{
                    color: #3B82F6;
                    text-decoration: none;
                }}

                a:hover {{
                    text-decoration: underline;
                }}

                ul, ol {{
                    margin: 12px 0;
                    padding-left: 24px;
                }}

                li {{
                    margin: 4px 0;
                }}

                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}

                th, td {{
                    border: 1px solid #3A3A4F;
                    padding: 12px;
                    text-align: left;
                }}

                th {{
                    background-color: #7C3AED;
                    color: white;
                    font-weight: bold;
                }}

                tr:nth-child(even) {{
                    background-color: #2D2D3F;
                }}

                hr {{
                    border: none;
                    border-top: 2px solid #3A3A4F;
                    margin: 24px 0;
                }}

                strong {{
                    color: #FFFFFF;
                    font-weight: bold;
                }}

                em {{
                    color: #D0D0D6;
                    font-style: italic;
                }}

                /* Mermaid diagrams (if rendered) */
                .mermaid {{
                    background-color: #1E1E2E;
                    padding: 16px;
                    border-radius: 8px;
                    margin: 16px 0;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

    def get_welcome_html(self) -> str:
        """Get welcome message HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Georgia, serif;
                    color: #A0A0AB;
                    background-color: #262637;
                    padding: 40px;
                    text-align: center;
                }
                h1 {
                    color: #7C3AED;
                    font-size: 32px;
                    margin-bottom: 16px;
                }
                p {
                    font-size: 16px;
                    line-height: 1.6;
                }
            </style>
        </head>
        <body>
            <h1>📝 FlowNotes</h1>
            <p>AI-Powered Learning Companion</p>
            <p style="margin-top: 40px; color: #70707A;">
                Start typing in the editor to see your notes<br>
                beautifully rendered here in real-time.
            </p>
        </body>
        </html>
        """
