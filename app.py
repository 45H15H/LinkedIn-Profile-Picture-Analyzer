import streamlit as st
import PIL.Image

import re

# Page configuation
st.set_page_config(
    page_title="Streamlit App",
    page_icon="🧊",
    layout="wide"
)

# Title
st.title("Streamlit App")

# Subheader
st.subheader("Subheader")

# Form to enter API key
with st.form(key='api_form'):
    st.markdown("""
    Enter your Gemini API key :red[*]
    """)
    api_key = st.text_input("Enter your Gemini API key:", type='password', key = 'token', label_visibility='collapsed')
    st.form_submit_button("SUBMIT",
                          disabled=not api_key,
                          use_container_width=True)

if not (api_key.startswith('AI') and len(api_key) == 39):
    st.warning('Please enter your credentials!', icon = '⚠️')
else:
    st.success("Proceed to use the app!", icon = '✅')

col1, col2 = st.columns(spec=[0.4, 0.6],
                        gap="medium")

img = None # initialize the image

with col1:
    with st.container(border=True):
        img_ = st.file_uploader(label="Upload an image",
                               type=["png", "jpg", "jpeg", "webp"],
                               accept_multiple_files=False,
                               key="image0",
                               help="Upload an image to generate a description",
                               disabled=not api_key)
                               # label visibility: collapsed

        # show the image
        if img_ is not None:
            st.image(img_, caption="Uploaded Image", use_column_width=True)

            # save the image with PIL.Image
            img = PIL.Image.open(img_)




def get_analysis(prompt, image):
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Set up the model
    generation_config = {
      "temperature": 0.9,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 2048
    }

    safety_settings = [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      }
    ]

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    response = model.generate_content([prompt, image])

    return response.text


role = """
You are a highly skilled AI trained to review LinikedIn profile photos and provide feedback on their quality. You are a professional and your feedback should be constructive and helpful.
"""

instructions = """
You are provided with an image file depicting a LinkedIn profile photo.

Your job is to proved a structured report analyzing the image based on the following criteria:

1. Resolution and Clarity:

Good: "The image is high-resolution and clear, showcasing your facial features and details." (Optionally, provide a confidence score for this assessment.)
Bad: "The image is blurry or pixelated, making it difficult to discern your features. Consider uploading a higher-resolution photo."

2. Professional Appearance:

Good: "Your attire is appropriate for a professional setting (business casual or formal)." (Highlight specific elements like a blazer, collared shirt, etc.)
Bad: "The attire might not be suitable for a professional setting. Consider wearing more formal clothing for your profile picture."
Neutral Background: "The background is simple and uncluttered, allowing the focus to remain on you."
Distracting Background: "The background is busy or cluttered, potentially drawing attention away from you. Consider using a plain background or cropping the image to remove distractions."

3. Face Visibility:

Good: "Your face is clearly visible and unobstructed."
Bad: "Your face is partially covered by objects or hair, making it difficult to see you clearly. Reposition yourself or adjust the hairstyle for better visibility."

4. Appropriate Expression:

Good: "You have a friendly and approachable expression, making you look welcoming and open to connections."
Bad: "Your expression appears overly serious, stern, or unprofessional. Consider a more relaxed and natural smile for a more approachable look."

5. Filters and Distortions:

Good: "The photo appears natural and unaltered, showcasing your authentic appearance."
Bad: "Excessive filters, editing, or retouching can misrepresent your look. Opt for a natural-looking photo for a more genuine impression."
"""

output_format = """
Your report should be structured as follows:

**1. Resolution and Clarity:** \n
     [Good features/Bad features]
**2. Professional Appearance:** \n
     [Good features/Bad features]
**3. Face Visibility:** \n
     [Good features/Bad features]
**4. Appropriate Expression:** \n
     [Good features/Bad features]
**5. Filters and Distortions:** \n
     [Good features/Bad features]

Don't mention Good or Bad only write the features.

You should also provide a confidence score for each assessment, ranging from 0 to 100.

At the end give a final review on whether the image is suitable for a LinkedIn profile photo. Also the reason for your review.

For example:

**1. Resolution and Clarity:** \n
     [Good features/Bad features] (confidence: 90%)

**2. Professional Appearance:** \n
     [Good features/Bad features] (confidence: 80%)

**3. Face Visibility:** \n
     [Good features/Bad features] (confidence: 70%)

**4. Appropriate Expression:** \n
     [Good features/Bad features] (confidence: 60%)

**5. Filters and Distortions:** \n
     [Good features/Bad features] (confidence: 50%)

Final review in short paragraph.

"""

prompt = role + instructions + output_format

image_parts = [
    {
        "mime_type": "image/jpeg",
        "data": img
    }
]

with col2:
    with st.container(border=True):
        analyze_button = st.button("ANALYZE",
                                   type="primary",
                                   disabled=not img_,
                                   help="Analyze the image",
                                   use_container_width=True)

        if analyze_button:
            # show spinner while generating
            with st.spinner("Analyzing..."):
                # get the analysis
                analysis = get_analysis(prompt, img)

                placeholder = st.empty()

                placeholder.markdown(f"{analysis}")

                # find all the headings that are enclosed in ** **
                headings = re.findall(r"\*\*(.*?)\*\*", analysis)

                # find all the features that are after ** and before (confidence
                features = re.findall(r"\*\*\s\n\n\s{5}(.*?) \(confidence", analysis)

                # find all the confidence scores that are after (confidence: and before %)
                confidence_scores = re.findall(r"\(confidence: (.*?)\%\)", analysis)

                # find the final review which is after the last confidence score like this:
                # (confidence: 50%)\n\n(.*?)
                final_review = re.findall(r"\(confidence: (.*?)\%\)\n\n(.*?)$", analysis, re.DOTALL)[0][1]

                # show the headings
                st.write("Headings:", headings)

                # show the features
                st.write("Features:", features)

                # show the confidence scores
                st.write("Confidence Scores:", confidence_scores)

                # show the final review
                st.write("Final Review:", final_review)

                st.text_area("Analysis", value=analysis, height=500)



            # display the analysis
            # st.write(analysis)