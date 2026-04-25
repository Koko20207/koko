import streamlit as st
    import requests
    import time

    st.set_page_config(page_title="AI 虛擬試衣", page_icon="👗")
    st.title("👗 AI 虛擬試衣神器")

    從 Streamlit Secrets 讀取 API Token
    API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN")

    def run_replicate_prediction(cloth_file, model_file):
        # 1. 將上傳的檔案上傳至 Replicate 的檔案儲存服務以取得 URL
        def upload_to_replicate(file):
            url = "https://api.replicate.com/v1/files"
            headers = {"Authorization": f"Token {API_TOKEN}"}
            files = {'file': (file.name, file.getvalue(), file.type)}
            response = requests.post(url, headers=headers, files=files)
            return response.json()["urls"]["get"]

        cloth_url = upload_to_replicate(cloth_file)
        model_url = upload_to_replicate(model_file)

        # 2. 發送試衣請求
        url = "https://api.replicate.com/v1/predictions"
        headers = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "version": "f17837e10265261d7637841c6d36e2f18374d64082260021c37b98d30e38600d",
            "input": {
                "garm_img": cloth_url,
                "human_img": model_url,
                "garment_des": "high quality clothing",
                "denoise_steps": 30
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        pred_id = response.json()["id"]

        # 3. 等待結果
        with st.spinner("正在生成中，請稍候..."):
            while True:
                res = requests.get(f"https://api.replicate.com/v1/predictions/{pred_id}", headers=headers)
                data = res.json()
                if data["status"] in ["succeeded", "failed"]:
                    return data
                time.sleep(3)

    UI 介面
    uploaded_cloth = st.file_uploader("1. 上傳衣服照片", type=["jpg", "png", "jpeg"])
    uploaded_model = st.file_uploader("2. 上傳模特兒照片", type=["jpg", "png", "jpeg"])

    if uploaded_cloth and uploaded_model:
        if st.button("生成試衣結果"):
            result = run_replicate_prediction(uploaded_cloth, uploaded_model)
            if result["status"] == "succeeded":
                st.success("生成完成！")
                st.image(result["output"], caption="試衣結果")
                st.link_button("下載圖片", result["output"])
            else:
                st.error(f"生成失敗: {result.get('error')}")