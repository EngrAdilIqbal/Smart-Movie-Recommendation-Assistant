# Smart Movie Recommendation Assistant

An AI-inspired conversational assistant that recommends movies based on vague user inputs.  
The assistant identifies missing information (**slot filling**), asks clarifying questions (**dynamic question generation**), and retrieves the best matches from a knowledge base (**simplified RAG**).  

---

## Objective
When a user provides an ambiguous movie request (e.g., *"Recommend a sci-fi movie from the 90s"*), the assistant:
1. Extracts known details (**slot filling**).
2. Identifies missing slots.
3. Dynamically generates a clarifying question.
4. Retrieves the most relevant recommendations from a curated movie dataset.

---

## Project Structure
```

Smart-Movie-Recommendation-Assistant/
│── tasks.py           # Core logic (Prompt Design, Slot Filling, Retrieval, Dynamic Questioning)
│── run_demo.py        # CLI demo script
│── test_tasks.py      # Automated tests (pytest)
│── requirements.txt   # Dependencies
│── README.md          # Project documentation

````

---

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/Smart-Movie-Recommendation-Assistant.git
   cd Smart-Movie-Recommendation-Assistant
````

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate     # Mac/Linux
   venv\Scripts\activate        # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the demo from the command line:

```bash
python run_demo.py "Recommend a sci-fi movie from the 90s"
```

**Example:**

```
User: Recommend a sci-fi movie from the 90s
Assistant: Would you like something more light/fun or more serious/intense?
```

---

## Running Tests

Automated tests ensure that all components work as expected:

```bash
pytest -q
```

Expected output:

```
.....                                                                                                            [100%]
5 passed in 0.04s
```

---

## Features

* **Prompt Design** – Structured prompts for consistent assistant responses.
* **Slot Filling** – Extracts genre, mood, release era, director, language, runtime.
* **Simplified RAG** – Retrieves best-matching movies from a local knowledge base.
* **Dynamic Question Generation** – Asks targeted questions when information is missing.
* **Automated Tests** – Covers slot identification, retrieval, prompt building, and clarifying responses.

---

## Design Choices & Chain-of-Thought

* **Rule-Based Implementation**: To keep the task lightweight and deterministic, logic is implemented with handcrafted rules (not an actual LLM).
* **Slots**: Six key attributes are tracked – `genre`, `mood`, `release era`, `director`, `language`, `runtime`.
* **Retrieval**: A scoring system ranks movies in the database against filled slots.
* **Dynamic Questions**: If slots are missing, the system asks one clear, targeted question (e.g., mood, era, director).
* **Prompt Construction**: A dynamic system prompt simulates how an LLM would combine user input, filled slots, and retrieved candidates into a structured query.

This approach balances **explainability** (easy to understand logic) and **realism** (mimics how an AI movie recommender might work with RAG + prompting).

---

## Example Dialogues

**Input:**

```
python run_demo.py "Recommend a fun action movie"
```

**Output:**

```
User: Recommend a fun action movie
Assistant: Any preference for release era — classic, 1990s, 2000s, 2010s, or recent?
```

**Input:**

```
python run_demo.py "Any movies by Nolan?"
```

**Output:**

```
User: Any movies by Nolan?
Assistant: Do you prefer his superhero films or more mind-bending thrillers?
```

---

## Notes

* This is a **rule-based prototype**, designed to demonstrate **Prompt Design, Slot Filling, RAG, and Dynamic Question Generation**.
* No external APIs or actual LLMs are required.
