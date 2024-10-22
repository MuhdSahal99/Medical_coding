import streamlit as st
import os
from mistralai import Mistral
import time

class MedicalCodingAssistant:
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"

    def analyze_medical_record(self, medical_record):
        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical coding expert specializing in determining underlying causes of death 
                        and assigning appropriate ICD-10 codes. Analyze the medical record to determine the true underlying 
                        cause of death, not just the immediate cause."""
                    },
                    {
                        "role": "user",
                        "content": f"""Please analyze this medical record and:
                        1. Identify the underlying root cause of death
                        2. Explain the causal chain leading to death
                        3. Suggest the most appropriate ICD-10 code for the underlying cause
                        4. Provide rationale for why this is the root cause rather than immediate cause

                        Medical Record:
                        {medical_record}"""
                    }
                ]
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing medical record: {str(e)}"

def display_typing_effect(text, result_placeholder):
    """Display text with typing effect."""
    full_text = ""
    for char in text:
        full_text += char
        result_placeholder.markdown(full_text + "▌")
        time.sleep(0.01)  # Adjust typing speed here
    result_placeholder.markdown(full_text)

def main():
    st.set_page_config(page_title="Medical Record Analysis", page_icon="🏥", layout="wide")
    
    st.title("Medical Record Analysis System")
    st.write("Upload a medical record to analyze the underlying cause of death")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Enter  Key", type="password")
        st.markdown("""
        ### Instructions:
        1. Upload a medical record text file
        2. Click analyze to get results
        """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Medical Record", type=['txt'])
    
    if uploaded_file and api_key:
        # Read and display the original text
        text_content = uploaded_file.read().decode()
        
        st.subheader("Medical Record")
        st.text(text_content)
        
        # Analyze button
        if st.button("Analyze Cause of Death"):
            with st.spinner("Analyzing medical record..."):
                try:
                    assistant = MedicalCodingAssistant(api_key)
                    result = assistant.analyze_medical_record(text_content)
                    
                    # Display results with typing effect
                    st.subheader("Analysis Results")
                    result_placeholder = st.empty()
                    display_typing_effect(result, result_placeholder)
                    
                    # Add download button for the analysis
                    st.download_button(
                        label="Download Analysis",
                        data=result,
                        file_name="medical_analysis_report.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    elif not api_key:
        st.warning("Please enter your Mistral API key in the sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("Medical Record Analysis System - For Healthcare Professionals Only")

if __name__ == "__main__":
    main()