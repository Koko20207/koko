import io
import os
import streamlit as st
import replicate

st.set_page_config(page_title="AI 虛擬試衣神器", page_icon="👗")
st.title("👗 AI 虛擬試衣 & 模特兒生成")

replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

if not replicate_api_token:
    st.error("❌ 找不到 REPLICATE_API_TOKEN，請確認 .streamlit/secrets.toml 或部署平台 Secrets 設定正確")
    st.stop()

os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

if "human_img_bytes" not in st.session_state:
    st.session_state["human_img_bytes"] = None

if "cloth_img_bytes" not in st.session_state:
    st.session_state["cloth_img_bytes"] = None


def to_file_obj(image_bytes):
    return io.BytesIO(image_bytes)


def normalize_output(output):
    if isinstance(output, list):
        return output[0]
    return output


with st.sidebar:
    st.header("🎨 設定面板")
    mode = st.radio("第一步：選擇模特兒來源", ["自己上傳照片", "AI 文字生成"])

    if st.button("🧹 清除照片重新開始"):
        st.session_state["human_img_bytes"] = None
        st.session_state["cloth_img_bytes"] = None
        st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 準備人物底圖")

    if mode == "自己上傳照片":
        uploaded_human = st.file_uploader("選擇您的照片", type=["jpg", "png", "jpeg"], key="h_up")
        if uploaded_human is not None:
            st.session_state["human_img_bytes"] = uploaded_human.getvalue()
    else:
        prompt = st.text_area(
            "模特兒描述咒語",
            value="A professional studio portrait of a beautiful Asian female model, front view, wearing a plain white t-shirt, clean background",
        )

        if st.button("✨ 生成 AI 模特兒"):
            with st.spinner("🚀 AI 畫家正在生成中..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={
                            "prompt": prompt,
                            "aspect_ratio": "3:4",
                        },
                    )

                    if output:
                        generated = normalize_output(output)
                        generated_bytes = generated.read() if hasattr(generated, "read") else generated
                        st.session_state["human_img_bytes"] = generated_bytes
                        st.success("✅ 生成成功！")
                    else:
                        st.error("❌ AI 模特兒沒有成功產生圖片")

                except Exception as e:
                    st.error(f"❌ 模特兒生成失敗：{e}")

    if st.session_state["human_img_bytes"]:
        st.image(st.session_state["human_img_bytes"], caption="人物底圖", use_container_width=True)

with col2:
    st.subheader("2. 準備衣服照片")

    uploaded_cloth = st.file_uploader("上傳衣服照片", type=["jpg", "png", "jpeg"], key="c_up")
    if uploaded_cloth is not None:
        st.session_state["cloth_img_bytes"] = uploaded_cloth.getvalue()

    if st.session_state["cloth_img_bytes"]:
        st.image(st.session_state["cloth_img_bytes"], caption="✅ 衣服已就緒", use_container_width=True)

st.markdown("---")

if st.button("✨ ✨ 開始魔法換裝 ✨ ✨", type="primary", use_container_width=True):
    if st.session_state["human_img_bytes"] and st.session_state["cloth_img_bytes"]:
        with st.spinner("🚀 AI 試衣間正在合成中...約需 30-60 秒"):
            try:
                human_file = to_file_obj(st.session_state["human_img_bytes"])
                garm_file = to_file_obj(st.session_state["cloth_img_bytes"])

                output = replicate.run(
                    "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
                    input={
                        "human_img": human_file,
                        "garm_img": garm_file,
                        "garment_des": "a high quality garment",
                        "category": "upper_body",
                        "steps": 30,
                    },
                )

                if output:
                    result = normalize_output(output)
                    st.write("### ✨ 換裝成果：")
                    st.image(result, use_container_width=True)
                    st.balloons()
                else:
                    st.error("❌ 換裝失敗，模型沒有回傳圖片")

            except Exception as e:
                st.error(f"❌ 執行錯誤：{e}")
                if "429" in str(e):
                    st.info("💡 提示：如果看到 429，代表流量限制中，請等 1 分鐘後再試一次")
   
