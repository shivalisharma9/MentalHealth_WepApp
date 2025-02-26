import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Helper functions for type conversion and validation
def convert_binary_response(value):
    """Convert Yes/No responses to float"""
    if isinstance(value, str):
        return float(1) if value.lower() == 'yes' else float(0)
    return float(0)

def convert_numeric(value, default=0.0):
    """Convert any value to float safely"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return float(default)

def encode_categorical(value, categories, prefix=''):
    """Create one-hot encoding for categorical values"""
    encoding = {}
    for category in categories:
        column_name = f"{prefix}_{category}" if prefix else category
        encoding[column_name] = float(1) if value == category else float(0)
    return encoding

# Load models with error handling
try:
    stress_model = pickle.load(open('stress_model.pkl', 'rb'))
    depression_model = pickle.load(open('depression_model.pkl', 'rb'))
    burnout_model = pickle.load(open('burnout_model.pkl', 'rb'))
    wellness_model = pickle.load(open('wellness_model.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
except FileNotFoundError as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

st.title("Mental Health Wellness Predictor")
st.write("Fill in the details below to get predictions.")

def get_user_input():
    with st.form("prediction_form"):
        try:
            # Common inputs
            age = st.number_input("Age", min_value=10, max_value=100, value=25)
            gender = st.selectbox("Gender", ['Male', 'Female', 'Other'])
            sleep_hours = st.slider("Sleep Hours per Night", 0, 12, 7)
            
            # Lifestyle Factors
            st.subheader("Lifestyle Factors")
            work_hours = st.slider("Work Hours per Day", 0, 16, 8)
            exercise_freq = st.slider("Exercise Frequency (days per week)", 0, 7, 3)
            screen_time = st.slider("Screen Time (hours per day)", 0, 12, 4)
            social_activity = st.slider("Social Activity Level (0-10)", 0, 10, 5)
            diet_quality = st.slider("How healthy is your diet? (0-10)", 0, 10, 5)

            # Mental Health History
            st.subheader("Mental Health History")
            family_history = st.selectbox("Family History of Mental Health Issues", ['No', 'Yes'])
            sleep_quality = st.slider("Sleep Quality (0-10)", 0, 10, 5)
            stress_level_dep = st.slider("Current Stress Level (0-10)", 0, 10, 5)
            social_support = st.slider("Social Support Level (0-10)", 0, 10, 5)
            physical_activity = st.slider("Physical Activity Level (0-10)", 0, 10, 5)
            substance_use = st.selectbox("Substance Use (Alcohol, Drugs, etc.)", ['No', 'Yes'])

            # Work-Related Factors
            st.subheader("Work-Related Factors")
            overtime = st.slider("Overtime Hours per Week", 0, 20, 0)
            work_satisfaction = st.slider("Work Satisfaction (0-10)", 0, 10, 5)
            mood_swings = st.slider("Mood Swings Frequency (0-10)", 0, 10, 5)
            stress_level_burn = st.slider("Stress Level for Burnout (0-10)", 0, 10, 5)

            # Wellness Assessment
            st.subheader("Wellness Assessment")
            stress_level_well = st.slider("Current Stress Level for Wellness (0-5)", 0, 5, 2)

            submitted = st.form_submit_button("Predict Mental Health Status")

            if submitted:
                # Convert all categorical and binary inputs first
                gender_encoded = encode_categorical(gender, ['Male', 'Other'], 'gender')
                family_history_num = convert_binary_response(family_history)
                substance_use_num = convert_binary_response(substance_use)

                # Prepare stress input with type safety
                stress_input = pd.DataFrame({
                    'age': [convert_numeric(age)],
                    'sleep_hours': [convert_numeric(sleep_hours)],
                    'work_hours': [convert_numeric(work_hours)],
                    'exercise_freq': [convert_numeric(exercise_freq)],
                    'screen_time': [convert_numeric(screen_time)],
                    'social_activity': [convert_numeric(social_activity)],
                    'diet_quality': [convert_numeric(diet_quality)],
                    'gender_Male': [gender_encoded['gender_Male']],
                    'gender_Other': [gender_encoded['gender_Other']]
                })

                # Prepare depression input with type safety
                depression_input = pd.DataFrame({
                    'age': [convert_numeric(age)],
                    'sleep_quality': [convert_numeric(sleep_quality)],
                    'stress_level': [convert_numeric(stress_level_dep)],
                    'social_support': [convert_numeric(social_support)],
                    'physical_activity': [convert_numeric(physical_activity)],
                    'gender_Male': [gender_encoded['gender_Male']],
                    'gender_Other': [gender_encoded['gender_Other']],
                    'family_history_Yes': [family_history_num],
                    'substance_use_Yes': [substance_use_num]
                })

                # Prepare burnout input with type safety
                burnout_input = pd.DataFrame({
                    'age': [convert_numeric(age)],
                    'work_hours': [convert_numeric(work_hours)],
                    'overtime': [convert_numeric(overtime)],
                    'work_satisfaction': [convert_numeric(work_satisfaction)],
                    'stress_level': [convert_numeric(stress_level_burn)],
                    'sleep_hours': [convert_numeric(sleep_hours)],
                    'mood_swings': [convert_numeric(mood_swings)],
                    'gender_Male': [gender_encoded['gender_Male']],
                    'gender_Other': [gender_encoded['gender_Other']]
                })

                try:
                    # Make predictions with type safety
                    stress_prediction = convert_numeric(stress_model.predict(stress_input)[0])
                    depression_prediction = convert_numeric(depression_model.predict(depression_input)[0])
                    burnout_prediction = convert_numeric(burnout_model.predict(burnout_input)[0])

                    # Prepare wellness input with type safety
                    wellness_input = pd.DataFrame({
                        'age': [convert_numeric(age)],
                        'stress_level': [convert_numeric(stress_level_well)],
                        'gender_Male': [gender_encoded['gender_Male']],
                        'gender_Other': [gender_encoded['gender_Other']],
                        'burnout_Yes': [convert_numeric(burnout_prediction)],
                        'depression_risk_Yes': [convert_numeric(depression_prediction)]
                    })

                    # Scale wellness input and get predictions
                    wellness_input_scaled = scaler.transform(wellness_input)
                    wellness_predictions = wellness_model.predict(wellness_input_scaled)[0]
                    
                    # Convert numpy array to list if needed
                    if isinstance(wellness_predictions, np.ndarray):
                        wellness_predictions = wellness_predictions.tolist()

                    # Display results with corrected scales
                    st.subheader("Predictions:")
                    st.write(f"**Stress Level:** {stress_prediction:.1f}/5")  # Changed to /5
                    st.write(f"**Depression Risk:** {'Yes' if depression_prediction >= 0.5 else 'No'}")  # Changed to Yes/No
                    st.write(f"**Burnout Status:** {'Yes' if burnout_prediction >= 0.5 else 'No'}")
                    
                    st.write("\n**Recommended Wellness Activities (1-5 scale):**")
                    wellness_activities = ['Meditation', 'Therapy', 'Music Therapy', 'Relaxation Techniques']
                    
                    # Handle wellness predictions more carefully
                    if isinstance(wellness_predictions, (list, np.ndarray)):
                        for activity, score in zip(wellness_activities, wellness_predictions):
                            score = convert_numeric(score, 1.0)
                            score = max(1.0, min(5.0, score))
                            st.write(f"- {activity}: {score:.1f}/5")
                    else:
                        # If single prediction, distribute it across activities
                        score = convert_numeric(wellness_predictions, 1.0)
                        score = max(1.0, min(5.0, score))
                        for activity in wellness_activities:
                            st.write(f"- {activity}: {score:.1f}/5")

                except Exception as e:
                    st.error(f"Error making predictions: {str(e)}")
                    st.error("Debug info:")
                    st.error(f"Wellness predictions type: {type(wellness_predictions)}")
                    if isinstance(wellness_predictions, np.ndarray):
                        st.error(f"Wellness predictions shape: {wellness_predictions.shape}")
                    st.error("Please check all input values and try again.")

        except Exception as e:
            st.error(f"Error processing inputs: {str(e)}")

# Main app execution
get_user_input()