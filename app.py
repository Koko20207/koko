import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣 & 模特兒生成", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成神器")

# --- 1. 密鑰檢查 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN")
if not replicate_api_token:
    st.error("❌ 找不到 API Token")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

if 'generated_model_url' not in st.session_state:
    st.session_state['generated_model_url'] = None

# --- 2. 介面設計 ---
with st.sidebar:
    st.header("🎨 功能設定")
    function_mode = st.radio("第一步：選擇模特兒來源", ["自己上傳人物照片", "AI 文字生成模特兒"])
    
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 準備人物底圖")
    final_human_img = None
    if function_mode == "自己上傳人物照片":
        st.session_state['generated_model_url'] = None
        uploaded_model = st.file_uploader("選擇照片", type=["jpg", "png", "jpeg"], key="manual_model")
        if uploaded_model:
            st.image(uploaded_model, caption="✅ 已選取人物", use_container_width=True)
            final_human_img = uploaded_model
    else:
        model_prompt = st.text_area("模特兒描述", value="A photorealistic front view portrait of a beautiful Asian female model, smiling, wearing a plain white t-shirt, standing against a clean light grey studio background, high quality, sharp focus")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家中..."):
                try:
                    # 更新為目前最穩定的 SDXL 模型 ID
                    output = replicate.run(
                        "stability-ai/sdxl:7762fd0fa582491b4da970d4f3b7d197607771415dfb73a388915152a229a4a7",
                        input={"prompt": model_prompt, "negative_prompt": "cartoon, ugly, deformed", "width": 768, "height": 1024}
                    )
                    if output:
                        st.session_state['generated_model_url'] = output[0]
                except Exception as e:
                    st.error(f"生成出錯：{str(e)}")
        if st.session_state['generated_model_url']:
            st.image(st.session_state['generated_model_url'], caption="✅ AI 模特兒", use_container_width=True)
            final_human_img = st.session_state['generated_model_url']

with col2:
    st.subheader("2. 上傳衣服照片")
    cloth_file = st.file_uploader("選擇衣服", type=["jpg", "png", "jpeg"], key="cloth")
    if cloth_file:
        st.image(cloth_file, use_container_width=True)

st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if cloth_file and final_human_img:
        with st.spinner("🚀 試衣間合成中...約 30 秒"):
            try:
                # 試衣模型維持不變，它是穩定的
                output = replicate.run(
                    "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={"garm_img": cloth_file, "human_img": final_human_img, "category": "upper_body"}
                )
                if output:
                    st.image(output, caption="✨ 換裝完成！", use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"換裝失敗：{str(e)}")
