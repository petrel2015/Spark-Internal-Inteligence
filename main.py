import click
import json
from pathlib import Path
from src.mbox_parser import parse_mbox_to_threads
from src.topic_filter import filter_threads

@click.command()
@click.option('--mbox', 'mbox_path', 
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), 
              required=True, 
              help='Path to the mbox file.')
@click.option('--output-dir', 'output_base', 
              type=click.Path(file_okay=False, dir_okay=True, writable=True), 
              default='output',
              help='Base directory for output files.')
def main(mbox_path, output_base):
    """
    A command-line tool to parse an mbox file, filter conversation
    threads, and save the output as a JSON file in a date-based directory.
    """
    click.echo(f"Processing mbox file: {mbox_path}")
    
    # --- 1. Parsing ---
    threads = parse_mbox_to_threads(mbox_path)
    click.echo(f"Found {len(threads)} conversation threads.")

    if not threads:
        click.echo("No threads found. Exiting.")
        return

    # Extract date from the first thread to determine folder structure
    # Format: YYYY-MM
    try:
        first_date = threads[0].get('start_date')
        # Simple string slicing for ISO format (YYYY-MM-DD...)
        # e.g., "2025-10-31T14:29:51-07:00" -> "2025-10"
        date_folder = first_date[:7] 
    except Exception:
        date_folder = "unknown_date"

    target_dir = Path(output_base) / date_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    # Save full threads
    full_output_path = target_dir / "step1_threads.json"
    with open(full_output_path, 'w', encoding='utf-8') as f:
        json.dump(threads, f, indent=2, ensure_ascii=False)
    click.echo(f"Saved full threads to: {full_output_path}")

    # --- 2. Filtering ---
    filtered_threads = filter_threads(threads)
    
    # --- 3. Saving Output ---
    filtered_output_path = target_dir / "step2_threads_filtered.json"
    
    with open(filtered_output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_threads, f, indent=2, ensure_ascii=False)
        
    click.echo(click.style(f"Successfully saved filtered JSON to: {filtered_output_path}", fg='green'))

if __name__ == '__main__':
    main()