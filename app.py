import streamlit as st
import PIL.Image

import json

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
    with st.container(height=500, border=True):
        img_ = st.file_uploader(label=":red[Upload your image]",
                               type=["png", "jpg", "jpeg", "webp"],
                               accept_multiple_files=False,
                               key="image0",
                               help="Upload your image to generate a description",
                               disabled=not api_key)

        # show the image
        if img_ is not None:
            st.image(img_, caption="Uploaded Image", use_container_width=True)

            # save the image with PIL.Image
            img = PIL.Image.open(img_)




def get_analysis(prompt, image):
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Set up the model
    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 8192,
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

    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp",
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
(provide a confidence score for this assessment. (0-100))

2. Professional Appearance:

Analyse the image and describe the attire of the person in the image. Tell what he/she is wearing. If the attire is appropriate for a professional setting, tell the user that their attire is appropriate for a professional setting. If the attire is not appropriate for a professional setting, tell the user that their attire might not be suitable for a professional setting. If the attire is not appropriate for a professional setting, suggest the user to wear more formal clothing for their profile picture. Also include background in this assessment. Describe the background of the person. If the background is simple and uncluttered, tell the user about it, that it is  allowing the focus to remain on them. If the background is not good, tell the user about it. If the background is not suitable, suggest the user to use a plain background or crop the image to remove distractions.
(provide a confidence score for this assessment. (0-100))

3. Face Visibility:

Analyse the image and describe the visibility of the person's face. If the face is clearly visible and unobstructed, tell the user that their face is clearly visible and unobstructed. If the face is partially covered by any objects or hair, making it difficult to see the face clearly, tell the user about it. Also tell where the person is looking. If the person is looking away, suggest the user to look into the camera for a more direct connection.
(provide a confidence score for this assessment. (0-100))

4. Appropriate Expression:

Describe the expression of the person in the image. If the expression is friendly and approachable, tell the user about it. If the expression is overly serious, stern, or unprofessional, tell the user user about it. If the expression is not appropriate, suggest the user to consider a more relaxed and natural smile for a more approachable look.
(provide a confidence score for this assessment. (0-100))

5. Filters and Distortions:

Describe the filters and distortions applied to the image. If the image appears natural and unaltered, tell the user about it. If the image appears to be excessively filtered, edited, or retouched, tell the user about it. If the image is excessively filtered, edited, or retouched, suggest the user to opt for a natural-looking photo for a more genuine impression.
(provide a confidence score for this assessment. (0-100))

6. Single Person and No Pets:

Describe the number of people and pets in the image. If the image contains only the user, tell the user about it. If the image contains multiple people or pets, tell the user about it. If the image contains multiple people or pets, suggest the user to crop the image to remove distractions.
(provide a confidence score for this assessment. (0-100))

Final review:

At the end give a final review on whether the image is suitable for a LinkedIn profile photo. Also the reason for your review.
"""

output_format = """
Output the result as a raw JSON string as follows:
resolution and clarity: [Your description and analysis.], resolution and clarity confidence: [score here], professional appearance: [Your description and analysis.], professional appearance confidence: [score here], face visibility: [Your description and analysis.], face visibility confidence: [score here], appropriate expression: [Your description and analysis.], appropriate expression confidence: [score here], filters and distortions: [Your description and analysis.], filters and distortions confidence: [score here], single person and no pets: [Your description and analysis.], single person and no pets confidence: [score here], final_review: [Your final review.]
Don't use ```json to format the output. Just output the raw JSON string.
"""

prompt = role + instructions + output_format

image_parts = [
    {
        "mime_type": "image/jpeg",
        "data": img
    }
]

with col2:
    with st.container(height=500, border=True):
        st.markdown(":grey[Click the button to see the analysis]")
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
                    # parse the json response
                    response = json.loads(analysis)

                    # get the features
                    features = [
                        response["resolution and clarity"],
                        response["professional appearance"],
                        response["face visibility"],
                        response["appropriate expression"],
                        response["filters and distortions"],
                        response["single person and no pets"]
                    ]

                    # get the confidence scores
                    confidence_scores = [
                        response["resolution and clarity confidence"],
                        response["professional appearance confidence"],
                        response["face visibility confidence"],
                        response["appropriate expression confidence"],
                        response["filters and distortions confidence"],
                        response["single person and no pets confidence"]
                    ]

                    headings = [
                        "Resolution and Clarity",
                        "Professional Appearance",
                        "Face Visibility",
                        "Appropriate Expression",
                        "Filters and Distortions",
                        "Single Person and No Pets"
                    ]     

                    final_review = response["final_review"]            

                    for i in range(6):

                        st.divider()

                        st.markdown(f"**{headings[i]}**\n\n{features[i]}")

                        # show progress bar
                        st.progress(int(confidence_scores[i]), text=f"confidence score: {confidence_scores[i]}")

                    st.divider()

                    st.markdown(f"**Final review:**\n{final_review}")