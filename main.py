import streamlit as st
import base64
from openai import OpenAI

import smtplib
from email.message import EmailMessage

from markdown_pdf import MarkdownPdf
from markdown_pdf import Section

def save_email(receiver):
    file_path = "emails.txt"

    with open(file_path, "r") as file:
        existing_emails = [email.strip() for email in file.readlines()]

    if receiver not in existing_emails: 
        with open(file_path, 'a') as file:
            file.write(f"{receiver}\n")

def send_email(receiver, response):
    try:
        save_email(receiver)
        
        response = f"""| ![Logo](logo.png) | <div>**Contact Person**<br>**Name:** Mr. Koay Kheng Huat<br>**Phone:** 012 400 1158<br>**Email:** Khenghuat.koay@eliteindigo.com</div> |\n|:--:|---|\n\n{response}"""

        pdf = MarkdownPdf(toc_level = 2, optimize = True)
        pdf.add_section(Section(response), user_css = "div {padding: 0px; margin-top: 10px; margin-left: 30px; text-align:left}\n p{text-align:justify}")
        pdf.save(f"{receiver}.pdf")

        msg = EmailMessage()
        msg["Subject"] = "PalmAanalysis.ai Report"
        msg["From"] = st.secrets.email_sender
        msg["To"] = receiver
        msg["Cc"] = st.secrets.email_cc
        msg.set_content("Dear Sir/Madam,\n\nHere is the report from PalmAnalysis.ai.\n\nThank you.\n\nSincere regards,\n\nPalmAnalysis.ai")
        
        file_data = open(f"{receiver}.pdf", "rb").read()
        msg.add_attachment(file_data, maintype = "application", subtype = "octet-stream", filename = "palmAnalysis.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets.email_sender, st.secrets.email_password)
            smtp.send_message(msg)

        return True

    except Exception as e:
        return e

st.image("logo.png")
st.title("PalmAnalysis.ai : Discovering Your Strength, Empower Your Future")

enable = st.checkbox("Enable camera")
img = st.camera_input("Take a picture", disabled = not enable)

api_key = st.secrets.openai_api_key
if "has_response" not in st.session_state:
    st.session_state.has_response = False

if img:
    with st.form("my_form"):
        if not st.session_state.has_response:
            client = OpenAI(api_key = api_key)

            img = img.getvalue()
            base64_image = base64.b64encode(img).decode("utf-8")

            response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "input_text", "text": "You are an expert in Palm Reading. You will get my left palm, analyze the image and give me a detail report on my strengths and give me top 3 career advise. You also will provide me 3 areas of development." },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
            )

            st.session_state.palm_res = response.output_text

        st.session_state.has_response = True
        
        st.header("Response")
        st.write(st.session_state.palm_res)

        st.header("Send Report")
        
        receiver = st.text_input("Email")
        submitted = st.form_submit_button("Send")

        if submitted: 
            msg = send_email(receiver, st.session_state.palm_res)
            if msg == True:
                st.info("The report is sent. ")
            else:
                st.error(msg)

else:
    st.session_state.has_response = False