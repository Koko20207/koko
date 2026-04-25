import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣神器")

# 這裡會自動從您剛設定的 Secrets 讀取
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 密鑰讀取失敗！請確認 Secrets 設定中包含 REPLICATE_API_TOKEN")
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
    st.success("✅ API 密鑰已接通！")

col1, col2 = st.columns(2)
with col1:
    cloth_img = st.file_uploader("1. 上傳衣服照片", type=["jpg", "png", "jpeg"])
with col2:
    model_img = st.file_uploader("2. 上傳人物照片", type=["jpg", "png", "jpeg"])

if st.button("✨ 開始魔法換裝"):
    if cloth_img and model_img:
        with st.spinner("🚀 AI 正在努力合成中，大約需要 30 秒..."):
            try:
                # 呼叫 Replicate 上的 IDM-VTON 模型
                output = replicate.run(
                    "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "crop": False,
                        "seed": 42,
                        "steps": 30,
                        "category": "upper_body",
                        "garm_img": cloth_img,
                        "human_img": model_img,
                        "garment_des": "a photo of a garment"
                    }
                )
                if output:
                    st.image(output, caption="✨ 換裝完成！", use_column_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 算圖出錯了：{e}")
    else:
        st.warning("⚠️ 請先上傳兩張照片喔！")
