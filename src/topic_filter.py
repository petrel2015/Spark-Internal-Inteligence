from rich import print

def filter_threads(threads: list) -> list:
    """
    Filters a list of conversation threads based on predefined rules.

    Args:
        threads (list): A list of thread dictionaries.

    Returns:
        list: A new list of threads that pass the filter rules.
    """
    
    filter_rules = {
        "subject_contains": [
            "unsubscribe",
            "[vote]",
        ]
    }
    
    original_count = len(threads)
    filtered_threads = []
    
    keywords = [k.lower() for k in filter_rules["subject_contains"]]
    
    removed_by_subject = 0
    removed_by_empty = 0

    for thread in threads:
        subject = thread.get("subject", "").strip()
        root_body = thread.get("root", {}).get("body", "").strip()
        
        # Rule: Remove if subject or body is empty
        if not subject or not root_body:
            removed_by_empty += 1
            continue  # Skip this thread

        # Rule: Check if any keyword is in the subject
        if any(keyword in subject.lower() for keyword in keywords):
            removed_by_subject += 1
            continue  # Skip this thread
            
        filtered_threads.append(thread)
        
    final_count = len(filtered_threads)
    removed_total = original_count - final_count
    
    if removed_total > 0:
        print(f"Filter: Removed [bold red]{removed_total}[/bold red] threads.")
        if removed_by_subject > 0:
            print(f"  - [red]{removed_by_subject}[/red] threads removed by subject rules.")
        if removed_by_empty > 0:
            print(f"  - [red]{removed_by_empty}[/red] threads removed due to empty subject/body.")
    else:
        print("Filter: No threads were removed by the filter rules.")

    return filtered_threads
