import streamlit as st
import replicate
import os

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

# --- 2. API 密鑰安全讀取 ---
# 會先從 Streamlit Secrets 找，找不到再找環境變數
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 API KEY，請至 Streamlit Secrets 設定並確認沒有斷行")
    st.stop()
else:
    # 這裡會確保 API 密鑰被系統正確讀取
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# --- 3. 初始化長期記憶 (Session State) ---
# 確保生成模特兒或上傳衣服後，不會因為按了按鈕而消失
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None
if "cloth_img" not in st.session_state:
    st.session_state["cloth_img"] = None

# --- 4. 側邊欄：功能面板 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳照片", "AI 文字生成"])
    if st.button("🧹 清除所有照片重新開始"):
        st.session_state["human_img"] = None
        st.session_state["cloth_img"] = None
        st.rerun()
    st.markdown("---")
    st.info("💡 提醒：若剛更換 Token 或儲值，請靜候 2-5 分鐘讓系統同步。")

col1, col2 = st.columns(2)

# --- 5. 人物底圖區域 ---
with col1:
    st.subheader("1. 準備人物底圖")
    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="h_up_key")
        if uploaded_human:
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    # 使用 Flux 穩定版本編號
                    output = replicate.run(
                        "black-forest-labs/flux-schnell:a7788470a256920272b7891789c629851722e0300d86b72a6b2a3b04c861214c",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 模特兒生成失敗：{e}")
    
    # 顯示人物記憶
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 6. 衣服照片區域 (加強記憶邏輯) ---
with col2:
    st.subheader("2. 準備衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="c_up_key")
    
    # 如果有新上傳，就更新記憶
    if uploaded_cloth:
        st.session_state["cloth_img"] = uploaded_cloth
    
    # 顯示衣服記憶
    if st.session_state["cloth_img"]:
        st.image(st.session_state["cloth_img"], caption="✅ 衣服已就緒", use_container_width=True)

# --- 7. 開始魔法換裝 (採用非同步 Prediction 模式) ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        with st.spinner("🚀 AI 試衣間正在排隊合成中...約需 30-60 秒"):
            try:
                # 參考您的建議：使用 predictions.create 配合 wait() 提升成功率
                prediction = replicate.predictions.create(
                    version="8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "garm_img": st.session_state["cloth_img"],
                        "human_img": st.session_state["human_img"],
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "denoise_steps": 30
                    }
                )

                # 等待直到雲端計算完成
                prediction.wait()

                if prediction.status == "succeeded":
                    # 處理回傳結果，可能是陣列或網址字串
                    output = prediction.output
                    final_url = output[0] if isinstance(output, list) else output
                    st.write("### ✨ 換裝成果：")
                    st.image(final_url, use_container_width=True)
                    st.balloons()
                else:
                    st.error(f"❌ 處理失敗: {prediction.error}")
                    
            except Exception as e:
                st.error(f"❌ 執行發生錯誤：{str(e)}")
                if "429" in str(e):
                    st.info("💡 提示：請求太頻繁，請等 10 秒後再按一次。")
                elif "402" in str(e):
                    st.warning("💡 提示：錢包餘額正在同步中，請稍候再試。")
    else:
        st.warning("⚠️ 請確認人物底圖與衣服照片都已經準備好囉！")
