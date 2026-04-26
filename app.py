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

# --- 2. 初始化 Session State (記憶功能) ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None
if "cloth_img" not in st.session_state:
    st.session_state["cloth_img"] = None

# --- 3. 側邊欄：選擇模特兒來源 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("模特兒來源", ["自己上傳照片", "AI 文字生成"])
    st.markdown("---")
    st.info("💡 提醒：若錢包餘額為 $0，AI 將無法運作。")

col1, col2 = st.columns(2)

# --- 4. 處理人物底圖 ---
with col1:
    st.subheader("1. 人物底圖")
    if mode == "自己上傳照片":
        uploaded_file = st.file_uploader("上傳人物照", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.session_state["human_img"] = uploaded_file
            st.image(uploaded_file, caption="✅ 已選取人物", use_container_width=True)
    else:
        prompt = st.text_area("模特兒咒語", value="A photorealistic portrait of a beautiful Asian female model, standing front, white t-shirt, studio background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在揮毫..."):
                try:
                    # 使用 Flux 模型生成 (目前最快最穩)
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = output[0]
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")
        
        if st.session_state["human_img"]:
            st.image(st.session_state["human_img"], caption="✅ AI 模特兒", use_container_width=True)

# --- 5. 處理衣服照片 ---
with col2:
    st.subheader("2. 衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照", type=["jpg", "png", "jpeg"])
    if uploaded_cloth:
        st.session_state["cloth_img"] = uploaded_cloth
        st.image(uploaded_cloth, caption="✅ 衣服已就緒", use_container_width=True)

# --- 6. 開始換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        with st.spinner("🚀 試衣間合成中...請等候約 30 秒"):
            try:
                # 執行 IDM-VTON 換裝
                result = replicate.run(
                    "yisol/idm-vton",
                    input={
                        "garm_img": st.session_state["cloth_img"],
                        "human_img": st.session_state["human_img"],
                        "category": "upper_body"
                    }
                )
                if result:
                    st.image(result, caption="🎉 換裝完成！", use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 換裝出錯：{e}")
                st.info("如果是 402 或 422 錯誤，通常是錢包沒錢或是模型忙碌中。")
    else:
        st.warning("⚠️ 請確認人物與衣服都已經準備好喔！")
