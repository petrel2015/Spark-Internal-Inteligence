import mailbox
import email
from email.header import decode_header
from dateutil.parser import parse as parse_date
import json
from rich.progress import track

def get_email_body(msg):
    """Extracts the text content from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or 'utf-8'
                try:
                    body = part.get_payload(decode=True).decode(charset, errors='replace')
                    break # Found the plain text part
                except (UnicodeDecodeError, AttributeError):
                    continue
    else:
        charset = msg.get_content_charset() or 'utf-8'
        try:
            body = msg.get_payload(decode=True).decode(charset, errors='replace')
        except (UnicodeDecodeError, AttributeError):
            body = ""
    return body.strip()

def decode_subject(header):
    """Decodes email subject header to a string."""
    if header is None:
        return ""
    decoded_parts = decode_header(header)
    subject = ""
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            subject += part.decode(charset or 'utf-8', errors='replace')
        else:
            subject += str(part)
    return subject

def simplify_message(msg, msg_id):
    """Converts an email.message.Message to a simplified dictionary."""
    try:
        date_str = msg.get("Date", "")
        dt = parse_date(date_str) if date_str else None
    except Exception:
        dt = None

    return {
        "id": msg_id,
        "from": msg.get("From", ""),
        "subject": decode_subject(msg.get("Subject", "")),
        "date": dt.isoformat() if dt else None,
        "body": get_email_body(msg),
        "in_reply_to": msg.get("In-Reply-To"),
        "references": msg.get("References"),
        "replies": []
    }

def parse_mbox_to_threads(mbox_path):
    """
    Parses an mbox file and organizes emails into conversation threads.

    Args:
        mbox_path (str): The path to the mbox file.

    Returns:
        list: A list of conversation threads, where each thread is a dictionary
              representing the root message with nested replies.
    """
    mbox_obj = mailbox.mbox(mbox_path)
    messages_by_id = {}
    
    # First pass: Read all messages and store them by Message-ID
    for msg in track(mbox_obj, description="Pass 1/2: Reading messages..."):
        msg_id = msg.get("Message-ID")
        if not msg_id:
            continue
        messages_by_id[msg_id] = simplify_message(msg, msg_id)

    # Second pass: Link messages into threads
    root_messages = []
    processed_ids = set()

    all_ids = list(messages_by_id.keys())
    for msg_id in track(all_ids, description="Pass 2/2: Building threads..."):
        if msg_id in processed_ids:
            continue

        message = messages_by_id[msg_id]
        parent_id = None
        
        # Try to find parent via References header first
        references = message.get("references")
        if references:
            # The direct parent is typically the last ID in the References list
            ref_ids = references.split()
            for i in range(len(ref_ids) - 1, -1, -1):
                if ref_ids[i] in messages_by_id:
                    parent_id = ref_ids[i]
                    break
        
        # If no parent found in References, use In-Reply-To
        if not parent_id:
            parent_id = message.get("in_reply_to")

        if parent_id and parent_id in messages_by_id:
            parent_message = messages_by_id[parent_id]
            parent_message["replies"].append(message)
            processed_ids.add(msg_id)
        else:
            # This is a root message
            root_messages.append(message)
            processed_ids.add(msg_id)

    # The above logic is simple but can miss nested replies if parents are processed after children.
    # A more robust approach is to build the full tree structure.
    
    # Reset and use a more robust tree-building logic
    messages = messages_by_id
    nodes = {mid: msg for mid, msg in messages.items()}
    
    # Clear previous replies lists
    for n in nodes.values():
        n['replies'] = []

    root_nodes = []
    for mid, node in track(nodes.items(), description="Pass 2/2: Re-building threads..."):
        parent_id = None
        references = node.get("references")
        if references:
            ref_ids = references.split()
            # Find the closest existing parent in the reference list
            for ref_id in reversed(ref_ids):
                if ref_id in nodes:
                    parent_id = ref_id
                    break
        
        if not parent_id:
            parent_id = node.get("in_reply_to")
            if parent_id and parent_id not in nodes:
                parent_id = None # Ignore if parent doesn't exist in our set

        if parent_id and parent_id in nodes:
            # It's a child, add it to its parent
            nodes[parent_id]['replies'].append(node)
        else:
            # It's a root message
            root_nodes.append(node)

    # Sort replies by date for chronological order
    def sort_threads_by_date(thread_list):
        for thread in thread_list:
            if thread['date']:
                thread['replies'].sort(key=lambda r: r['date'] or '1970-01-01T00:00:00')
            sort_threads_by_date(thread['replies'])

    sort_threads_by_date(root_nodes)
    
    # Create final thread objects
    final_threads = []
    for root in root_nodes:
        
        def count_messages(node):
            return 1 + sum(count_messages(r) for r in node['replies'])

        final_threads.append({
            "thread_id": root['id'],
            "subject": root['subject'],
            "start_date": root['date'],
            "message_count": count_messages(root),
            "root": root
        })
        
    # Sort threads by start date
    final_threads.sort(key=lambda t: t['start_date'] or '1970-01-01T00:00:00', reverse=True)

    return final_threads
