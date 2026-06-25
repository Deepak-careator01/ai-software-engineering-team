"""Supabase connectivity verification script. No database writes."""

from app.services.db.supabase_client import supabase_client

if supabase_client is None:
    print("WARNING: Supabase client could not be created.")
    print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file.")
else:
    print("Supabase client created successfully")
    print(type(supabase_client))
