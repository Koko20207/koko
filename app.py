import random

# ===== 初始化 =====
if "human_img" not in st.session_state:
    st.session_state["human_img"] = None

# ===== 高成功率 Prompt（關鍵）=====
base_prompt = """
a full body front view photo of a young asian female model,
standing straight, arms naturally down,
symmetrical pose,
wearing a plain white t-shirt,
no hands covering body,
no crossed arms,
clean white background,
studio lighting,
high resolution,
fashion catalog style
"""

# ===== 隨機微調（讓人不同但不亂）=====
variations = [
    "slight smile",
    "neutral expression",
    "professional expression"
]

# ===== 生成按鈕 =====
if st.button("✨ 自動生成最佳模特兒"):
    with st.spinner("生成中（高成功率）..."):
        try:
            prompt = base_prompt + ", " + random.choice(variations)

            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934c3fba5b0c5d8e8f5d9a1f6f9c0c1b8c7c5b9a1d9f1e8e7c6d",
                input={
                    "prompt": prompt,
                    "width": 512,
                    "height": 768,
                    "seed": random.randint(1, 999999)
                }
            )

            result = output[0] if isinstance(output, list) else output

            st.session_state["human_img"] = result
            st.image(result, caption="✅ 已自動選擇最佳模特兒")

        except Exception as e:
            st.error(f"生成失敗：{str(e)}")
