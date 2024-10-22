import streamlit as st
import os
from mistralai import Mistral
import time

class MedicalCodingAssistant:
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
        
    def create_medical_prompt(self, symptoms, conditions, events):
        prompt = f"""
        As a medical coding expert, analyze the following patient information and determine the underlying cause of death:
        
        Patient Conditions and Symptoms:
        {', '.join(symptoms)}
        
        Existing Medical Conditions:
        {', '.join(conditions)}
        
        Events Leading to Death:
        {', '.join(events)}
        
        Please:
        1. Identify the underlying root cause of death
        2. Explain the causal chain leading to death
        3. Suggest the most appropriate ICD-10 code for the underlying cause
        4. Provide rationale for why this is the root cause rather than immediate cause
        
        Focus on identifying chronic conditions that initiated the chain of events leading to death.
        """
        return prompt

    def analyze_cause_of_death(self, symptoms, conditions, events):
        prompt = self.create_medical_prompt(symptoms, conditions, events)
        
        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical coding expert specializing in determining underlying causes of death and assigning appropriate ICD-10 codes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing cause of death: {str(e)}"

def extract_medical_info(text):
    """Extract medical information from the text file."""
    # Initialize lists to store extracted information
    symptoms = []
    conditions = []
    events = []
    
    # Convert text to lowercase for easier matching
    text_lower = text.lower()
    
    # Extract symptoms
    if "presenting symptoms" in text_lower:
        symptoms_section = text_lower.split("presenting symptoms")[1].split("\n\n")[0]
        symptoms = [s.strip("- ").strip() for s in symptoms_section.split("\n") if s.strip("- ").strip()]
    
    # Extract conditions
    if "medical history" in text_lower:
        conditions_section = text_lower.split("medical history")[1].split("\n\n")[0]
        conditions = [c.strip("- ").strip() for c in conditions_section.split("\n") if c.strip("- ").strip()]
    
    # Extract events
    if "course of events" in text_lower:
        events_section = text_lower.split("course of events")[1].split("\n\n")[0]
        events = [e.strip("- ").strip() for e in events_section.split("\n") if e.strip("- ").strip() and not e.lower().startswith("march")]
    
    return symptoms, conditions, events

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
        api_key = st.text_input("Enter Key", type="password")
        st.markdown("""
        ### Instructions:
        1. Upload a medical record text file
        2. Review the extracted information
        3. Click analyze to get results
        """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Medical Record", type=['txt'])
    
    if uploaded_file and api_key:
        # Read and display the original text
        text_content = uploaded_file.read().decode()
        with st.expander("View Original Medical Record"):
            st.text(text_content)
        
        # Extract information
        symptoms, conditions, events = extract_medical_info(text_content)
        
        # Display extracted information in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Extracted Symptoms")
            symptoms_edit = st.multiselect("Edit Symptoms", symptoms, default=symptoms)
            
        with col2:
            st.subheader("Extracted Conditions")
            conditions_edit = st.multiselect("Edit Conditions", conditions, default=conditions)
            
        with col3:
            st.subheader("Extracted Events")
            events_edit = st.multiselect("Edit Events", events, default=events)
        
        # Create a placeholder for results
        result_container = st.empty()
        
        # Analyze button
        if st.button("Analyze Cause of Death"):
            with st.spinner("Analyzing medical record..."):
                try:
                    assistant = MedicalCodingAssistant(api_key)
                    result = assistant.analyze_cause_of_death(
                        symptoms=symptoms_edit,
                        conditions=conditions_edit,
                        events=events_edit
                    )
                    
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