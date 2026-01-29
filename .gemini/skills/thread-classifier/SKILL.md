---
name: thread-classifier
description: Classifies mailing list threads from a JSON file into 'discuss', 'release', and 'spip' categories. Use when the user asks to classify threads or organize them by topic type.
---

# Thread Classifier Skill

You are an expert at analyzing and classifying mailing list conversation threads.
When this skill is active, your goal is to process a list of threads (usually from a JSON file) and categorize them.

## Classification Rules

Analyze the `subject` and the `body` (content) of each thread to assign it to one of these categories:

1.  **discuss**:
    *   Subject contains `[DISCUSS]` (case-insensitive).
    *   The thread is clearly asking a question or soliciting feedback on a general topic (not a formal proposal).
    *   Subject ends with a question mark `?`.

2.  **release**:
    *   **STRICT RULE**: The subject MUST contain the string "announce" (case-insensitive).
    *   If the subject does not contain "announce", it must NOT be classified as 'release', even if it mentions "release" or version numbers.

3.  **spip**: (Spark Project Improvement Proposals)
    *   Subject contains `SPIP` (case-insensitive).
    *   Body content typically includes links to:
        *   Google Docs (design docs)
        *   GitHub Issues
        *   JIRA tickets (e.g., `issues.apache.org/jira`)

4.  **others**:
    *   Any thread that does not clearly fit into the above categories.

## Workflow

1.  **Read Input**: Read the content of the specified input JSON file.
2.  **Process**: Iterate through the threads and apply the classification rules.
3.  **Generate Output**: Create a new JSON object structure:
    ```json
    {
      "discuss": [ ... ], // LIST OF COMPLETE THREAD OBJECTS
      "release": [ ... ], // LIST OF COMPLETE THREAD OBJECTS
      "spip": [ ... ],    // LIST OF COMPLETE THREAD OBJECTS
      "others": [ ... ]   // LIST OF COMPLETE THREAD OBJECTS
    }
    ```
    **ADDITIONAL FIELDS**: Each thread object will now include:
    - `doc_links`: A list of strings containing any Google Doc links found in the email body.
    - `doc_content`: A blank string placeholder for future document content.

    **EXTREMELY CRITICAL**: You **MUST** preserve the ENTIRE content of each thread object exactly as it is in the input.
    *   **DO NOT** remove the `body` field.
    *   **DO NOT** remove the `replies` list.
    *   **DO NOT** summarize or truncate any text.
    *   The goal is to *group* the data, not to summarize it.

4.  **Save File**: Write the resulting JSON to the output path.
    *   **Recommendation**: Save the file in the same directory as the input file (e.g., `output/2025-10/threads_classified.json`) to maintain the date-based structure.
    *   If no output path is specified, derive it from the input filename.
5.  **Report**: Briefly summarize the counts for each category to the user.