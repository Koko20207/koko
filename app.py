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

# --- 2. 初始化長期記憶 ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None
if "cloth_img" not in st.session_state:
    st.session_state["cloth_img"] = None

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("模特兒來源", ["自己上傳照片", "AI 文字生成"])
    if st.button("🧹 清除所有照片重新開始"):
        st.session_state["human_img"] = None
        st.session_state["cloth_img"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 4. 人物底圖區域 ---
with col1:
    st.subheader("1. 準備人物底圖")
    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="h_u")
        if uploaded_human:
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    # 【修正】移除長編號，直接使用模型路徑
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 模特兒生成失敗：{e}")
    
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 5. 衣服照片區域 ---
with col2:
    st.subheader("2. 準備衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="c_u")
    if uploaded_cloth:
        st.session_state["cloth_img"] = uploaded_cloth
    
    if st.session_state["cloth_img"]:
        st.image(st.session_state["cloth_img"], caption="✅ 衣服已就緒", use_container_width=True)

# --- 6. 開始魔法換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        with st.spinner("🚀 AI 試衣間合成中...約 30-50 秒"):
            try:
                # 【修正】移除長編號，直接使用模型路徑
                result = replicate.run(
                    "yisol/idm-vton",
                    input={
                        "garm_img": st.session_state["cloth_img"],
                        "human_img": st.session_state["human_img"],
                        "garment_des": "a stylish garment",
                        "category": "upper_body"
                    }
                )

                if result:
                    final_url = result[0] if isinstance(result, list) else result
                    st.write("### ✨ 換裝成果：")
                    st.image(final_url, use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 換裝失敗：{e}")
    else:
        st.warning("⚠️ 請確認人物與衣服都已經準備好囉！")
