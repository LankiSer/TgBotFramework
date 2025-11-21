"""
CLI для управления проектами
"""

from .commands import create_project, init_database, run_migrations

__all__ = [
    "create_project",
    "init_database",
    "run_migrations",
]

