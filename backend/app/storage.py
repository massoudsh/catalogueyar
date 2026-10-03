import json
import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import DATABASE_PATH
from app.schemas.catalog import CatalogDraft, CatalogGenerateResponse, CatalogUpdate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE IF NOT EXISTS drafts (id TEXT PRIMARY KEY, seller_id TEXT NOT NULL, catalog TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
    connection.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, draft_id TEXT NOT NULL, seller_id TEXT NOT NULL, changes TEXT NOT NULL, created_at TEXT NOT NULL)")
    connection.commit()
    return connection


def create_draft(seller_id: str, catalog: CatalogGenerateResponse) -> CatalogDraft:
    draft_id = str(uuid.uuid4())
    timestamp = _now()
    with _connect() as connection:
        connection.execute("INSERT INTO drafts VALUES (?, ?, ?, ?, ?)", (draft_id, seller_id, catalog.model_dump_json(), timestamp, timestamp))
    return CatalogDraft(id=draft_id, seller_id=seller_id, created_at=timestamp, updated_at=timestamp, catalog=catalog)


def _row_to_draft(row: sqlite3.Row) -> CatalogDraft:
    return CatalogDraft(id=row["id"], seller_id=row["seller_id"], created_at=row["created_at"], updated_at=row["updated_at"], catalog=CatalogGenerateResponse.model_validate_json(row["catalog"]))


def get_draft(seller_id: str, draft_id: str) -> CatalogDraft | None:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM drafts WHERE id = ? AND seller_id = ?", (draft_id, seller_id)).fetchone()
    return _row_to_draft(row) if row else None


def list_drafts(seller_id: str, limit: int = 20) -> list[CatalogDraft]:
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM drafts WHERE seller_id = ? ORDER BY created_at DESC LIMIT ?", (seller_id, limit)).fetchall()
    return [_row_to_draft(row) for row in rows]


def update_draft(seller_id: str, draft_id: str, update: CatalogUpdate) -> CatalogDraft | None:
    current = get_draft(seller_id, draft_id)
    if current is None:
        return None
    changes = update.model_dump(exclude_none=True)
    catalog = current.catalog.model_copy(update=changes)
    timestamp = _now()
    with _connect() as connection:
        connection.execute("UPDATE drafts SET catalog = ?, updated_at = ? WHERE id = ? AND seller_id = ?", (catalog.model_dump_json(), timestamp, draft_id, seller_id))
        connection.execute("INSERT INTO feedback (draft_id, seller_id, changes, created_at) VALUES (?, ?, ?, ?)", (draft_id, seller_id, json.dumps(changes, ensure_ascii=False), timestamp))
    return CatalogDraft(id=current.id, seller_id=current.seller_id, created_at=current.created_at, updated_at=timestamp, catalog=catalog)


def seller_context(seller_id: str, limit: int = 5) -> list[CatalogGenerateResponse]:
    return [draft.catalog for draft in list_drafts(seller_id, limit)]
