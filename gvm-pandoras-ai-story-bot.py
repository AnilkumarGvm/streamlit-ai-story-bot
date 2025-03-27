from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import streamlit as st
from supabase import create_client, Client

# Initialize FastAPI app
app = FastAPI()

# OpenAI API key setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define request models
class StoryRequest(BaseModel):
    story_origin: str
    use_case: str
    time_frame: str
    story_focus: List[str]
    story_type: str
    details: dict

class StoryEnhancementRequest(BaseModel):
    story_text: str
    enhancement_type: str

class StoryPolishRequest(BaseModel):
    story_text: str
    polish_options: List[str]

class StoryUpdateRequest(BaseModel):
    story_id: int
    story_text: str

@app.post("/generate_story")
def generate_story(request: StoryRequest):
    try:
        prompt = f"Create a compelling story based on the following details: {request.dict()}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        story_text = response["choices"][0]["message"]["content"]
        
        data, count = supabase.table("stories").insert({
            "story_origin": request.story_origin,
            "use_case": request.use_case,
            "time_frame": request.time_frame,
            "story_focus": request.story_focus,
            "story_type": request.story_type,
            "details": request.details,
            "story_text": story_text
        }).execute()
        
        return {"story": story_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_stories")
def get_stories():
    try:
        data, count = supabase.table("stories").select("*").execute()
        return {"stories": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update_story")
def update_story(request: StoryUpdateRequest):
    try:
        data, count = supabase.table("stories").update({"story_text": request.story_text}).eq("id", request.story_id).execute()
        
        return {"message": "Story updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhance_story")
def enhance_story(request: StoryEnhancementRequest):
    try:
        prompt = f"Refine the following story using the {request.enhancement_type} technique: {request.story_text}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"enhanced_story": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/polish_story")
def polish_story(request: StoryPolishRequest):
    try:
        prompt = f"Improve the following story by adding {', '.join(request.polish_options)}: {request.story_text}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"polished_story": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Welcome to Gvm Pandora's AI Story Bot API!"}

# Streamlit UI
st.title("Gvm Pandora's AI Story Bot")
st.header("Create Your Story")

story_origin = st.selectbox("Choose Story Origin", ["Personal Anecdote", "Adapt a Well-Known Tale"])
story_use_case = st.selectbox("Define the Use Case", ["Profile Story", "Social Media Content", "Marketing Story"])
time_frame = st.selectbox("Select Story Time Frame", ["Childhood", "Mid-Career", "Recent Experiences"])
story_focus = st.multiselect("Select Leadership Qualities", ["Generosity", "Integrity", "Loyalty", "Determination"])
story_type = st.selectbox("Select Story Type", ["Founding Story", "Vision Story", "Strategy Story"])
story_details = st.text_area("Describe Key Story Details")

if st.button("Generate Story"):
    request_data = StoryRequest(
        story_origin=story_origin,
        use_case=story_use_case,
        time_frame=time_frame,
        story_focus=story_focus,
        story_type=story_type,
        details={"content": story_details}
    )
    response = generate_story(request_data)
    st.subheader("Generated Story")
    st.write(response["story"])

# Tier 2: Story Enhancement
st.header("Enhance Your Story")
st.write("Congratulations on completing your first draft! Choose an enhancement option:")
st.button("Book a one-on-one session with expert storytellers")
st.selectbox("Choose storytelling technique", ["The Story Hanger", "The Story Spine", "Hero's Journey", "Nested Loops", "Cliffhanger"])

# Tier 3: Story Polishing
st.header("Polish Your Story")
st.write("Refine your narrative with creative enhancements:")
st.multiselect("Choose enhancement options", ["Impactful Quotes", "Poems", "Similes", "Comparisons", "AI-generated descriptions"])
st.button("Polish Story")
