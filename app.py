import streamlit as st
import replicate
import os

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

# --- 2. API 密鑰讀取 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API KEY，請確認 Streamlit Secrets 設定正確且無斷行")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# --- 3. 初始化長期記憶 (Session State) ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None
if "cloth_img" not in st.session_state:
    st.session_state["cloth_img"] = None

# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳照片", "AI 文字生成"])
    if st.button("🧹 清除照片重新開始"):
        st.session_state["human_img"] = None
        st.session_state["cloth_img"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 5. 人物底圖區域 ---
with col1:
    st.subheader("1. 準備人物底圖")
    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="h_up")
        if uploaded_human:
            # 存入記憶前先確保指標歸零
            uploaded_human.seek(0)
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell:a7788470a256920272b7891789c629851722e0300d86b72a6b2a3b04c861214c",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 模特兒生成失敗：{e}")
    
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 6. 衣服照片區域 ---
with col2:
    st.subheader("2. 準備衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="c_up")
    if uploaded_cloth:
        # 確保指標歸零
        uploaded_cloth.seek(0)
        st.session_state["cloth_img"] = uploaded_cloth
    
    if st.session_state["cloth_img"]:
        st.image(st.session_state["cloth_img"], caption="✅ 衣服已就緒", use_container_width=True)

# --- 7. 開始魔法換裝 (加入關鍵修正邏輯) ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        with st.spinner("🚀 AI 試衣間正在合成中...約 30-50 秒"):
            try:
                # 【關鍵修正函數】處理指標歸零
                def get_file_content(item):
                    if hasattr(item, "read"):
                        item.seek(0) # 確保讀取點在開頭
                        return item
                    return item # 如果是 URL 字串則直接返回

                garm_file = get_file_content(st.session_state["cloth_img"])
                human_file = get_file_content(st.session_state["human_img"])

                # 使用 Prediction 模式
                prediction = replicate.predictions.create(
                    version="8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "garm_img": garm_file,
                        "human_img": human_file,
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "denoise_steps": 30
                    }
                )

                prediction.wait()

                if prediction.status == "succeeded":
                    final_url = prediction.output
                    if isinstance(final_url, list): final_url = final_url[0]
                    st.write("### ✨ 換裝成果：")
                    st.image(final_url, use_container_width=True)
                    st.balloons()
                else:
                    st.error(f"❌ 處理失敗: {prediction.error}")
                    st.write("除錯細節：", prediction.logs)

            except Exception as e:
                st.error(f"❌ 執行發生錯誤：{str(e)}")
                if "429" in str(e):
                    st.info("💡 提醒：頻率過高，請等 10 秒後再點一次。")
    else:
        st.warning("⚠️ 請確認人物底圖與衣服照片都已經準備好囉！")
