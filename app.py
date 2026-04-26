import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

# --- 1. API 密鑰設定 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API KEY，請至 Streamlit Secrets 設定")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# --- 2. 初始化 Session (維持模特兒圖片) ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None

# --- 3. 側邊欄：功能選擇 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳照片", "AI 文字生成"])
    if st.button("🧹 清除所有照片"):
        st.session_state["human_img"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 4. 人物底圖區域 ---
with col1:
    st.subheader("1. 人物底圖")
    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="human_u")
        if uploaded_human:
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    # 使用 Flux 模型
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        # 生成的是網址字串
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")
    
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 5. 衣服照片區域 ---
with col2:
    st.subheader("2. 衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="cloth_u")
    if uploaded_cloth:
        st.image(uploaded_cloth, caption="✅ 衣服已就緒", use_container_width=True)

# --- 6. 開始魔法換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and uploaded_cloth:
        with st.spinner("🚀 AI 試衣間正在合成中...請耐心等候約 30-50 秒"):
            try:
                # 參考您提供的修正邏輯：
                # IDM-VTON 模型呼叫
                result = replicate.run(
                    "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "garm_img": uploaded_cloth,           # 衣服檔案
                        "human_img": st.session_state["human_img"], # 人物檔案或 URL
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "denoise_steps": 30
                    }
                )

                if result:
                    # 處理回傳結果：有時候是陣列，有時候是字串
                    final_url = result[0] if isinstance(result, list) else result
                    st.write("### ✨ 換裝成果：")
                    st.image(final_url, use_container_width=True)
                    st.balloons()
                else:
                    st.error("❌ AI 沒能回傳結果圖片，請稍後再試。")
                    
            except Exception as e:
                st.error(f"❌ 換裝失敗：{e}")
                st.write("🔧 除錯資訊：", e) # 顯示完整錯誤，方便我們排查
    else:
        st.warning("⚠️ 請確認人物與衣服都已經準備好囉！")
