import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣 & 模特兒生成", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成神器")

# --- 1. 密鑰檢查 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN")
if not replicate_api_token:
    st.error("❌ 找不到 API Token，請檢查 Streamlit Secrets")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# 儲存生成的圖片網址
if 'generated_model_url' not in st.session_state:
    st.session_state['generated_model_url'] = None

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.header("🎨 功能設定")
    function_mode = st.radio("第一步：選擇模特兒來源", ["自己上傳人物照片", "AI 文字生成模特兒"])
    st.info("💡 建議：AI 生成模特兒後，再上傳衣服進行換裝。")

col1, col2 = st.columns(2)

# --- 3. 準備模特兒 ---
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
            with st.spinner("🚀 AI 畫家中...請稍候"):
                try:
                    # 改用自動選擇最新版的寫法 (stability-ai/sdxl)
                    output = replicate.run(
                        "stability-ai/sdxl",
                        input={
                            "prompt": model_prompt,
                            "negative_prompt": "cartoon, ugly, deformed, blurry",
                            "width": 768,
                            "height": 1024
                        }
                    )
                    if output:
                        st.session_state['generated_model_url'] = output[0]
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{str(e)}")
                    st.info("💡 如果出現 401，請檢查 API Key；如果是 422，可能是模型暫時維修。")

        if st.session_state['generated_model_url']:
            st.image(st.session_state['generated_model_url'], caption="✅ AI 生成模特兒", use_container_width=True)
            final_human_img = st.session_state['generated_model_url']

# --- 4. 上傳衣服 ---
with col2:
    st.subheader("2. 上傳衣服照片")
    cloth_file = st.file_uploader("選擇衣服", type=["jpg", "png", "jpeg"], key="cloth")
    if cloth_file:
        st.image(cloth_file, caption="✅ 衣服已就緒", use_container_width=True)

# --- 5. 執行試衣 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if cloth_file and final_human_img:
        with st.spinner("🚀 試衣間合成中...預計 30-50 秒"):
            try:
                # 試衣模型 IDM-VTON
                output = replicate.run(
                    "yisol/idm-vton",
                    input={
                        "garm_img": cloth_file,
                        "human_img": final_human_img,
                        "category": "upper_body",
                        "garment_des": "a stylish shirt"
                    }
                )
                if output:
                    st.image(output, caption="✨ 換裝成果圖", use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 換裝失敗：{str(e)}")
    else:
        st.warning("⚠️ 請確認「人物」與「衣服」都已經準備好喔！")
