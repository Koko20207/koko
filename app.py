import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

# --- 1. API 密鑰 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API KEY，請至 Streamlit Secrets 設定")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# --- 2. 初始化 Session (確保模特兒生成後不會消失) ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳人物照片", "AI 文字生成"])
    if st.button("🧹 清除所有照片"):
        st.session_state["human_img"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 4. 人物底圖區域 ---
with col1:
    st.subheader("1. 準備人物底圖")
    if mode == "自己上傳人物照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="manual_u")
        if uploaded_human:
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 Flux 畫家正在生成中..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")
    
    # 顯示人物圖
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 5. 衣服照片區域 (恢復最直接的顯示方式) ---
with col2:
    st.subheader("2. 準備衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="cloth_u")
    
    # 直接檢查上傳檔案是否存在，不透過 session_state 以免檔案物件失效
    if uploaded_cloth:
        st.image(uploaded_cloth, caption="✅ 衣服已選取", use_container_width=True)

# --- 6. 開始換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and uploaded_cloth:
        with st.spinner("🚀 AI 試衣間正在合成中...約 30-50 秒"):
            try:
                # 執行 IDM-VTON 換裝
                result = replicate.run(
                    "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "garm_img": uploaded_cloth, # 直接傳遞上傳的檔案物件
                        "human_img": st.session_state["human_img"],
                        "garment_des": "a stylish garment",
                        "category": "upper_body"
                    }
                )
                if result:
                    st.write("### ✨ 換裝成果：")
                    st.image(result, use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 換裝出錯：{e}")
                if "402" in str(e):
                    st.warning("💡 提示：這代表 Replicate 錢包餘額不足，請檢查儲值是否成功。")
    else:
        st.warning("⚠️ 請確認「人物底圖」與「衣服照片」都已經準備好囉！")
