import streamlit as st
import replicate
import os

st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣神器")

# 1. 檢查 API Token
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API Token，請檢查 Streamlit Secrets 設定。")
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
    st.success("✅ API 密鑰已接通！")

# 2. 上傳區域
col1, col2 = st.columns(2)

with col1:
    st.write("### 1. 上傳衣服")
    cloth_file = st.file_uploader("選擇衣服照片", type=["jpg", "png", "jpeg"], key="cloth")
    if cloth_file:
        st.image(cloth_file, caption="衣服上傳成功", use_container_width=True)

with col2:
    st.write("### 2. 上傳人物")
    model_file = st.file_uploader("選擇人物照片", type=["jpg", "png", "jpeg"], key="model")
    if model_file:
        st.image(model_file, caption="人物上傳成功", use_container_width=True)

# 3. 按鈕執行
if st.button("✨ 開始魔法換裝", type="primary"):
    if cloth_file and model_file:
        with st.spinner("🚀 AI 正在計算中...大約需要 30-60 秒，請勿關閉視窗"):
            try:
                # 呼叫最新的 IDM-VTON 模型
                model_version = "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c"
                
                output = replicate.run(
                    model_version,
                    input={
                        "garm_img": cloth_file,
                        "human_img": model_file,
                        "category": "upper_body",
                        "garment_des": "a stylish garment",
                        "crop": True,
                        "seed": 42
                    }
                )
                
                if output:
                    st.image(output, caption="✨ 換裝完成！", use_container_width=True)
                    st.balloons()
                else:
                    st.error("❌ AI 沒有回傳結果，請稍後再試。")
                    
            except Exception as e:
                st.error(f"❌ 發生錯誤：{str(e)}")
    else:
        st.warning("⚠️ 請確認「兩邊」照片都已上傳，並看到預覽圖出現在畫面上。")
