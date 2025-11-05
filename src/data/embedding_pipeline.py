import os
import asyncio
from src.data.parser import parse_discord_export
from src.memory.service import memory_service
from src.llm.service import llm_service
from src.utils.logger import log
from colorama import Fore
import hashlib

async def process_file(file_path):
    """
    Process a single Discord export file: parse, embed, and store.

    Args:
        file_path: Path to the .txt file
    """
    log(f"\n{'='*60}", Fore.CYAN)
    log(f"Processing: {file_path}", Fore.CYAN)
    log(f"{'='*60}", Fore.CYAN)

    # Parse messages
    messages = parse_discord_export(file_path)
    log(f"Extracted {len(messages)} messages", Fore.GREEN)

    if not messages:
        log("No messages to process", Fore.YELLOW)
        return

    # Generate embeddings and store in ChromaDB
    log("Generating embeddings and storing in ChromaDB...", Fore.CYAN)
    for author, message in messages:
        await memory_service.add_memory(author, message)

    log(f"✓ Successfully processed {file_path}", Fore.GREEN)


async def process_all_files(folder_path='attached_assets'):
    """
    Process all Discord export files in a folder.

    Args:
        folder_path: Path to folder containing .txt files
    """
    from pathlib import Path

    folder = Path(folder_path)
    txt_files = list(folder.glob('*.txt'))

    if not txt_files:
        log(f"No .txt files found in {folder_path}", Fore.YELLOW)
        return

    log(f"Found {len(txt_files)} files to process", Fore.CYAN)

    for file_path in txt_files:
        await process_file(str(file_path))

    log(f"\n{'='*60}", Fore.CYAN)
    log(f"COMPLETE!", Fore.CYAN)
    log(f"{'='*60}", Fore.CYAN)


if __name__ == '__main__':
    from src.config.settings import config
    if not config.LLM_API_KEY:
        log("ERROR: LLM_API_KEY not found in environment variables", Fore.RED)
        exit(1)

    log("Starting embedding pipeline...", Fore.CYAN)
    asyncio.run(process_all_files())
