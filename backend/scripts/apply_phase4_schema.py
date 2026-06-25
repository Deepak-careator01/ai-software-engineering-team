"""Apply Phase 4 workflow persistence schema to Supabase (DDL only)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote_plus

import httpx
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_DIR = _REPO_ROOT / "backend"

load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_REPO_ROOT / ".env")

MIGRATION_FILE = (
    Path(__file__).resolve().parents[2]
    / "supabase"
    / "migrations"
    / "20250624120000_phase4_workflow_schema.sql"
)

WORKFLOW_RUNS_COLUMNS = {
    "id": "uuid",
    "goal": "text",
    "status": "text",
    "final_output": "jsonb",
    "created_at": "timestamp without time zone",
}

AGENT_RUNS_COLUMNS = {
    "id": "uuid",
    "workflow_id": "uuid",
    "agent_name": "text",
    "input": "jsonb",
    "output": "jsonb",
    "created_at": "timestamp without time zone",
}


def _project_ref() -> str:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not url:
        raise SystemExit("SUPABASE_URL is not set in environment.")
    return url.replace("https://", "").split(".")[0]


def _management_token() -> str | None:
    return os.getenv("SUPABASE_ACCESS_TOKEN")


def _apply_via_management_api(sql: str) -> None:
    token = _management_token()
    if not token:
        raise RuntimeError("SUPABASE_ACCESS_TOKEN is not set.")

    ref = _project_ref()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": sql,
        "name": "phase4_workflow_schema",
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"https://api.supabase.com/v1/projects/{ref}/database/migrations",
            headers=headers,
            json=payload,
        )
        if response.status_code >= 400:
            response = client.post(
                f"https://api.supabase.com/v1/projects/{ref}/database/query",
                headers=headers,
                json={"query": sql},
            )
        if response.status_code >= 400:
            raise SystemExit(
                "Management API schema apply failed "
                f"({response.status_code}): {response.text}"
            )


def _database_url() -> str:
    explicit = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if explicit:
        return explicit

    password = os.getenv("SUPABASE_DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "Set DATABASE_URL, SUPABASE_DB_URL, or SUPABASE_DB_PASSWORD."
        )

    ref = _project_ref()
    user = quote_plus(f"postgres.{ref}")
    encoded_password = quote_plus(password)
    pooler_host = "aws-0-ap-south-1.pooler.supabase.com"
    last_error: Exception | None = None
    for port in (5432, 6543):
        url = (
            f"postgresql://{user}:{encoded_password}@{pooler_host}:{port}/postgres"
            "?sslmode=require"
        )
        try:
            import psycopg2

            conn = psycopg2.connect(url, connect_timeout=20)
            conn.close()
            return url
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Could not connect to Supabase Postgres: {last_error}")


def _normalize_type(data_type: str, udt_name: str) -> str:
    if data_type == "USER-DEFINED" and udt_name == "uuid":
        return "uuid"
    if data_type == "jsonb":
        return "jsonb"
    if data_type == "text":
        return "text"
    if data_type.startswith("timestamp"):
        return "timestamp without time zone"
    return data_type


def _rows_from_management_response(response: httpx.Response) -> list[dict]:
    try:
        payload = response.json()
    except json.JSONDecodeError:
        return []

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("result", "rows", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def _fetch_columns_management(table_name: str) -> dict[str, str]:
    token = _management_token()
    if not token:
        raise RuntimeError("SUPABASE_ACCESS_TOKEN is not set.")

    ref = _project_ref()
    query = """
        select column_name, data_type, udt_name
        from information_schema.columns
        where table_schema = 'public' and table_name = %s
        order by ordinal_position
    """
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"https://api.supabase.com/v1/projects/{ref}/database/query/read-only",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"query": query.replace("%s", f"'{table_name}'")},
        )
    if response.status_code >= 400:
        raise SystemExit(
            "Management API validation failed "
            f"({response.status_code}): {response.text}"
        )

    columns: dict[str, str] = {}
    for row in _rows_from_management_response(response):
        name = row.get("column_name")
        if not name:
            continue
        columns[str(name)] = _normalize_type(
            str(row.get("data_type", "")),
            str(row.get("udt_name", "")),
        )
    return columns


def _fetch_columns_postgres(cur, table_name: str) -> dict[str, str]:
    cur.execute(
        """
        select column_name, data_type, udt_name
        from information_schema.columns
        where table_schema = 'public' and table_name = %s
        order by ordinal_position
        """,
        (table_name,),
    )
    return {
        row[0]: _normalize_type(row[1], row[2])
        for row in cur.fetchall()
    }


def _validate_columns(workflow_cols: dict[str, str], agent_cols: dict[str, str]) -> None:
    for name, expected in WORKFLOW_RUNS_COLUMNS.items():
        actual = workflow_cols.get(name)
        if actual != expected:
            raise SystemExit(
                f"Validation failed: workflow_runs.{name} is {actual!r}, "
                f"expected {expected!r}."
            )

    for name, expected in AGENT_RUNS_COLUMNS.items():
        actual = agent_cols.get(name)
        if actual != expected:
            raise SystemExit(
                f"Validation failed: agent_runs.{name} is {actual!r}, "
                f"expected {expected!r}."
            )


def _validate_schema_postgres(cur) -> None:
    for table_name in ("workflow_runs", "agent_runs"):
        cur.execute(
            """
            select 1
            from information_schema.tables
            where table_schema = 'public' and table_name = %s
            """,
            (table_name,),
        )
        if cur.fetchone() is None:
            raise SystemExit(f"Validation failed: {table_name} table does not exist.")

    workflow_cols = _fetch_columns_postgres(cur, "workflow_runs")
    agent_cols = _fetch_columns_postgres(cur, "agent_runs")
    _validate_columns(workflow_cols, agent_cols)

    cur.execute(
        """
        select 1
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu
          on tc.constraint_name = kcu.constraint_name
         and tc.table_schema = kcu.table_schema
        join information_schema.constraint_column_usage ccu
          on ccu.constraint_name = tc.constraint_name
         and ccu.table_schema = tc.table_schema
        where tc.constraint_type = 'FOREIGN KEY'
          and tc.table_schema = 'public'
          and tc.table_name = 'agent_runs'
          and kcu.column_name = 'workflow_id'
          and ccu.table_name = 'workflow_runs'
          and ccu.column_name = 'id'
        """
    )
    if cur.fetchone() is None:
        raise SystemExit(
            "Validation failed: foreign key agent_runs.workflow_id → "
            "workflow_runs.id not found."
        )


def _validate_schema_management() -> None:
    workflow_cols = _fetch_columns_management("workflow_runs")
    agent_cols = _fetch_columns_management("agent_runs")
    if not workflow_cols:
        raise SystemExit("Validation failed: workflow_runs table does not exist.")
    if not agent_cols:
        raise SystemExit("Validation failed: agent_runs table does not exist.")
    _validate_columns(workflow_cols, agent_cols)

    token = _management_token()
    ref = _project_ref()
    fk_query = """
        select 1
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu
          on tc.constraint_name = kcu.constraint_name
         and tc.table_schema = kcu.table_schema
        join information_schema.constraint_column_usage ccu
          on ccu.constraint_name = tc.constraint_name
         and ccu.table_schema = tc.table_schema
        where tc.constraint_type = 'FOREIGN KEY'
          and tc.table_schema = 'public'
          and tc.table_name = 'agent_runs'
          and kcu.column_name = 'workflow_id'
          and ccu.table_name = 'workflow_runs'
          and ccu.column_name = 'id'
    """
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"https://api.supabase.com/v1/projects/{ref}/database/query/read-only",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"query": fk_query},
        )
    if response.status_code >= 400 or not _rows_from_management_response(response):
        raise SystemExit(
            "Validation failed: foreign key agent_runs.workflow_id → "
            "workflow_runs.id not found."
        )


def _apply_via_postgres(sql: str) -> None:
    db_url = _database_url()
    try:
        import psycopg2
    except ImportError as exc:
        raise SystemExit(
            "psycopg2 is required. Install with: pip install psycopg2-binary"
        ) from exc

    with psycopg2.connect(db_url) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
            _validate_schema_postgres(cur)


def main() -> None:
    if not MIGRATION_FILE.is_file():
        raise SystemExit(f"Migration file not found: {MIGRATION_FILE}")

    sql = MIGRATION_FILE.read_text(encoding="utf-8")

    if _management_token():
        _apply_via_management_api(sql)
        _validate_schema_management()
    else:
        try:
            _apply_via_postgres(sql)
        except RuntimeError as exc:
            message = str(exc)
            if "Could not connect" in message:
                raise SystemExit(
                    f"{message}\n\n"
                    "Postgres ports may be blocked from this terminal. Run the script "
                    "from your local PowerShell, or paste the SQL from "
                    "supabase/migrations/20250624120000_phase4_workflow_schema.sql "
                    "into the Supabase SQL Editor."
                ) from exc
            raise SystemExit(
                f"{message}\n\n"
                "Add one of the following to your root .env, then re-run:\n"
                "  SUPABASE_ACCESS_TOKEN=<from Supabase Dashboard → Account → Tokens>\n"
                "  SUPABASE_DB_PASSWORD=<from Supabase Dashboard → Project Settings → Database>"
            ) from exc

    print("Phase 4 schema created successfully")


if __name__ == "__main__":
    main()
