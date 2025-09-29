from typing import Tuple, List, Dict
import re

# --- Provided Data & Initial Setup ---

MOVIE_DB = [
    {"title": "Inception", "genre": "Sci-Fi/Action", "release_year": 2010, "director": "Christopher Nolan", "language": "English", "keywords": ["dream", "thriller", "mind-bending", "heist"]},
    {"title": "Parasite", "genre": "Drama/Thriller", "release_year": 2019, "director": "Bong Joon Ho", "language": "Korean", "keywords": ["family", "social commentary", "dark comedy", "serious"]},
    {"title": "The Avengers", "genre": "Sci-Fi/Action", "release_year": 2012, "director": "Joss Whedon", "language": "English", "keywords": ["superhero", "Marvel", "team-up", "blockbuster"]},
    {"title": "La La Land", "genre": "Musical/Romance", "release_year": 2016, "director": "Damien Chazelle", "language": "English", "keywords": ["music", "love", "dream", "emotional"]},
    {"title": "The Dark Knight", "genre": "Action/Drama", "release_year": 2008, "director": "Christopher Nolan", "language": "English", "keywords": ["superhero", "DC", "philosophical", "serious", "gritty"]},
]

# --- Task 1: System Prompt Design ---
SYSTEM_PROMPT = """
You are a friendly and knowledgeable movie expert. You ask smart, concise clarifying questions that help users get a tailored movie suggestion.
Constraints:
- Always ask at least one clarifying question before recommending a final movie title.
- Keep tone warm, brief and professional.
- When possible, prefer single, specific clarifying questions that are easy to answer (yes/no or short phrases).
"""

# --- Task 3: Few-Shot Examples ---
FEW_SHOT_EXAMPLES = [
    {
     "input": "I liked the new Nolan movie.",
     "output": "Christopher Nolan's films are fantastic! To help me narrow it down, are you in the mood for a more thoughtful thriller (e.g., Inception) or a darker, gritty superhero drama (e.g., The Dark Knight)?"
    },
    {
     "input": "Something romantic but upbeat.",
     "output": "Nice — do you prefer musicals (songs integrated in story) or romantic comedies (lighthearted, modern)? A one-word answer like 'musical' or 'rom-com' is perfect."
    },
]

# --- Task 2: Slot Definition, Retrieval, and Identification ---

# Define at least 5 slots essential for a good recommendation
DEFINED_SLOTS = {
    "genre": "The genre of the movie (e.g., Action, Drama, Romance, Sci-Fi, Comedy).",
    "mood": "The desired mood for the movie (e.g., fun, dark, emotional, thought-provoking).",
    "release_era": "Approximate release era (e.g., 1990s, 2000s, 2010s, modern).",
    "director": "Prefer a film by a specific director.",
    "language": "Preferred language of the movie (e.g., English, Korean).",
    # optional slot:
    "runtime": "Preferred runtime (short < 100 min, medium 100-140, long > 140)."
}

# Helper: normalize small words and synonyms
GENRE_SYNONYMS = {
    "sci-fi": "Sci-Fi",
    "science fiction": "Sci-Fi",
    "science-fiction": "Sci-Fi",
    "action": "Action",
    "drama": "Drama",
    "romance": "Romance",
    "musical": "Musical",
    "comedy": "Comedy",
    "thriller": "Thriller",
    "superhero": "Sci-Fi/Action",
}

MOOD_KEYWORDS = {
    "fun": ["fun", "light", "funny", "laugh", "comedic", "entertaining"],
    "serious": ["serious", "dark", "grim", "heavy", "thoughtful", "dramatic"],
    "emotional": ["emotional", "touching", "tear", "sad", "romantic"],
    "mind-bending": ["mind-bending", "twisty", "puzzling", "complex"],
    "blockbuster": ["blockbuster", "epic", "big", "spectacle"],
}

ERA_KEYWORDS = {
    "1990s": range(1990, 2000),
    "2000s": range(2000, 2010),
    "2010s": range(2010, 2020),
    "2020s": range(2020, 2030),
    "classic": range(1900, 1990),
}

