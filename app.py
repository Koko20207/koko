import streamlit as st
import requests
import time
import random

# --- 頁面配置 ---
st.set_page_config(page_title="AI 虛擬試衣與模特兒生成", page_icon="👗", layout="wide")
st.title("👗 AI 虛擬試衣神器 + 智慧模特兒生成")

# --- 從 Streamlit Secrets 讀取 API Token ---
# 請確保Secrets中已設定 REPLICATE_API_TOKEN
API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN")
HEADERS = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"}

# --- 核心工具函數 ---

def upload_to_replicate(file):
    """將本地上傳的檔案上傳至 Replicate 儲存服務，取得網址"""
    url = "https://api.replicate.com/v1/files"
    # 注意：這裡不設定 Content-Type header，requests 會自動處理 boundary
    upload_headers = {"Authorization": f"Token {API_TOKEN}"}
    files = {'file': (file.name, file.getvalue(), file.type)}
    try:
        response = requests.post(url, headers=upload_headers, files=files)
        if response.status_code == 201:
            return response.json()["urls"]["get"]
        else:
            st.error(f"檔案儲存失敗: {response.text}")
            return None
    except Exception as e:
        st.error(f"上傳發生錯誤: {e}")
        return None

def poll_prediction(pred_id, spinner_text):
    """輪詢等待 Replicate 任務完成"""
    with st.spinner(spinner_text):
        while True:
            res = requests.get(f"https://api.replicate.com/v1/predictions/{pred_id}", headers=HEADERS)
            data = res.json()
            if data["status"] in ["succeeded", "failed", "canceled"]:
                return data
            time.sleep(3)

# --- 功能函數 ---

