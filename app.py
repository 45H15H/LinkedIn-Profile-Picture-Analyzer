import streamlit as st
import PIL.Image

import re

# Page configuation
st.set_page_config(
    page_title="LinkedIn Profile Photo Analyzer",
    page_icon="👩‍💼",
    layout="wide"
)

# Subheader
st.subheader(":blue[LinkedIn] Profile Photo Analyzer", divider="gray")
st.caption("Powerd by Gemini Pro Vision")

# Form to enter API key
with st.form(key='api_form'):
    st.markdown("""
    Enter your Gemini API key :red[*]
    """)
    api_key = st.text_input("Enter your Gemini API key:", type='password', key = 'token', label_visibility='collapsed')
    st.form_submit_button("SUBMIT",
                        #   disabled=not api_key,
                          use_container_width=True)
    st.caption(
    "To use this app, you need an API key. "
    "You can get one [here](https://ai.google.dev/)."
    )

if not (api_key.startswith('AI') and len(api_key) == 39):
    st.warning('Please enter your credentials!', icon = '⚠️')
else:
    st.success("Proceed to use the app!", icon = '✅')

col1, col2 = st.columns(spec=[0.4, 0.6],
                        gap="medium")

img = None # initialize the image

with col1:
    with st.container(border=True):
        img_ = st.file_uploader(label=":red[Upload your image]",
                               type=["png", "jpg", "jpeg", "webp"],
                               accept_multiple_files=False,
                               key="image0",
                               help="Upload your image to generate a description",
                               disabled=not api_key)

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
      "max_output_tokens": 5000,
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

Describe the resolution and clarity of the image. Tell the user whether the image is blurry or pixelated, making it difficult to discern the features. If the image is not clear, suggest the user to upload a higher-resolution photo.
(provide a confidence score for this assessment.)

2. Professional Appearance:

Analyse the image and describe the attire of the person in the image. Tell what he/she is wearing. If the attire is appropriate for a professional setting, tell the user that their attire is appropriate for a professional setting. If the attire is not appropriate for a professional setting, tell the user that their attire might not be suitable for a professional setting. If the attire is not appropriate for a professional setting, suggest the user to wear more formal clothing for their profile picture. Also include background in this assessment. Describe the background of the person. If the background is simple and uncluttered, tell the user about it, that it is  allowing the focus to remain on them. If the background is not good, tell the user about it. If the background is not suitable, suggest the user to use a plain background or crop the image to remove distractions.
(provide a confidence score for this assessment.)

3. Face Visibility:

Analyse the image and describe the visibility of the person's face. If the face is clearly visible and unobstructed, tell the user that their face is clearly visible and unobstructed. If the face is partially covered by any objects or hair, making it difficult to see the face clearly, tell the user about it. Also tell where the person is looking. If the person is looking away, suggest the user to look into the camera for a more direct connection.
(provide a confidence score for this assessment.)

4. Appropriate Expression:

Describe the expression of the person in the image. If the expression is friendly and approachable, tell the user about it. If the expression is overly serious, stern, or unprofessional, tell the user user about it. If the expression is not appropriate, suggest the user to consider a more relaxed and natural smile for a more approachable look.
(provide a confidence score for this assessment.)

5. Filters and Distortions:

Describe the filters and distortions applied to the image. If the image appears natural and unaltered, tell the user about it. If the image appears to be excessively filtered, edited, or retouched, tell the user about it. If the image is excessively filtered, edited, or retouched, suggest the user to opt for a natural-looking photo for a more genuine impression.
(provide a confidence score for this assessment.)

6. Single Person and No Pets:

Describe the number of people and pets in the image. If the image contains only the user, tell the user about it. If the image contains multiple people or pets, tell the user about it. If the image contains multiple people or pets, suggest the user to crop the image to remove distractions.
(provide a confidence score for this assessment.)

Final review:

At the end give a final review on whether the image is suitable for a LinkedIn profile photo. Also the reason for your review.
"""

output_format = """
Your report should be structured like shown in triple backticks below:

```
**1. Resolution and Clarity:**\n[description] (confidence: [confidence score]%)

**2. Professional Appearance:**\n[description] (confidence: [confidence score]%)

**3. Face Visibility:**\n[description] (confidence: [confidence score]%)

**4. Appropriate Expression:**\n[description] (confidence: [confidence score]%)

**5. Filters and Distortions:**\n[description] (confidence: [confidence score]%)

**6. Single Person and No Pets:**\n[description] (confidence: [confidence score]%)

**Final review:**\n[your review]
```

You should also provide a confidence score for each assessment, ranging from 0 to 100.

Don't copy the above text. Write your own report.

And always keep your output in this format.

For example:

**1. Resolution and Clarity:**\n[Your description and analysis.] (confidence: [score here]%)

**2. Professional Appearance:**\n[Your description and analysis.] (confidence: [socre here]%)

**3. Face Visibility:**\n[Your description and analysis.] (confidence: [score her]%)

**4. Appropriate Expression:**\n[Your description and analysis.] (confidence: [score here]%)

**5. Filters and Distortions:**\n[Your description and analysis.] (confidence: [score here]%)

**6. Single Person and No Pets:**\n[Your description and analysis.] (confidence: [score here]%)

**Final review:**\n[Your review]

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
        st.markdown(":grey[Click the button to analyze the image]")
        analyze_button = st.button("ANALYZE",
                                   type="primary",
                                   disabled=not img_,
                                   help="Analyze the image",
                                   use_container_width=True)
        
        

        if analyze_button:
            # show spinner while generating
            with st.spinner("Analyzing..."):

                try:
                    # get the analysis
                    analysis = get_analysis(prompt, img)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
                else:

                    # find all the headings that are enclosed in ** **
                    headings = re.findall(r"\*\*(.*?)\*\*", analysis)

                    # find all the features that are after ** and before (confidence
                    features = re.findall(r"\*\*.*?\*\*\n(.*?)\s\(", analysis)

                    # find all the confidence scores that are after (confidence: and before %)
                    confidence_scores = re.findall(r"\(confidence: (.*?)\%\)", analysis)

                    # find the final review which is after the last confidence score like this:
                    # (confidence: 50%)\n\n(.*?)
                    final_review = re.findall(r"\*\*Final review:\*\*\n(.*?)$", analysis)[0]
                
                    for i in range(6):

                        st.divider()

                        st.markdown(f"**{headings[i]}**\n\n{features[i]}")

                        # show progress bar
                        st.progress(int(confidence_scores[i]), text=f"confidence score: {confidence_scores[i]}")

                    st.divider()

                    st.markdown(f"**Final review:**\n{final_review}")