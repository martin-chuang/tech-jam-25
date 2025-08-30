"""Main Flask application entry point with proper DI structure."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.common.app_factory import create_app


def create_application():
    """Create the Flask application instance using app factory."""
    return create_app()


if __name__ == "__main__":
    app = create_application()
    app.run(host="0.0.0.0", port=5000, debug=True)