def generate_ai_model(gender, style, pose):
    """【功能一】呼叫繪圖 AI (Flux 模型) 生成隨機模特兒"""
    # 根據選擇構建 Prompt
    gender_txt = "a beautiful full-body fashion model woman" if gender == "女性" else "a handsome full-body fashion model man"
    
    # 隨機場景，增加「隨機感」
    backgrounds = ["plain grey background", "urban street style background", "luxury apartment interior", "nature park background"]
    selected_bg = random.choice(backgrounds)
    
    prompt = f"{style} photography of {gender_txt}, {pose}, standing, looking at camera, default pleasant expression, high fashion, 8k resolution, photorealistic, lighting suited for {selected_bg}, centered composition."

    url = "https://api.replicate.com/v1/predictions"
    payload = {
        # 使用目前的強大模型，例如 Flux.1-schnell (速度快)
        "version": "flux-schnell", # 或者使用完整 ID
        "input": {
            "prompt": prompt,
            "go_fast": True,
            "num_outputs": 1,
            "aspect_ratio": "9:16", # 模特兒通常是直幅
            "output_format": "jpg"
        }
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    prediction_data = response.json()
    
    if "id" not in prediction_data:
        st.error(f"生成模特兒請求失敗: {prediction_data.get('detail', '未知錯誤')}")
        return None
        
    result = poll_prediction(prediction_data["id"], "AI 正在憑空創造模特兒中...")
    
    if result["status"] == "succeeded":
        return result["output"] # 返回生成的圖片網址 (可以是 string 或 list)
    else:
        st.error(f"模特兒生成失敗: {result.get('error')}")
        return None

def run_tryon_prediction(cloth_url, model_url):
    """【功能二】呼叫試衣模型結合衣服與模特兒"""
    url = "https://api.replicate.com/v1/predictions"
    payload = {
        # 這是原本你使用的 IDM-VTON 模型
        "version": "f17837e10265261d7637841c6d36e2f18374d64082260021c37b98d30e38600d",
        "input": {
            "garm_img": cloth_url,
            "human_img": model_url,
            "garment_des": "high quality clothing",
            "denoise_steps": 30
        }
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    prediction_data = response.json()
    
    if "id" not in prediction_data:
        st.error(f"發送試衣請求失敗: {prediction_data.get('detail', '未知錯誤')}")
        return None
    
    result = poll_prediction(prediction_data["id"], "正在將衣服穿到模特兒身上...")
    
    if result["status"] == "succeeded":
        # 確保 output 格式正確 (有些模型回傳 list)
        output_url = result.get("output")
        return output_url[0] if isinstance(output_url, list) else output_url
    else:
        st.error(f"試衣失敗: {result.get('error')}")
        return None

# --- UI 介面 ---
if not API_TOKEN:
    st.error("❌ 找不到 API Token，請在 Streamlit Secrets 中設定 `REPLICATE_API_TOKEN`。")
    st.stop()

st.sidebar.header("🔧 設定核心輸入")
uploaded_cloth = st.sidebar.file_uploader("1. 上傳衣服照片", type=["jpg", "png", "jpeg"])

st.sidebar.divider()
st.sidebar.header("👯 模特兒來源")
model_source = st.sidebar.radio("選擇模特兒來源:", ("自己上傳", "AI 生成隨機模特兒"))

final_model_url = None # 儲存最終要用於試衣的模特兒網址

col_main, col_res = st.columns([2, 1])

with col_main:
    # 衣服顯示區
    st.subheader("👕 衣服與模特兒確認")
    c1, c2 = st.columns(2)
    with c1:
        if uploaded_cloth:
            st.image(uploaded_cloth, caption="你上傳的衣服", use_container_width=True)
        else:
            st.info("請在左側上傳衣服照片")

    with c2:
        if model_source == "自己上傳":
            uploaded_model = st.sidebar.file_uploader("2. 上傳模特兒照片", type=["jpg", "png", "jpeg"])
            if uploaded_model:
                st.image(uploaded_model, caption="你上傳的模特兒", use_container_width=True)
                # 上傳檔案到 Replicate
                if st.sidebar.button("確認上傳模特兒"):
                    url = upload_to_replicate(uploaded_model)
                    if url:
                        st.session_state['uploaded_model_url'] = url
                        st.success("模特兒上傳成功！")
                
                # 從 session state 取得 URL
                final_model_url = st.session_state.get('uploaded_model_url')

        else:
            # AI 生成模特兒設定區
            st.sidebar.subheader("AI 模特兒偏好")
            m_gender = st.sidebar.selectbox("性別", ["女性", "男性"])
            m_style = st.sidebar.selectbox("風格", ["Studio", "Street Style", "Editorial"])
            m_pose = st.sidebar.selectbox("姿勢", ["正面向前 standing normally", "手放口袋 standing hands in pockets", "稍微側身 sideways turn"])

            if st.sidebar.button("✨ 生成/更換隨機模特兒"):
                gen_output = generate_ai_model(m_gender, m_style, m_pose)
                if gen_output:
                    # 如果回傳是 list，取第一個
                    gen_url = gen_output[0] if isinstance(gen_output, list) else gen_output
                    st.session_state['generated_model_url'] = gen_url
            
            # 從 session state 取得已生成的網址顯示
            final_model_url = st.session_state.get('generated_model_url')
            if final_model_url:
                st.image(final_model_url, caption="AI 生成的模特兒", use_container_width=True)
            else:
                st.info("請點擊左側「生成隨機模特兒」按鈕")

st.divider()

# --- 生成最終結果 ---
if uploaded_cloth and final_model_url:
    if st.button("🚀 開始智慧試衣 (Combining both AI steps)", use_container_width=True):
        
        # 1. 先處理衣服 URL
        with st.spinner("正在準備衣服檔案..."):
            cloth_url = upload_to_replicate(uploaded_cloth)
        
        if cloth_url and final_model_url:
            # 2. 呼叫試衣 API
            final_result = run_tryon_prediction(cloth_url, final_model_url)
            
            if final_result:
                with col_res:
                    st.subheader("🎉 最終試衣結果")
                    st.image(final_result, use_container_width=True)
                    st.link_button("💾 下載圖片", final_result, use_container_width=True)
                    st.balloons()
else:
    st.warning("請確保已上傳衣服照片，且已選定模特兒（上傳或生成）。")
