import streamlit as st
from supabase import create_client, Client

# Supabaseの接続情報（後で設定します）
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("傘レンタル・プロトタイプ")

# データの読み込み
res = supabase.table("stands").select("*").eq("location_name", "熊本駅前1号機").execute()

if res.data:
    data = res.data[0]
    st.metric("現在の在庫", f"{data['current_stock']} 本")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("傘を借りる (-1)"):
            new_stock = data['current_stock'] - 1
            supabase.table("stands").update({"current_stock": new_stock, "is_unlocked": True}).eq("id", data['id']).execute()
            st.rerun()

    with col2:
        if st.button("傘を返す (+1)"):
            new_stock = data['current_stock'] + 1
            supabase.table("stands").update({"current_stock": new_stock, "is_unlocked": True}).eq("id", data['id']).execute()
            st.rerun()
