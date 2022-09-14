import os
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
from gotrue import helpers

load_dotenv("heavy_variables/environment.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
# Sign in using the user email and password.
version = "Unknown"
def boot():
    try:
        email = "sriniranjan.gs@gmail.com"
        user = supabase.auth.sign_in(email=email)
        return f"Signed Boot"
    except helpers.APIError:
        return f"Non-Signed Boot"

def add(guild, features: dict):
    try:
        supabase.table('Test').insert({**{'server': guild}, **features}).execute()
    except Exception:
        return

def update(guild, features):
    data = supabase.table("Test").update(features).eq("server", guild).execute()

def get():
    return supabase.table("Test").select("*").execute().data
# data = supabase.table("Test").update(guild_features[ctx.guild]).eq("server", ctx.guild).execute()
# Assert we pulled real data.
data = supabase.table('Test').insert({'value1': '56', 'server': "reminder"}).execute()
results = supabase.table("Test").select("*").execute()
# assert len(data.data) > 0
print(results.data)