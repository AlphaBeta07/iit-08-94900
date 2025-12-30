import streamlit as st
from utils.chunker import chunk_text
from utils.embeddings import store_chunks, search_db
from utils.llm import ask_llm

from scrapers import (
    home, about_us, placements, workshops,
    internship, courses, admission,
    testimonials, infrastructure, contact_us
)

SCRAPER_MAP = {
    "Home": home,
    "About Us": about_us,
    "Placements": placements,
    "Workshops": workshops,
    "Internship": internship,
    "Courses": courses,
    "Admission": admission,
    "Testimonials": testimonials,
    "Infrastructure": infrastructure,
    "Contact Us": contact_us
}

st.set_page_config(layout="wide")
st.title("Sunbeam Institute AI Assistant")

section = st.pills(
    "Select Section",
    list(SCRAPER_MAP.keys())
)

question = st.text_input("Ask your question")

if st.button("Search"):
    scraper = SCRAPER_MAP[section]
    raw_text = scraper.scrape()

    chunks = chunk_text(raw_text)
    store_chunks(chunks, {"source": section})

    docs = search_db(question)
    answer = ask_llm("\n".join(docs), question)

    st.subheader("Answer")
    st.write(answer)
