import streamlit as st
import replicate
import os

# 1. 網頁基本設定
st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗", layout="wide")
st.title("👗 AI 虛擬試衣神器 + 智慧模特兒生成")

# 2. 從 Secrets 讀取 API Token 並設定給環境變數
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
else:
    st.error("❌ 找不到 API Token，請在 Streamlit Cloud 的 Secrets 中設定。")

# 3. 初始化 Session State (確保圖片狀態可以跨元件保存)
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None

# 4. 介面佈局：左側控制面板，右側成果顯示
with st.sidebar:
    st.header("🛠️ 設定核心輸入")
    uploaded_cloth = st.file_uploader("1. 上傳衣服照片", type=["jpg", "png", "jpeg"])
    
    st.divider()
    
    st.header("👥 模特兒來源")
    source_option = st.radio("選擇模特兒來源：", ["自己上傳", "使用範例圖片"])
    
    if source_option == "自己上傳":
        uploaded_human = st.file_uploader("2. 上傳模特兒照片", type=["jpg", "png", "jpeg"])
        if uploaded_human:
            st.session_state["human_img"] = uploaded_human
    else:
        # 提供一個固定的範例圖片 URL (也可以換成您喜歡的)
        st.info("已為您選用預設模特兒")
        st.session_state["human_img"] = "https://replicate.delivery/xpbkg/f12e1f2b-8872-4638-8686-e75924765792/human.png"

# 5. 主畫面 logic
col_cloth, col_human = st.columns(2)

with col_cloth:
    if uploaded_cloth:
        st.image(uploaded_cloth, caption="已上傳的衣服", use_container_width=True)
    else:
        st.info("請在左側上傳衣服照片")

with col_human:
    if st.session_state["human_img"]:
        st.image(st.session_state["human_img"], caption="目標模特兒", use_container_width=True)
    else:
        st.info("請提供模特兒照片")

st.divider()

# 6. ✨ 開始換裝按鈕 (整合您提供的邏輯)
if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img"] and uploaded_cloth:
        if not REPLICATE_API_TOKEN:
            st.warning("⚠️ API Token 未設定，無法執行。")
        else:
            with st.spinner("🚀 AI 試衣間正在合成中...約 30-50 秒"):
                try:
                    # 呼叫最新的穩定模型版本
                    result = replicate.run(
                        "yisol/idm-vton:8a89b0ab59a050244a751b6475d91041a8507204ca1d1bc659c853177719790c",
                        input={
                            "garm_img": uploaded_cloth, 
                            "human_img": st.session_state["human_img"],
                            "garment_des": "a high quality garment",
                            "category": "upper_body",
                            "denoise_steps": 30
                        }
                    )

                    if result:
                        st.success("✨ 換裝完成！")
                        # 處理結果 (可能是 URL 或陣列)
                        img_url = result[0] if isinstance(result, list) else result
                        
                        st.write("### 🖼️ 最終成果：")
                        st.image(img_url, use_container_width=True)
                        
                        # 提供下載按鈕
                        st.download_button("📥 下載試穿照", requests.get(img_url).content, "result.png", "image/png")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ 換裝過程中出錯：{e}")
                    st.exception(e) # 顯示更詳細的錯誤資訊方便除錯
    else:
        st.warning("⚠️ 請確認已同時具備「衣服」與「模特兒」照片。")