def identify_slots(user_input: str) -> Tuple[Dict[str,str], List[str]]:
    """
    Identifies filled and missing slots from user input using simple heuristics:
    - Keyword matching for genres, moods, director names (simple check), era (year or decades), language.
    Returns (filled_slots, missing_slots_list).
    """
    text = user_input.lower()
    filled = {}

    # Genre detection (search for known words)
    for key, val in GENRE_SYNONYMS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            # map to a canonical genre (we choose main label)
            filled['genre'] = val
            break

    # Mood detection
    for mood, kw_list in MOOD_KEYWORDS.items():
        for kw in kw_list:
            if kw in text:
                filled['mood'] = mood
                break
        if 'mood' in filled:
            break

    # Director detection: look for proper names existing in DB
    for movie in MOVIE_DB:
        director_lower = movie['director'].lower()
        # check if last name or full name appears
        last_name = director_lower.split()[-1]
        if last_name in text or director_lower in text:
            filled['director'] = movie['director']
            break

    # Release era detection: look for explicit decade or year
    # Year (4-digit)
    years = re.findall(r'\b(19|20)\d{2}\b', user_input)
    if years:
        # take first full match
        year_match = re.search(r'\b(19|20)\d{2}\b', user_input)
        if year_match:
            y = int(year_match.group(0))
            filled['release_era'] = str(y)
    else:
        # decades keywords
        for era in ERA_KEYWORDS:
            if era.replace('s','') in text or era in text:
                filled['release_era'] = era
                break

    # Language detection
    for movie in MOVIE_DB:
        lang = movie.get('language', '').lower()
        if lang and lang in text:
            filled['language'] = movie['language']
            break
    # common language words
    if 'korean' in text:
        filled['language'] = 'Korean'
    if 'english' in text:
        filled['language'] = 'English'

    # runtime preference
    if re.search(r'\b(short|under ?1 ?hr|< ?60|min)\b', text):
        filled['runtime'] = 'short'
    if re.search(r'\b(long|epic|over ?2 ?hr|> ?120|min)\b', text):
        filled['runtime'] = 'long'

    # Compose missing slots
    missing = [s for s in DEFINED_SLOTS.keys() if s not in filled]

    return filled, missing


def _score_movie_against_slots(movie: dict, filled_slots: dict) -> int:
    """
    Very simple scoring:
    +3 for genre match (substring)
    +4 for director exact
    +2 for language match
    +1 per keyword match (from mood or user-specified words)
    +2 for release_era match (if year or era string matches)
    """
    score = 0
    # genre
    if 'genre' in filled_slots:
        # match if the filled slot appears within movie['genre'] (case-insensitive)
        if filled_slots['genre'].lower() in movie['genre'].lower():
            score += 3
    # director
    if 'director' in filled_slots:
        if filled_slots['director'].lower() == movie['director'].lower():
            score += 4
    # language
    if 'language' in filled_slots:
        if movie.get('language', '').lower() == filled_slots['language'].lower():
            score += 2
    # release_era (could be year or decade string)
    if 'release_era' in filled_slots:
        val = filled_slots['release_era']
        try:
            # if it's a numeric year
            y = int(val)
            if movie.get('release_year') == y:
                score += 3
            else:
                # near decades: +2 for same decade
                if movie.get('release_year') // 10 == y // 10:
                    score += 2
        except ValueError:
            # treat as era label like "2010s"
            if val.endswith('s'):
                decade = int(val[:4]) if len(val) >= 4 and val[:4].isdigit() else None
                if decade and movie.get('release_year') in ERA_KEYWORDS.get(val, []):
                    score += 2
    # mood -> keywords
    if 'mood' in filled_slots:
        mood = filled_slots['mood']
        keywords = movie.get('keywords', [])
        # check if any mood keyword appears in movie keywords or title
        for kw in keywords:
            if mood in kw.lower() or any(m in kw.lower() for m in mood.split()):
                score += 1
        # also if mood word in title
        if mood in movie['title'].lower():
            score += 1

    # simple keyword matching against user provided textual preferences (if present)
    # (not implemented here as we don't carry raw user text to retrieve function)
    return score


def retrieve_candidates(filled_slots: dict, top_k: int = 3) -> List[dict]:
    """
    Retrieves and ranks candidate movies from MOVIE_DB by scoring.
    Returns top_k movies (sorted by score desc).
    If no filled slots or no matches, return a small diverse fallback.
    """
    if not filled_slots:
        # return a balanced fallback list (popular/varied)
        return MOVIE_DB[:top_k]

    scored = []
    for movie in MOVIE_DB:
        score = _score_movie_against_slots(movie, filled_slots)
        # small fallback: movies that have any keyword overlap with any filled slot text
        scored.append((score, movie))

    # sort by score descending, then by release_year descending
    scored_sorted = sorted(scored, key=lambda x: (x[0], x[1].get('release_year', 0)), reverse=True)
    top = [m for s, m in scored_sorted if s > 0][:top_k]

    # If we didn't find any scored > 0, provide a small fallback sample
    if not top:
        # include top_k most recent
        top = sorted(MOVIE_DB, key=lambda m: m.get('release_year', 0), reverse=True)[:top_k]
    return top


# --- Task 3: Dynamic Prompt Generation ---

