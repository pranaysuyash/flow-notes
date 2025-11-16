"""
Privacy-Preserving Analytics for FlowNotes
Tracks usage metrics locally without sending data to external servers
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class PrivacyAnalytics:
    """Local-only analytics system"""

    def __init__(self, storage_dir: Path):
        """
        Initialize analytics system

        Args:
            storage_dir: Directory to store analytics data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.analytics_file = self.storage_dir / ".analytics.json"
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load analytics data from disk"""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except:
                return self._default_data()
        return self._default_data()

    def _default_data(self) -> Dict:
        """Create default analytics structure"""
        return {
            "install_date": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_notes": 0,
            "total_words": 0,
            "ai_enhancements": defaultdict(int),
            "keyboard_shortcuts_used": defaultdict(int),
            "features_used": defaultdict(int),
            "daily_stats": {},  # date -> stats
            "streak_days": 0,
            "longest_streak": 0,
            "onboarding_completed": False,
            "version": "3.0"
        }

    def _save_data(self):
        """Save analytics data to disk"""
        # Convert defaultdicts to regular dicts for JSON serialization
        data_to_save = {
            k: dict(v) if isinstance(v, defaultdict) else v
            for k, v in self.data.items()
        }

        with open(self.analytics_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)

    def track_event(self, event_name: str, properties: Optional[Dict] = None):
        """
        Track an event (locally only)

        Args:
            event_name: Name of the event
            properties: Optional event properties
        """
        # Update last active
        self.data["last_active"] = datetime.now().isoformat()

        # Increment feature usage
        if "features_used" not in self.data:
            self.data["features_used"] = {}

        self.data["features_used"][event_name] = \
            self.data["features_used"].get(event_name, 0) + 1

        # Save
        self._save_data()

    def track_session_start(self):
        """Track app session start"""
        self.data["total_sessions"] += 1
        self.data["last_active"] = datetime.now().isoformat()

        # Update daily stats
        today = datetime.now().date().isoformat()
        if "daily_stats" not in self.data:
            self.data["daily_stats"] = {}

        if today not in self.data["daily_stats"]:
            self.data["daily_stats"][today] = {
                "sessions": 0,
                "notes_created": 0,
                "words_written": 0,
                "ai_uses": 0
            }

        self.data["daily_stats"][today]["sessions"] += 1

        # Update streak
        self._update_streak()

        self._save_data()

    def track_note_created(self, word_count: int = 0):
        """Track note creation"""
        self.data["total_notes"] += 1
        self.data["total_words"] += word_count

        today = datetime.now().date().isoformat()
        if today in self.data.get("daily_stats", {}):
            self.data["daily_stats"][today]["notes_created"] += 1
            self.data["daily_stats"][today]["words_written"] += word_count

        self._save_data()

    def track_ai_enhancement(self, enhancement_type: str):
        """Track AI enhancement usage"""
        if "ai_enhancements" not in self.data:
            self.data["ai_enhancements"] = {}

        self.data["ai_enhancements"][enhancement_type] = \
            self.data["ai_enhancements"].get(enhancement_type, 0) + 1

        today = datetime.now().date().isoformat()
        if today in self.data.get("daily_stats", {}):
            self.data["daily_stats"][today]["ai_uses"] += 1

        self._save_data()

    def track_shortcut_used(self, shortcut: str):
        """Track keyboard shortcut usage"""
        if "keyboard_shortcuts_used" not in self.data:
            self.data["keyboard_shortcuts_used"] = {}

        self.data["keyboard_shortcuts_used"][shortcut] = \
            self.data["keyboard_shortcuts_used"].get(shortcut, 0) + 1

        self._save_data()

    def mark_onboarding_complete(self):
        """Mark onboarding as completed"""
        self.data["onboarding_completed"] = True
        self._save_data()

    def _update_streak(self):
        """Update learning streak"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Check if yesterday has activity
        yesterday_str = yesterday.isoformat()
        today_str = today.isoformat()

        if yesterday_str in self.data.get("daily_stats", {}):
            # Continue streak
            self.data["streak_days"] += 1
        elif today_str not in self.data.get("daily_stats", {}):
            # First activity today, reset if more than 1 day gap
            self.data["streak_days"] = 1

        # Update longest streak
        if self.data["streak_days"] > self.data.get("longest_streak", 0):
            self.data["longest_streak"] = self.data["streak_days"]

    def get_stats(self) -> Dict:
        """Get analytics statistics"""
        # Calculate time using app
        install_date = datetime.fromisoformat(self.data["install_date"])
        days_since_install = (datetime.now() - install_date).days

        return {
            "days_since_install": days_since_install,
            "total_sessions": self.data.get("total_sessions", 0),
            "total_notes": self.data.get("total_notes", 0),
            "total_words": self.data.get("total_words", 0),
            "average_words_per_note": (
                self.data.get("total_words", 0) / self.data.get("total_notes", 1)
                if self.data.get("total_notes", 0) > 0 else 0
            ),
            "streak_days": self.data.get("streak_days", 0),
            "longest_streak": self.data.get("longest_streak", 0),
            "most_used_ai": self._get_top_items(self.data.get("ai_enhancements", {}), 3),
            "most_used_shortcuts": self._get_top_items(
                self.data.get("keyboard_shortcuts_used", {}), 5
            ),
            "onboarding_completed": self.data.get("onboarding_completed", False),
        }

    def get_weekly_stats(self) -> Dict:
        """Get this week's statistics"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        weekly_notes = 0
        weekly_words = 0
        weekly_ai_uses = 0

        for date_str, stats in self.data.get("daily_stats", {}).items():
            date = datetime.fromisoformat(date_str).date()
            if week_ago <= date <= today:
                weekly_notes += stats.get("notes_created", 0)
                weekly_words += stats.get("words_written", 0)
                weekly_ai_uses += stats.get("ai_uses", 0)

        return {
            "notes_this_week": weekly_notes,
            "words_this_week": weekly_words,
            "ai_uses_this_week": weekly_ai_uses,
            "daily_average_notes": weekly_notes / 7,
        }

    def get_learning_insights(self) -> List[str]:
        """Generate learning insights based on usage"""
        insights = []
        stats = self.get_stats()

        # Streak insights
        if stats["streak_days"] >= 7:
            insights.append(f"🔥 Amazing! You're on a {stats['streak_days']}-day streak!")
        elif stats["streak_days"] >= 3:
            insights.append(f"💪 Keep it up! {stats['streak_days']} days in a row!")
        else:
            insights.append("📅 Build a learning habit - try to use FlowNotes daily!")

        # Notes insights
        if stats["total_notes"] >= 100:
            insights.append(f"📚 Wow! You've created {stats['total_notes']} notes!")
        elif stats["total_notes"] >= 50:
            insights.append(f"📝 Great progress - {stats['total_notes']} notes and counting!")

        # AI usage insights
        total_ai_uses = sum(self.data.get("ai_enhancements", {}).values())
        if total_ai_uses >= 50:
            insights.append(f"✨ AI power user! {total_ai_uses} enhancements generated!")
        elif total_ai_uses < 5 and stats["total_notes"] > 10:
            insights.append("💡 Try the AI assistant - it can save you hours!")

        # Keyboard shortcuts
        total_shortcuts = sum(self.data.get("keyboard_shortcuts_used", {}).values())
        if total_shortcuts >= 50:
            insights.append(f"⌨️ Keyboard ninja! {total_shortcuts} shortcuts used!")
        elif total_shortcuts < 10 and stats["total_sessions"] > 5:
            insights.append("⌨️ Tip: Learn keyboard shortcuts to work faster (press ?)")

        # Words written
        if stats["total_words"] >= 10000:
            insights.append(f"✍️ You've written {stats['total_words']:,} words!")

        return insights[:4]  # Return top 4 insights

    def _get_top_items(self, items_dict: Dict, n: int = 3) -> List[tuple]:
        """Get top N items from a frequency dict"""
        sorted_items = sorted(
            items_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_items[:n]

    def export_data(self) -> Dict:
        """Export all analytics data (for user data export)"""
        return self.data.copy()

    def clear_data(self):
        """Clear all analytics data"""
        self.data = self._default_data()
        self._save_data()


# Usage tracking decorator
def track(event_name: str):
    """Decorator to track function calls"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'analytics'):
                self.analytics.track_event(event_name)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# Test
if __name__ == "__main__":
    import tempfile

    # Test analytics
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = PrivacyAnalytics(Path(tmpdir))

        # Simulate usage
        analytics.track_session_start()
        analytics.track_note_created(250)
        analytics.track_note_created(180)
        analytics.track_ai_enhancement("flashcards")
        analytics.track_ai_enhancement("summary")
        analytics.track_shortcut_used("Ctrl+S")
        analytics.mark_onboarding_complete()

        # Get stats
        print("Stats:", json.dumps(analytics.get_stats(), indent=2))
        print("\nWeekly:", json.dumps(analytics.get_weekly_stats(), indent=2))
        print("\nInsights:", analytics.get_learning_insights())
