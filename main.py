import streamlit as st
from supabase import create_client, Client

# --- 1. 接続設定 ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. 画面左側のメニュー ---
st.sidebar.title("操作メニュー")
app_mode = st.sidebar.radio("表示モードを切り替え", ["利用者用", "管理者用", "開発・テスト用"])

# --- 3. データの取得 ---
# 傘立て情報
res_stand = supabase.table("stands").select("*").eq("location_name", "熊本駅前1号機").execute()
stand = res_stand.data[0] if res_stand.data else None

# ユーザー情報（今はテスト用に特定のユーザーIDを固定で使います）
# 本来はログインしているユーザーのIDを使います
user_id = "test-user-001" 
res_user = supabase.table("users").select("*").eq("id", user_id).execute()
user = res_user.data[0] if res_user.data else None

# --- 4. モード別表示 ---

if app_mode == "利用者用":
    st.title("☂️ くまもん傘シェア")
    
    if stand and user:
        # ロックが開いている（物理操作待ち）の時
        if stand['is_unlocked']:
            st.warning("🔒 ロックを解除しました。傘立てを操作してください。")
            st.info("※傘を引き抜く、または差し込むと自動的に画面が戻ります。")
        
        # ロックが閉まっている時
        else:
            if not user['is_renting']:
                # 何も借りていない時 → 借りるボタンのみ
                st.write("現在は何も借りていません。")
                if st.button("傘を借りる"):
                    # 借りる予約フラグを立てて、ロックを開ける
                    supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
                    st.rerun()
            else:
                # 1本借りている時 → 返すボタンのみ
                st.write("現在 1本 貸出中です。")
                if st.button("傘を返す"):
                    # 返す予約フラグを立てて、ロックを開ける
                    supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
                    st.rerun()

elif app_mode == "管理者用":
    st.title("📊 管理者ダッシュボード")
    if stand:
        st.metric("在庫数", f"{stand['current_stock']} 本")
        st.write("利用者ステータス:", "貸出中" if user['is_renting'] else "未利用")

else:
    st.title("🛠 開発・テスト（ハードウェア再現）")
    if stand and stand['is_unlocked']:
        # 利用者の状態を見て、今「借りる」動作なのか「返す」動作なのかを自動判別
        action_type = "借りる" if not user['is_renting'] else "返す"
        
        st.info(f"スマホから「{action_type}」の指示が届いています。")
        st.write("傘が通過するのを待機しています...")

        if st.button("（物理）傘が通過した！"):
            # 在庫とユーザー状態の計算
            new_stock = stand['current_stock'] - 1 if action_type == "借りる" else stand['current_stock'] + 1
            new_renting_status = True if action_type == "借りる" else False
            
            # DB一括更新
            # 1. 傘立ての在庫を更新し、ロックを閉じる
            supabase.table("stands").update({
                "current_stock": new_stock,
                "is_unlocked": False
            }).eq("id", stand['id']).execute()
            
            # 2. ユーザーの「貸出中」フラグを更新
            supabase.table("users").update({
                "is_renting": new_renting_status
            }).eq("id", user_id).execute()
            
            st.success(f"{action_type}処理が完了しました。")
            st.rerun()
    else:
        st.write("待機中：利用者からの指示を待っています。")
