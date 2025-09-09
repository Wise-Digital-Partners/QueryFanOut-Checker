import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Set up the app page
st.set_page_config(
    page_title="Gemini Query Fan-Out Analyzer",
    layout="wide",
)

# --- App UI and Logic ---

st.title("Gemini Query Fan-Out Analyzer")
st.markdown("This app analyzes a URL's content to predict potential Google AI Mode query fan-out and identify content gaps.")

api_key = st.text_input("Enter your Gemini API Key", type="password")
url = st.text_input("Enter the URL to analyze")

# Button to trigger the analysis
if st.button("Analyze URL"):
    if not api_key:
        st.error("Please enter your Gemini API key.")
    elif not url:
        st.error("Please enter a URL.")
    else:
        try:
            with st.spinner("Fetching and analyzing content..."):
                # 1. Fetch the URL content
                st.info("Step 1: Fetching URL content...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 2. Extract semantic chunks
                st.info("Step 2: Chunking content...")

                def extract_semantic_chunks(soup):
                    chunks = []
                    
                    # Extract title and main heading
                    title = soup.title.string if soup.title else ''
                    h1 = soup.find('h1')?.text.strip() if soup.find('h1') else ''
                    if title or h1:
                        chunks.append({
                            'type': 'primary_topic',
                            'content': f"{title} {h1}".strip()
                        })

                    # Extract headings and their content
                    headings = soup.find_all(['h2', 'h3'])
                    for heading in headings:
                        content = heading.get_text().strip()
                        sibling = heading.find_next_sibling()
                        section_content = ''

                        while sibling and sibling.name not in ['h1', 'h2', 'h3']:
                            if sibling.get_text().strip():
                                section_content += ' ' + sibling.get_text().strip()
                            sibling = sibling.find_next_sibling()
                        
                        if section_content.strip():
                            chunks.append({
                                'type': 'section',
                                'heading': content,
                                'content': section_content.strip()[:500]
                            })
                    
                    # Extract key lists and FAQs
                    for i, list_element in enumerate(soup.find_all(['ul', 'ol'])):
                        if i < 5 and len(list_element.find_all('li')) > 2:
                            list_items = [li.get_text().strip() for li in list_element.find_all('li')]
                            chunks.append({
                                'type': 'list',
                                'content': ' | '.join(list_items)[:300]
                            })
                    
                    # Extract schema.org data
                    for script in soup.find_all('script', type='application/ld+json'):
                        try:
                            data = json.loads(script.string)
                            if '@type' in data:
                                chunks.append({
                                    'type': 'structured_data',
                                    'content': f"Type: {data['@type']}, {json.dumps(data)[:200]}"
                                })
                        except json.JSONDecodeError:
                            continue
                            
                    return chunks

                chunks = extract_semantic_chunks(soup)
                
                # 3. Create prompt and call Gemini API
                st.info("Step 3: Sending prompt to Gemini...")
                prompt = f"""You are analyzing a webpage for Google's AI Mode query fan-out potential. Google's AI Mode decomposes user queries into multiple sub-queries to synthesize comprehensive answers.

URL: {url}

SEMANTIC CHUNKS FROM PAGE:
{json.dumps(chunks, indent=2)}

Based on this content, perform the following analysis:

1. IDENTIFY PRIMARY TOPIC: What is the main ontological entity or topic of this page?

2. PREDICT FAN-OUT QUERIES: Generate 8–10 likely sub-queries that Google's AI might create when a user asks about this topic. Consider:
    - Related queries (broader context)
    - Implicit queries (unstated user needs)
    - Comparative queries (alternatives, comparisons)
    - Procedural queries (how-to aspects)
    - Contextual refinements (budget, size, location specifics)
    - Potential Google classifications (Google’s best-in-class information systems, and it’s built right into Search. Fresh, real-time sources like the Knowledge Graph, info about the real world, and shopping data for billions of products)

3. SEMANTIC COVERAGE SCORE: For each predicted query, assess if the page content provides information to answer it (Yes/Partial/No).

4. FOLLOW-UP QUESTION POTENTIAL: What follow-up questions would users likely ask after reading this content?

OUTPUT FORMAT:
PRIMARY TOPIC: [entity name]

FAN-OUT QUERIES:
- [Query 1] - Coverage: [Yes/Partial/No]
- [Query 2] - Coverage: [Yes/Partial/No]
...

FOLLOW-UP POTENTIAL:
- [Follow-up question 1]
- [Follow-up question 2]
...

COVERAGE SCORE: [X/10 queries covered]
RECOMMENDATIONS: [Specific content gaps to fill]"""

                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-preview-05-20:generateContent?key={api_key}"
                request_data = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "topK": 20,
                        "topP": 0.9,
                        "maxOutputTokens": 2048
                    }
                }
                gemini_response = requests.post(gemini_url, json=request_data)
                gemini_response.raise_for_status()
                analysis_text = gemini_response.json()['candidates'][0]['content']['parts'][0]['text']
                
                # 4. Display the results
                st.subheader("Analysis Results")
                st.markdown(analysis_text)
                
                st.subheader("Content Chunking Summary")
                st.info(f"""
                - Primary Topic Chunks: {len([c for c in chunks if c['type'] == 'primary_topic'])}
                - Section Chunks: {len([c for c in chunks if c['type'] == 'section'])}
                - List/FAQ Chunks: {len([c for c in chunks if c['type'] == 'list'])}
                - Structured Data: {'Yes' if any(c['type'] == 'structured_data' for c in chunks) else 'No'}
                - Total Semantic Chunks: {len(chunks)}
                """)
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
