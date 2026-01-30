import streamlit as st
from supabase import create_client, Client

# --- 1. 接続設定 ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. 画面左側のメニュー（サイドバー）を作る ---
st.sidebar.title("操作メニュー")
app_mode = st.sidebar.radio("表示モードを切り替え", ["利用者用", "管理者用", "開発・テスト用"])

# --- 3. データの取得 ---
res = supabase.table("stands").select("*").eq("location_name", "熊本駅前1号機").execute()
stand = res.data[0] if res.data else None

# --- 4. 選んだモードによって表示を変える ---

if app_mode == "利用者用":
    st.title("☂️ くまもん傘シェア")
    if stand:
        st.subheader(f"設置場所: {stand['location_name']}")
        st.write("傘が必要な時、または返す時にボタンを押してください。")
        
        if not stand['is_unlocked']:
            c1, c2 = st.columns(2)
            if c1.button("傘を借りる"):
                supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
                st.rerun()
            if c2.button("傘を返す"):
                supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
                st.rerun()
        else:
            st.warning("現在、傘立てのロックが開いています。操作を待機中です...")

elif app_mode == "管理者用":
    st.title("📊 管理者ダッシュボード")
    if stand:
        st.write("### 現在の稼働状況")
        col1, col2 = st.columns(2)
        col1.metric("在庫数", f"{stand['current_stock']} 本")
        col2.metric("ロック状態", "🔓 開" if stand['is_unlocked'] else "🔒 閉")
        st.divider()
        st.write("※将来的にここに全拠点のリストや売上グラフを表示します。")

else:
    st.title("🛠 開発・テスト（ハードウェア再現）")
    st.write("この画面は「M5Stack（傘立て本体）」がやるべき動作をテストする場所です。")
    
    if stand and stand['is_unlocked']:
        st.info("スマホから解錠命令が届いています。")
        action = st.radio("今の動作は？", ["借りた", "返した"])
        
        if st.button("（物理）傘が通過した！"):
            diff = -1 if action == "借りた" else 1
            # ↓ ここでインデントエラーが起きていたので修正しました
            supabase.table("stands").update({
                "current_stock": stand['current_stock'] + diff,
                "is_unlocked": False
            }).eq("id", stand['id']).execute()
            
            st.success("物理動作を検知し、在庫を更新しました。")
            st.rerun()
    else:
        st.write("待機中：スマホからの解錠命令を待っています。")
