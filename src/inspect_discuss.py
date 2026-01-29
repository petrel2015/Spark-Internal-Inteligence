import json
import sys

def inspect_discuss(path):
    with open(path, 'r') as f:
        data = json.load(f)
    
    discuss_threads = data.get('discuss', [])
    print(f"Found {len(discuss_threads)} discuss threads.")
    
    for i, thread in enumerate(discuss_threads):
        print(f"\n=== Thread {i+1} ===")
        print(f"Subject: {thread.get('subject')}")
        root = thread.get('root', {})
        print(f"From: {root.get('from')}")
        print(f"Date: {root.get('date')}")
        print(f"Body:\n{root.get('body')}")
        
        replies = root.get('replies', [])
        print(f"\nReplies: {len(replies)}")
        for reply in replies:
            print(f"  -- Reply from: {reply.get('from')}")
            print(f"  Body: {reply.get('body')}")
            print("-" * 20)
        print("=" * 40)

if __name__ == "__main__":
    inspect_discuss(sys.argv[1])
