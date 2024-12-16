#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime

def find_todos(directory):
    todos = {}
    completed_todos = {}
    # Files/directories to ignore
    ignore_patterns = ['.git', '.github', 'node_modules', '__pycache__', '.obsidian', 'TODO.md']
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not any(pat in d for pat in ignore_patterns)]
        
        for file in files:
            if file == 'TODO.md':  # Skip TODO.md file
                continue
            if file.endswith(('.md', '.py', '.js', '.html', '.css', '.txt', '.tex')):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find active TODOs
                    matches = re.finditer(r'^.*(?:%+)?#TODO(?!-DONE).*$', content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        todo_line = match.group().strip()
                        if rel_path not in todos:
                            todos[rel_path] = []
                        todos[rel_path].append(todo_line)

                    # Find completed TODOs
                    completed_matches = re.finditer(r'^.*(?:%+)?#TODO-DONE.*$', content, re.MULTILINE | re.IGNORECASE)
                    for match in completed_matches:
                        todo_line = match.group().strip()
                        if rel_path not in completed_todos:
                            completed_todos[rel_path] = []
                        completed_todos[rel_path].append(todo_line)
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return todos, completed_todos

def generate_todo_md(todos, completed_todos):
    content = """# Project TODOs

This file collects all TODO items from across the repository.

"""
    
    # Process active TODOs
    dir_todos = {}
    for file_path, todo_list in todos.items():
        dir_name = os.path.dirname(file_path) or "Root"
        if dir_name not in dir_todos:
            dir_todos[dir_name] = []
        dir_todos[dir_name].extend((file_path, todo) for todo in todo_list)
    
    # Generate markdown content for active TODOs
    for dir_name, todo_items in sorted(dir_todos.items()):
        if dir_name != "Root":
            content += f"## {dir_name}\n"
        else:
            content += "## Miscellaneous\n"
            
        for file_path, todo in todo_items:
            # Clean the todo line by removing common markers
            clean_todo = re.sub(r'^[-*]\s*', '', todo)  # Remove list markers
            clean_todo = re.sub(r'#TODO\s*', '', clean_todo, flags=re.IGNORECASE)  # Remove #TODO
            clean_todo = re.sub(r'^%+', '', clean_todo)  # Remove LaTeX-style TODO prefix
            clean_todo = clean_todo.strip()
            
            content += f"- {clean_todo}\n"
            content += f"  - Location: `{file_path}`\n\n"
    
    content += """---
*Note: This TODO list is automatically generated from TODO comments in the codebase. 
Add `#TODO` to your comments to have them appear here.
When completing a TODO, change `#TODO` to `#TODO-DONE` to move it to the completed section.*

"""

    # Add completed TODOs section
    if completed_todos:
        content += "## Completed TODOs\n\n"
        for file_path, todo_list in completed_todos.items():
            for todo in todo_list:
                # Clean the completed todo line
                clean_todo = re.sub(r'^[-*]\s*', '', todo)  # Remove list markers
                clean_todo = re.sub(r'#TODO-DONE\s*', '', clean_todo, flags=re.IGNORECASE)  # Remove #TODO-DONE
                clean_todo = re.sub(r'^%+', '', clean_todo)  # Remove LaTeX-style TODO prefix
                clean_todo = clean_todo.strip()
                
                content += f"- ~~{clean_todo}~~ *(from `{file_path}`)*\n"
        content += "\n"

    content += f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return content

def main():
    # Get the root directory (where the script is run from)
    root_dir = os.getcwd()
    
    # Find all TODOs
    todos, completed_todos = find_todos(root_dir)
    
    # Generate markdown content
    content = generate_todo_md(todos, completed_todos)
    
    # Write to TODO.md
    with open('TODO.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
