import os

import app.core.config  # noqa: F401 — load .env before reading Supabase variables

from supabase import Client, create_client


class SupabaseClient:
    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Client | None = None

        if not self.url:
            print("WARNING: SUPABASE_URL is not set")
        if not self.key:
            print("WARNING: SUPABASE_SERVICE_ROLE_KEY is not set")

        if self.url and self.key:
            self.client = create_client(self.url, self.key)

    def get_client(self) -> Client | None:
        return self.client


supabase_client = SupabaseClient().get_client()
