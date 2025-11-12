#!/usr/bin/env python3
"""
Migration Script: Convert existing notes to new raw note structure

This script:
1. Finds all existing notes in topics/[topic]/YYYY-MM-DD.md format
2. Converts them to topics/[topic]/raw/YYYY-MM-DD_HH-MM-SS.md format
3. Creates corresponding metadata JSON files
4. Preserves all original content
5. Creates backups before migration

Usage:
    python scripts/migrate_to_raw_notes.py [--dry-run] [--backup]
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import sys

class NoteMigrator:
    def __init__(self, project_dir: Path, dry_run: bool = False, create_backup: bool = True):
        self.project_dir = project_dir
        self.topics_dir = project_dir / "topics"
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.migrated_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def run(self):
        """Execute the migration"""
        print("=" * 80)
        print("LEARNING MENTOR NOTE MIGRATION")
        print("Converting to raw note structure with metadata")
        print("=" * 80)
        print()
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print()
        
        # Create backup if requested
        if self.create_backup and not self.dry_run:
            self._create_backup()
        
        # Find all existing notes
        notes = self._find_existing_notes()
        
        if not notes:
            print("✓ No notes found to migrate")
            return
        
        print(f"Found {len(notes)} notes to migrate")
        print()
        
        # Migrate each note
        for note_path in notes:
            self._migrate_note(note_path)
        
        # Summary
        print()
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"✓ Migrated: {self.migrated_count}")
        print(f"⊘ Skipped:  {self.skipped_count}")
        print(f"✗ Errors:   {self.error_count}")
        
        if self.dry_run:
            print()
            print("This was a dry run. Run without --dry-run to perform migration.")
        elif self.migrated_count > 0:
            print()
            print("✓ Migration complete! Original notes backed up.")
            print(f"  Backup location: {self.project_dir / 'backups'}")
    
    def _create_backup(self):
        """Create backup of topics directory"""
        backup_dir = self.project_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"topics_backup_{timestamp}"
        
        print(f"📦 Creating backup: {backup_path}")
        try:
            shutil.copytree(self.topics_dir, backup_path)
            print(f"✓ Backup created successfully")
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            print("Aborting migration for safety.")
            sys.exit(1)
        print()
    
    def _find_existing_notes(self):
        """Find all existing notes in old format"""
        notes = []
        
        if not self.topics_dir.exists():
            return notes
        
        for topic_dir in self.topics_dir.iterdir():
            if not topic_dir.is_dir():
                continue
            
            # Skip if already has raw/ directory
            raw_dir = topic_dir / "raw"
            if raw_dir.exists():
                print(f"⊘ Skipping {topic_dir.name} - already migrated")
                continue
            
            # Find date-formatted markdown files
            for note_file in topic_dir.glob("*.md"):
                # Match YYYY-MM-DD.md pattern
                if len(note_file.stem) == 10 and note_file.stem.count('-') == 2:
                    try:
                        datetime.strptime(note_file.stem, "%Y-%m-%d")
                        notes.append(note_file)
                    except ValueError:
                        # Not a date format, skip
                        pass
        
        return sorted(notes)
    
    def _migrate_note(self, note_path: Path):
        """Migrate a single note to new structure"""
        topic = note_path.parent.name
        date_str = note_path.stem
        
        print(f"Migrating: {topic}/{date_str}.md", end="")
        
        try:
            # Read original content
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(" ... SKIPPED (empty)")
                self.skipped_count += 1
                return
            
            # Create raw directory
            raw_dir = note_path.parent / "raw"
            if not self.dry_run:
                raw_dir.mkdir(exist_ok=True)
            
            # Generate timestamp (use noon as default time since we don't know exact time)
            timestamp = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=12, minute=0, second=0)
            timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            
            # New paths
            new_note_path = raw_dir / f"{timestamp_str}.md"
            metadata_path = raw_dir / f"{timestamp_str}.json"
            
            # Create metadata
            metadata = {
                "original_filename": note_path.name,
                "migrated_at": datetime.now().isoformat(),
                "topic": topic,
                "capture_date": date_str,
                "capture_time": timestamp.isoformat(),
                "source": "migrated_from_old_format",
                "tags": [],
                "session_id": f"{topic}_{timestamp_str}"
            }
            
            if not self.dry_run:
                # Write new note
                with open(new_note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write metadata
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                # Remove old note (it's backed up)
                note_path.unlink()
            
            print(f" ... ✓ → raw/{timestamp_str}.md")
            self.migrated_count += 1
            
        except Exception as e:
            print(f" ... ✗ ERROR: {e}")
            self.error_count += 1
    

def main():
    parser = argparse.ArgumentParser(
        description="Migrate notes to new raw note structure with metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup (not recommended)'
    )
    
    parser.add_argument(
        '--project-dir',
        type=Path,
        default=Path.home() / "Projects" / "notes",
        help='Path to notes project directory'
    )
    
    args = parser.parse_args()
    
    # Validate project directory
    if not args.project_dir.exists():
        print(f"Error: Project directory not found: {args.project_dir}")
        sys.exit(1)
    
    # Run migration
    migrator = NoteMigrator(
        project_dir=args.project_dir,
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    migrator.run()


if __name__ == "__main__":
    main()