def _format_candidates_for_prompt(candidates: List[dict]) -> str:
    if not candidates:
        return "No strong candidates found in the local DB."
    lines = []
    for c in candidates:
        lines.append(f"- {c['title']} ({c.get('release_year')}) — genre: {c.get('genre')}, director: {c.get('director')}")
    return "\n".join(lines)


def build_dynamic_prompt(user_input: str, filled_slots: dict, candidates: List[dict]) -> str:
    """
    Build a dynamic prompt for a downstream LLM. Includes:
    - system prompt
    - few-shot examples
    - user input
    - filled slots
    - retrieved candidates (R)
    - instruction to ask one specific clarifying question
    """
    prompt_parts = []
    prompt_parts.append(SYSTEM_PROMPT.strip())
    prompt_parts.append("\nFEW-SHOT EXAMPLES:")
    for ex in FEW_SHOT_EXAMPLES:
        prompt_parts.append(f"User: {ex['input']}\nAssistant: {ex['output']}\n")

    prompt_parts.append("USER REQUEST:")
    prompt_parts.append(user_input.strip())

    prompt_parts.append("IDENTIFIED SLOTS:")
    if filled_slots:
        for k, v in filled_slots.items():
            prompt_parts.append(f"- {k}: {v}")
    else:
        prompt_parts.append("- (none identified)")

    prompt_parts.append("RETRIEVED CANDIDATES (R):")
    prompt_parts.append(_format_candidates_for_prompt(candidates))

    prompt_parts.append("\nINSTRUCTION (A): You are the assistant. Based on the information above, ask exactly one concise, specific clarifying question that will most improve the recommendation. The question should be easy to answer (one or two words ideally). Do NOT recommend a movie yet. If all slots are already thoroughly filled, ask for a final small confirmation (e.g., 'Do you prefer something gritty or light?').")

    return "\n\n".join(prompt_parts)


# --- Main Logic ---
def get_ai_response(user_input: str) -> str:
    """
    Takes user input and returns the AI's next response (a clarifying question).
    Flow:
    1. Identify slots
    2. Retrieve candidates
    3. Build dynamic prompt (for hypothetical LLM)
    4. Generate simulated clarifying question (rule-based)
    Notes: Must ask at least one clarifying question before recommending a movie.
    """
    filled_slots, missing_slots = identify_slots(user_input)
    candidates = retrieve_candidates(filled_slots)

    # Build dynamic prompt (not sent to real LLM in this assignment)
    final_prompt = build_dynamic_prompt(user_input, filled_slots, candidates)
    # (For debugging) you could print(final_prompt) or log it.

    # If there are missing slots, choose the highest-priority one to ask about.
    # Priority order defined here:
    priority = ["genre", "mood", "release_era", "director", "language", "runtime"]

    if missing_slots:
        # pick first missing by priority
        for p in priority:
            if p in missing_slots:
                slot_to_ask = p
                break
        # Craft a contextual question tailored to the slot
        if slot_to_ask == "genre":
            return "Sure — what genre are you in the mood for? (e.g., Action, Drama, Comedy, Romance)"
        if slot_to_ask == "mood":
            return "Would you like something more light/fun or more serious/intense?"
        if slot_to_ask == "release_era":
            return "Any preference for release era — classic, 1990s, 2000s, 2010s, or recent?"
        if slot_to_ask == "director":
            return "Do you prefer a specific director or filmmaker? If yes, name them (e.g., Nolan)."
        if slot_to_ask == "language":
            return "Do you have a preferred language? (e.g., English, Korean, Spanish)"
        if slot_to_ask == "runtime":
            return "Do you prefer a short (<100 min), medium (100-140 min), or long (>140 min) movie?"

    # No missing slots: still ask a single confirmation question before recommending (per constraints)
    # Use candidates to ask a useful distinguishing question
    if filled_slots:
        # If genre is action, ask gritty vs blockbuster
        if filled_slots.get("genre") and "Action" in filled_slots.get("genre"):
            return "Great — for action, do you want something gritty/realistic or a fun blockbuster?"
        # If director specified, ask whether they want similar tone or same director
        if 'director' in filled_slots:
            return f"Do you want something by {filled_slots['director']} specifically, or films with a similar tone?"
        # If mood specified, confirm intensity
        if 'mood' in filled_slots:
            return f"You mentioned '{filled_slots['mood']}'. Would you prefer a milder or a stronger version of that mood?"
        # fallback confirmation
        return "Thanks — one quick check: do you prefer newer releases or are older films okay?"
    # If absolutely nothing identified, ask a starter question
    return "Got it — to start, what type of movie would you like (genre, mood, or director)?"
