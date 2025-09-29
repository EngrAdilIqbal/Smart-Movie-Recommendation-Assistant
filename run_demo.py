# run_demo.py
import sys
from tasks import get_ai_response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_demo.py \"<your query here>\"")
        sys.exit(1)

    user_query = sys.argv[1]
    response = get_ai_response(user_query)

    print("\nUser:", user_query)
    print("Assistant:", response)
