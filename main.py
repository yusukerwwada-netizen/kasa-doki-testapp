import streamlit as st
from supabase import create_client, Client

# Supabase接続設定
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("傘シェア・シミュレーター")

# --- データの取得 ---
stand_res = supabase.table("stands").select("*").eq("location_name", "熊本駅前1号機").execute()
if stand_res.data:
    stand = stand_res.data[0]
    
    # 状態表示
    st.subheader(f"場所: {stand['location_name']}")
    col_a, col_b = st.columns(2)
    col_a.metric("在庫数", f"{stand['current_stock']} 本")
    
    # ロックの状態を可視化
    lock_status = "🔓 解錠中" if stand['is_unlocked'] else "🔒 施錠中"
    col_b.metric("ロック状態", lock_status)

    st.divider()

    # --- ユーザー操作（スマホ画面のイメージ） ---
    if not stand['is_unlocked']:
        # ロックがかかっている時だけ、操作ボタンを出す
        c1, c2 = st.columns(2)
        if c1.button("傘を借りる"):
            if stand['current_stock'] > 0:
                supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
                st.info("ロックを開けました。傘を取り出してください。")
                st.rerun()
            else:
                st.error("在庫がありません。")
        
        if c2.button("傘を返す"):
            supabase.table("stands").update({"is_unlocked": True}).eq("id", stand['id']).execute()
            st.info("ロックを開けました。傘を差し込んでください。")
            st.rerun()

    else:
        # --- ハードウェアのシミュレーション（本来はM5Stackがやる動作） ---
        st.warning("⚠️ 現在ロックが開いています。物理的な動きを待機中...")
        
        # リミットスイッチを模した隠しボタン
        if st.button("（物理）傘がゲートを通過した！"):
            # 在庫の増減判定（本来はアプリ側で「貸出中」フラグ等を見て判断）
            # 今回は簡易的に「直前の動作」を判定するか、手動で選ぶ形にします
            st.write("傘の通過を検知。在庫を更新し、ロックを閉めます。")
            
            # ここでは「借りる」か「返す」かを選択させるシミュレーション
            action = st.radio("今の動作は？", ["借りた", "返した"])
            
            diff = -1 if action == "借りた" else 1
            new_stock = stand['current_stock'] + diff
            
            # DB更新
            supabase.table("stands").update({
                "current_stock": new_stock,
                "is_unlocked": False
            }).eq("id", stand['id']).execute()
            
            st.success(f"{action}処理が完了しました！")
            st.rerun()
