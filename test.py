import streamlit as st
from st_audiorec import st_audiorec

# Audio recorder component
st.write("Click the microphone button to start recording:")
wav_audio_data = st_audiorec()

# Display audio player and download button if audio is recorded
if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')
    
    # Add download button for the recorded audio
    st.download_button(
        label="Download Audio",
        data=wav_audio_data,
        file_name=f"interview_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
        mime="audio/wav"
    )