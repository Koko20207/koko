import streamlit as st
import replicate
import os
import requests
from io import BytesIO

st.set_page_config(page_title="AI 虛擬試衣 & 模特兒生成", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成神器")

# --- 1. 初始化與密鑰檢查 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API Token，請檢查 Streamlit Secrets 設定。")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
    # st.success("✅ API 密鑰已接通！") # 測試成功後可關閉這行，讓介面乾淨點

# 使用 st.session_state 來存儲生成的模特兒圖片網址，防止網頁重整消失
if 'generated_model_url' not in st.session_state:
    st.session_state['generated_model_url'] = None

# --- 2. 介面設計 ---
with st.sidebar:
    st.header("🎨 功能設定")
    function_mode = st.radio("第一步：選擇模特兒來源", ["自己上傳人物照片", "AI 文字生成模特兒"])
    
    st.markdown("---")
    st.write("💡 **說明：** 如果使用 AI 生成，請務必使用下方建議的「咒語」，確保模特兒穿著素色簡約衣物，試衣效果才會好。")

col1, col2 = st.columns(2)

# --- 3. 處理模特兒來源 ---
with col1:
    st.subheader("1. 準備人物底圖")
    final_human_img = None
    
    if function_mode == "自己上傳人物照片":
        # 模式 A：手動上傳
        st.session_state['generated_model_url'] = None # 清除生成的圖片
        uploaded_model = st.file_uploader("選擇您或模特兒的照片", type=["jpg", "png", "jpeg"], key="manual_model")
        if uploaded_model:
            st.image(uploaded_model, caption="✅ 已選取上傳人物", use_container_width=True)
            final_human_img = uploaded_model
            
    else:
        # 模式 B：AI 生成
        model_prompt = st.text_area(
            "輸入模特兒描述 (咒語)", 
            value="A photorealistic front view portrait of a beautiful Asian female model, smiling, wearing a plain white t-shirt, standing against a clean light grey studio background, high quality, sharp focus",
            height=100
            )
        
        if st.button("✨ 生成 AI 模特兒", type="secondary"):
            with st.spinner("🚀 AI 畫家中...大約 15 秒..."):
                try:
                    # 使用穩定且高品質的 SDXL 模型生成人物
                    model_gen_version = "stability-ai/sdxl:39ed52f6c48e8d618d205c1d4c782273897063d6de68316f734f3611ad592404"
                    output = replicate.run(
                        model_gen_version,
                        input={
                            "prompt": model_prompt,
                            "negative_prompt": "cartoon, ugly, deformed, complex clothing, patterns on shirt",
                            "width": 768,
                            "height": 1024,
                            "num_outputs": 1,
                            "scheduler": "K_EULER",
                            "num_inference_steps": 30,
                            "guidance_scale": 7.5
                        }
                    )
                    if output and len(output) > 0:
                        st.session_state['generated_model_url'] = output[0]
                        st.success("✅ AI 模特兒生成成功！")
                    else:
                        st.error("❌ 生成失敗，請再試一次。")
                except Exception as e:
                    st.error(f"❌ 生成出錯：{str(e)}")

        # 顯示生成的模特兒（如果有）
        if st.session_state['generated_model_url']:
            st.image(st.session_state['generated_model_url'], caption="✅ AI 生成的模特兒", use_container_width=True)
            # Replicate 接受 URL，所以我們直接用 URL
            final_human_img = st.session_state['generated_model_url']

# --- 4. 準備衣服與最後換裝 ---
with col2:
    st.subheader("2. 上傳衣服照片")
    cloth_file = st.file_uploader("選擇衣服照片", type=["jpg", "png", "jpeg"], key="cloth")
    if cloth_file:
        st.image(cloth_file, caption="✅ 衣服上傳成功", use_container_width=True)

    st.markdown("---")
    st.subheader("3. 開始換裝")
    # 最後執行按鈕
    if st.button("✨ ✨ 魔法換裝按鈕 ✨ ✨", type="primary", use_container_width=True):
        # 關鍵檢查：必須有衣服 AND 有人物（不論是生成的還是上傳的）
        if cloth_file and final_human_img:
            with st.spinner("🚀 AI 試衣間正在努力合成中...約 30-60 秒..."):
                try:
                    # 呼叫最新的 IDM-VTON 試衣模型
                    vton_version = "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c"
                    
                    output = replicate.run(
                        vton_version,
                        input={
                            "garm_img": cloth_file,
                            "human_img": final_human_img, # 這裡是檔案或 URL
                            "category": "upper_body",
                            "garment_des": "a stylish garment",
                            "crop": True,
                            "seed": 42
                        }
                    )
                    
                    if output:
                        st.write("---")
                        st.image(output, caption="✨ 🎉 換裝完成！", use_container_width=True)
                        st.balloons()
                    else:
                        st.error("❌ AI 沒有回傳結果。")
                        
                except Exception as e:
                    st.error(f"❌ 算圖失敗：{str(e)}")
                    st.info("💡 提示：算圖失敗通常是雲端伺服器忙碌，可以稍候 1 分鐘再按一次。")
        else:
            if not cloth_file:
                st.warning("⚠️ 請先上傳「衣服」照片喔！")
            if not final_human_img:
                st.warning("⚠️ 請先「生成」或「上傳」模特兒照片喔！")
