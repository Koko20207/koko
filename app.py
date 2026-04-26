import io
import os
import streamlit as st
import replicate

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

# --- 2. API 密鑰讀取 ---
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 REPLICATE_API_TOKEN，請確認 .streamlit/secrets.toml 或部署平台的 Secrets 設定正確")
    st.stop()

os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# --- 3. 初始化 session state ---
if "human_img_bytes" not in st.session_state:
    st.session_state["human_img_bytes"] = None

if "cloth_img_bytes" not in st.session_state:
    st.session_state["cloth_img_bytes"] = None


def to_file_obj(image_bytes):
    """把 bytes 轉成可提供給 Replicate 的檔案物件"""
    return io.BytesIO(image_bytes)


def normalize_output_file(output):
    """處理 Replicate 各種可能回傳格式"""
    if isinstance(output, list):
        return output[0]
    return output


# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳照片", "AI 文字生成"])

    if st.button("🧹 清除照片重新開始"):
        st.session_state["human_img_bytes"] = None
        st.session_state["cloth_img_bytes"] = None
        st.rerun()

col1, col2 = st.columns(2)

# --- 5. 人物底圖區域 ---
with col1:
    st.subheader("1. 準備人物底圖")

    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader(
            "選擇您的照片",
            type=["jpg", "png", "jpeg"],
            key="h_up"
        )

        if uploaded_human is not None:
            st.session_state["human_img_bytes"] = uploaded_human.getvalue()

    else:
        prompt = st.text_area(
            "模特兒描述咒語",
            value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background"
        )

        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={
                            "prompt": prompt,
                            "aspect_ratio": "3:4"
                        }
                    )

                    if output:
                        generated_file = normalize_output_file(output)
                        generated_bytes = generated_file.read() if hasattr(generated_file, "read") else generated_file
                        st.session_state["human_img_bytes"] = generated_bytes
                        st.success("✅ 生成成功！")
                    else:
                        st.error("❌ AI 模特兒沒有成功產生圖片")

                except Exception as e:
                    st.error(f"❌ 模特兒生成失敗：{e}")

    if st.session_state["human_img_bytes"]:
        st.image(st.session_state["human_img_bytes"], caption="人物底圖", use_container_width=True)

# --- 6. 衣服照片區域 ---
with col2:
    st.subheader("2. 準備衣服照片")

    uploaded_cloth = st.file_uploader(
        "上傳衣服照片",
        type=["jpg", "png", "jpeg"],
        key="c_up"
    )

    if uploaded_cloth is not None:
        st.session_state["cloth_img_bytes"] = uploaded_cloth.getvalue()

    if st.session_state["cloth_img_bytes"]:
        st.image(st.session_state["cloth_img_bytes"], caption="✅ 衣服已就緒", use_container_width=True)

# --- 7. 開始魔法換裝 ---
st.markdown("---")

if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img_bytes"] and st.session_state["cloth_img_bytes"]:
        with st.spinner("🚀 AI 試衣間正在合成中...約需 30-60 秒"):
            try:
                human_file = to_file_obj(st.session_state["human_img_bytes"])
                garm_file = to_file_obj(st.session_state["cloth_img_bytes"])

                output = replicate.run(
                    "cuuupid/idm-vton",
                    input={
                        "human_img": human_file,
                        "garm_img": garm_file,
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "steps": 30
                    }
                )

                if output:
                    result_file = normalize_output_file(output)
                    result_image = result_file.read() if hasattr(result_file, "read") else result_file

                    st.write("### ✨ 換裝成果：")
                    st.image(result_image, use_container_width=True)
                    st.balloons()
                else:
                    st.error("❌ 換裝失敗，模型沒有回傳圖片")

            except Exception as e:
                st.error(f"❌ 執行錯誤：{e}")
                if "429" in str(e):
                    st.info("💡 提示：如果您看到 429，代表系統正在控管流量，請靜候 1 分鐘再按一次！")

    else:
        st.warning("⚠️ 請確認人物底圖與衣服照片都已經準備好囉！")
