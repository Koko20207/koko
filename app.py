import random

# ===== 隨機模特兒參數 =====
styles = [
    "asian female model",
    "korean fashion model",
    "japanese model",
    "young asian woman",
]

poses = [
    "front view, standing straight",
    "slightly angled pose",
    "casual standing pose",
]

expressions = [
    "neutral expression",
    "slight smile",
    "professional look",
]

backgrounds = [
    "clean white background",
    "light grey studio background",
]

# 👉 每次隨機組合
random_prompt = f"""
{random.choice(styles)},
{random.choice(poses)},
{random.choice(expressions)},
wearing a plain white t-shirt,
{random.choice(backgrounds)},
high quality, studio lighting
"""

if st.button("🎲 隨機生成模特兒"):
    with st.spinner("生成中..."):
        try:
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934c3fba5b0c5d8e8f5d9a1f6f9c0c1b8c7c5b9a1d9f1e8e7c6d",
                input={
                    "prompt": random_prompt,
                    "width": 512,
                    "height": 768,
                    "num_outputs": 1,
                    "seed": random.randint(1, 999999)  # 🔥 關鍵：隨機種子
                }
            )

            result = output[0] if isinstance(output, list) else output
            st.session_state["human_img"] = result
            st.image(result)

        except Exception as e:
            st.error(f"生成失敗：{str(e)}")
