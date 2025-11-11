from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    MetaData,
    String,
    Table,
    Text,
    text,
)

metadata = MetaData()

todos = Table(
    "todos",
    metadata,
    Column("id", String, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("description", String(2000)),
    Column("completed", Boolean, nullable=False, default=False),
    Column("due_date", Date),
    Column("priority", String(10), nullable=False, server_default=text("'medium'")),
    Column("category", String(50)),
    Column("tags", Text),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
)

Index("idx_todos_created_at_desc", todos.c.created_at.desc())
