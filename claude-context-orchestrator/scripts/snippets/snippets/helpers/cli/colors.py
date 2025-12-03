"""ANSI color codes for terminal output."""


class Colors:
    """ANSI color utility class for terminal formatting."""

    # Color codes
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Style codes
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Reset
    RESET = "\033[0m"

    @classmethod
    def red(cls, text: str) -> str:
        """Color text red."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def green(cls, text: str) -> str:
        """Color text green."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def yellow(cls, text: str) -> str:
        """Color text yellow."""
        return f"{cls.YELLOW}{text}{cls.RESET}"

    @classmethod
    def blue(cls, text: str) -> str:
        """Color text blue."""
        return f"{cls.BLUE}{text}{cls.RESET}"

    @classmethod
    def magenta(cls, text: str) -> str:
        """Color text magenta."""
        return f"{cls.MAGENTA}{text}{cls.RESET}"

    @classmethod
    def cyan(cls, text: str) -> str:
        """Color text cyan."""
        return f"{cls.CYAN}{text}{cls.RESET}"

    @classmethod
    def white(cls, text: str) -> str:
        """Color text white."""
        return f"{cls.WHITE}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Make text bold."""
        return f"{cls.BOLD}{text}{cls.RESET}"

    @classmethod
    def dim(cls, text: str) -> str:
        """Make text dim."""
        return f"{cls.DIM}{text}{cls.RESET}"

    @classmethod
    def underline(cls, text: str) -> str:
        """Underline text."""
        return f"{cls.UNDERLINE}{text}{cls.RESET}"

    @classmethod
    def success(cls, text: str) -> str:
        """Format success message (green with checkmark)."""
        return f"{cls.GREEN}✓{cls.RESET} {text}"

    @classmethod
    def error(cls, text: str) -> str:
        """Format error message (red with X)."""
        return f"{cls.RED}✗{cls.RESET} {text}"

    @classmethod
    def warning(cls, text: str) -> str:
        """Format warning message (yellow with warning sign)."""
        return f"{cls.YELLOW}⚠{cls.RESET} {text}"

    @classmethod
    def info(cls, text: str) -> str:
        """Format info message (cyan with info sign)."""
        return f"{cls.CYAN}ℹ{cls.RESET} {text}"

    @classmethod
    def highlight(cls, text: str) -> str:
        """Highlight text (cyan and bold)."""
        return f"{cls.CYAN}{cls.BOLD}{text}{cls.RESET}"
