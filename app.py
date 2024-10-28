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
                        "content": """You are an expert medical coder with over 20 years of experience in clinical documentation 
                        and ICD-10 coding. You have extensive knowledge in reviewing medical records across all specialties 
                        including emergency medicine, internal medicine, surgery, obstetrics, and critical care.

                        APPROACH EACH MEDICAL RECORD LIKE THIS:

                        1. INITIAL ASSESSMENT:
                           - Review complete record thoroughly
                           - Identify department/setting (Emergency, Ward, ICU, etc.)
                           - Note patient demographics and presentation
                           - Understand timeline of events
                           - Identify key clinical findings and interventions

                        2. CLINICAL CONTEXT ANALYSIS:
                           - Assess if this is an emergency/acute presentation or chronic condition
                           - Look for pre-existing conditions and their relationship to death
                           - Evaluate documented symptoms, signs, and test results
                           - Consider the clinical progression and response to interventions
                           - Check if death was witnessed or unwitnessed
                           - Review any resuscitation attempts and their outcomes

                        3. CAUSE OF DEATH DETERMINATION:
                           Direct Cause:
                           - What immediately led to death?
                           - Is it clearly documented in the record?
                           - Are there objective clinical findings supporting this?

                           Intermediate Causes:
                           - What conditions led to the direct cause?
                           - Are there clear causal relationships?
                           - Is the sequence clinically logical?

                           Underlying Cause:
                           - What started the chain of events?
                           - Is it documented in the history?
                           - Does it make clinical sense?

                        4. TIME INTERVAL ASSESSMENT:
                           - Use documented dates/times when available
                           - Look for disease progression markers
                           - Consider typical disease trajectories when exact times aren't given
                           - Be honest about uncertainty - use "Unknown" if not clear

                        5. SPECIAL CONSIDERATIONS:
                           For Emergency Cases:
                           - Note exact timings of events
                           - Document interventions and responses
                           - Consider pre-hospital events
                           
                           For Maternal Cases:
                           - Check if female aged 15-49
                           - Verify pregnancy status or recent delivery
                           - Look for pregnancy-related complications
                           - Exclude external causes

                           For Chronic Conditions:
                           - Evaluate disease progression
                           - Note complications
                           - Consider multiple organ involvement"""
                    },
                    {
                        "role": "user",
                        "content": f"""Based on your expert analysis of this medical record, provide:

                        CLINICAL SCENARIO:
                        [Provide clear, concise summary of the case and key events]

                        DEATH CERTIFICATION:
                        Direct Cause of Death: [Diagnosis with ICD code]
                        Time Interval: [Specify]

                        First Intermediate Cause: [Diagnosis with ICD code if present]
                        Time Interval: [Specify]

                        Second Intermediate Cause: [Diagnosis with ICD code if present]
                        Time Interval: [Specify]

                        Underlying Cause: [Diagnosis with ICD code]
                        Time Interval: [Specify]

                        MATERNAL MORTALITY: [Yes/No/Not Applicable with clear reasoning]

                        CLINICAL REASONING:
                        [Explain your coding decisions, including why you chose these causes and sequence]

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
    st.set_page_config(page_title="Clinical Documentation Analysis", page_icon="🏥", layout="wide")
    
    st.title("Medical Record Analysis System")
    st.write("Professional Clinical Documentation and Coding Analysis")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Enter Mistral API Key", type="password")
        st.markdown("""
        ### System Capabilities:
        - Comprehensive medical record analysis
        - Accurate cause of death determination
        - Precise ICD-10 coding
        - Clinical reasoning documentation
        - Special circumstance consideration
        - Maternal mortality assessment
        
        ### Instructions:
        1. Upload a medical record text file
        2. Click analyze for detailed results
        """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Medical Record", type=['txt'])
    
    if uploaded_file and api_key:
        # Read and display the original text
        text_content = uploaded_file.read().decode()
        
        st.subheader("Medical Record")
        with st.expander("View Medical Record", expanded=True):
            st.text(text_content)
        
        # Analyze button
        if st.button("Analyze Medical Record"):
            with st.spinner("Performing comprehensive clinical analysis..."):
                try:
                    assistant = MedicalCodingAssistant(api_key)
                    result = assistant.analyze_medical_record(text_content)
                    
                    # Display results with typing effect
                    st.subheader("Clinical Analysis Results")
                    result_placeholder = st.empty()
                    display_typing_effect(result, result_placeholder)
                    
                    # Add download button for the analysis
                    st.download_button(
                        label="Download Clinical Report",
                        data=result,
                        file_name="clinical_analysis_report.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    elif not api_key:
        st.warning("Please enter your Mistral API key in the sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Clinical Documentation Analysis System - For Healthcare Professionals Only**
    
    This system provides expert-level analysis for:
    - Emergency and non-emergency cases
    - Chronic disease progression
    - Acute medical events
    - Maternal mortality cases
    - Complex medical scenarios
    """)

if __name__ == "__main__":
    main()
