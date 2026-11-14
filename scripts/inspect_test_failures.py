import json

with open('results/advanced/test_results.json', encoding='utf-8') as f:
    test = json.load(f)

for case in test['cases']:
    if not case['passed']:
        print(f"=== {case['id']} ({case['category']}) ===")
        print("Question:", case['question'])
        print("Gold answer:", case['gold_answer'])
        print("Agent answer:", case['agent_answer'])
        print("Reason:", case['reason'])
        print()
