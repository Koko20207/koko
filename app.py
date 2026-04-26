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

# --- 2. 初始化 Session ---
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None
if "cloth_img" not in st.session_state:
    st.session_state["cloth_img"] = None

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("模特兒來源", ["自己上傳照片", "AI 文字生成"])
    if st.button("🧹 清除照片重新開始"):
        st.session_state["human_img"] = None
        st.session_state["cloth_img"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 4. 人物底圖 ---
with col1:
    st.subheader("1. 人物底圖")
    if mode == "自己上傳照片":
        uploaded_file = st.file_uploader("上傳人物照", type=["jpg", "png", "jpeg"], key="u_human")
        if uploaded_file:
            st.session_state["human_img"] = uploaded_file
    else:
        prompt = st.text_area("模特兒咒語", value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background")
        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在揮毫..."):
                try:
                    # 使用 Flux 畫家
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt, "aspect_ratio": "3:4"}
                    )
                    if output:
                        st.session_state["human_img"] = str(output[0])
                        st.success("✅ 生成成功！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")
    
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="人物底圖", use_container_width=True)

# --- 5. 衣服照片 ---
with col2:
    st.subheader("2. 衣服照片")
    uploaded_cloth = st.file_uploader("上傳衣服照", type=["jpg", "png", "jpeg"], key="u_cloth")
    if uploaded_cloth:
        st.session_state["cloth_img"] = uploaded_cloth
        st.image(uploaded_cloth, caption="要穿的衣服", use_container_width=True)

# --- 6. 開始換裝 ---
st.markdown("---")
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    # 檢查是否兩張圖都有了
    if st.session_state["human_img"] and st.session_state["cloth_img"]:
        progress_text = st.empty()
        progress_text.info("🚀 AI 試衣間啟動中...這一步大約需要 30-60 秒，請勿重新整理頁面")
        
        try:
            # 呼叫 IDM-VTON 換裝模型 (加上 garment_des 讓它更準確)
            result = replicate.run(
                "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                input={
                    "garm_img": st.session_state["cloth_img"],
                    "human_img": st.session_state["human_img"],
                    "garment_des": "a stylish garment",
                    "category": "upper_body"
                }
            )
            
            if result:
                progress_text.empty()
                st.write("### ✨ 換裝成果：")
                st.image(result, use_container_width=True)
                st.balloons()
            else:
                st.error("❌ AI 合成失敗：模型沒有回傳圖片。")
                
        except Exception as e:
            progress_text.empty()
            st.error(f"❌ 換裝發生錯誤：{e}")
            if "402" in str(e) or "balance" in str(e).lower():
                st.warning("💡 偵測到錢包餘額不足，請檢查 Replicate 帳單頁面是否扣款成功。")
    else:
        st.warning("⚠️ 缺照片喔！請確認「人物」跟「衣服」都已經顯示在上面了。")
