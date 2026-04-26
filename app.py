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

# --- 3. 初始化長期記憶 ---
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
            uploaded_human.seek(0)
            st.session_state["human_img"] = uploaded_human
    else:
        prompt = st.text_area("模特兒描述咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        # 【修正】：解開 FileOutput 的物流箱，取出網址
                        flux_url = output[0]
                        if hasattr(flux_url, "url"):
                            flux_url = flux_url.url
                        elif hasattr(flux_url, "read"):
                            flux_url = flux_url.read()
                            
                        st.session_state["human_img"] = flux_url
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
        uploaded_cloth.seek(0)
        st.session_state["cloth_img"] = uploaded_cloth
    
    if st.session_state["cloth_img"]:
        st.image(st.session_state["cloth_img"], caption="✅ 衣服已就緒", use_container_width=True)

# --- 7. 開始魔法換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        with st.spinner("🚀 AI 試衣間正在合成中...約需 30-60 秒"):
            try:
                def get_file_content(item):
                    if hasattr(item, "seek"):
                        item.seek(0)
                    return item

                garm_file = get_file_content(st.session_state["cloth_img"])
                human_file = get_file_content(st.session_state["human_img"])

                output = replicate.run(
                    "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                    input={
                        "garm_img": garm_file,
                        "human_img": human_file,
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "denoise_steps": 30
                    }
                )

                if output:
                    final_url = output if isinstance(output, (str, bytes)) else output[0]
                    
                    # 【關鍵修正】：解開 FileOutput 的物流箱，取出換裝後的圖片網址
                    if hasattr(final_url, "url"):
                        final_url = final_url.url
                    elif hasattr(final_url, "read"):
                        final_url = final_url.read()
                    
                    st.write("### ✨ 換裝成果：")
                    st.image(final_url, use_container_width=True)
                    st.balloons()
                    
            except Exception as e:
                st.error(f"❌ 執行錯誤：{str(e)}")
                if "429" in str(e):
                    st.info("💡 提示：如果您看到 429，代表系統正在控管流量，請靜候 1 分鐘再按一次！")
    else:
        st.warning("⚠️ 請確認人物底圖與衣服照片都已經準備好囉！")
