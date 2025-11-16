"""
Demo Mode for FlowNotes
Pre-loaded sample notes to help users explore features
"""

from pathlib import Path
from datetime import datetime, timedelta


SAMPLE_NOTES = {
    "machine-learning": [
        {
            "filename": "neural-networks-basics.md",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": """# Neural Networks Basics

## Introduction
Neural networks are computing systems inspired by the biological neural networks that constitute animal brains.

## Key Components

### Layers
- **Input Layer**: Receives the raw data
- **Hidden Layers**: Process and transform the data
- **Output Layer**: Produces the final prediction

### Neurons & Connections
Each neuron:
- Receives inputs from previous layer
- Applies weights to each input
- Sums weighted inputs + bias
- Passes through activation function
- Sends output to next layer

### Activation Functions
Common activation functions:
- **ReLU** (Rectified Linear Unit): `f(x) = max(0, x)`
- **Sigmoid**: `f(x) = 1 / (1 + e^-x)`
- **Tanh**: `f(x) = tanh(x)`

## Training Process

### Forward Propagation
1. Input flows through network
2. Each layer applies transformations
3. Final layer produces prediction

### Backpropagation
1. Calculate error (loss function)
2. Propagate error backward
3. Update weights using gradient descent
4. Repeat until convergence

## Applications
- Image recognition
- Natural language processing
- Speech recognition
- Autonomous vehicles
- Game AI (AlphaGo)

## Key Concepts to Remember
> The power of neural networks comes from combining simple operations (weighted sums + activation functions) in deep architectures.

---
*Notes from: Deep Learning Course - Week 1*
"""
        },
        {
            "filename": "gradient-descent.md",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": """# Gradient Descent Algorithm

## What is Gradient Descent?
Optimization algorithm used to minimize the cost function in machine learning models.

## Intuition
Imagine you're on a mountain in fog:
- You can only see your immediate surroundings
- You want to reach the valley (minimum)
- You take small steps in the steepest downhill direction
- Eventually, you reach a local minimum

## Mathematical Formulation

**Update Rule**:
```
θ = θ - α * ∇J(θ)
```

Where:
- θ = model parameters (weights)
- α = learning rate
- ∇J(θ) = gradient of cost function

## Variants

### Batch Gradient Descent
- Uses entire dataset for each update
- **Pros**: Stable convergence
- **Cons**: Slow for large datasets

### Stochastic Gradient Descent (SGD)
- Uses one sample for each update
- **Pros**: Fast, can escape local minima
- **Cons**: Noisy updates, unstable

### Mini-Batch Gradient Descent
- Uses small batch (e.g., 32 samples)
- **Pros**: Balance speed and stability
- **Cons**: Requires tuning batch size

## Hyperparameters

### Learning Rate (α)
- Too small → slow convergence
- Too large → overshooting, divergence
- Common values: 0.001, 0.01, 0.1

### Momentum
Helps accelerate SGD:
```
v = β * v + ∇J(θ)
θ = θ - α * v
```

## Advanced Optimizers
- **Adam** (Adaptive Moment Estimation)
- **RMSprop** (Root Mean Square Propagation)
- **AdaGrad** (Adaptive Gradient)

## Practical Tips
1. Start with learning rate = 0.01
2. Use learning rate scheduling
3. Monitor loss curve for convergence
4. Try different optimizers
5. Normalize input features

---
*Remember: Gradient descent is the workhorse of deep learning!*
"""
        }
    ],
    "python-programming": [
        {
            "filename": "decorators-explained.md",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "content": """# Python Decorators

## What are Decorators?
Functions that modify the behavior of other functions or classes.

## Basic Concept
A decorator is a function that:
1. Takes a function as input
2. Adds functionality
3. Returns a new function

## Simple Example

```python
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function call
# Hello!
# After function call
```

## Decorators with Arguments

```python
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Prints "Hello, Alice!" 3 times
```

## Common Use Cases

### 1. Logging
```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### 2. Timing
```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.2f}s")
        return result
    return wrapper
```

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 4. Authentication
```python
def require_auth(func):
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            raise PermissionError("Not authorized")
        return func(*args, **kwargs)
    return wrapper
```

## Built-in Decorators

### @property
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
```

### @staticmethod & @classmethod
```python
class MyClass:
    @staticmethod
    def static_method():
        print("This is a static method")

    @classmethod
    def class_method(cls):
        print(f"This is a class method of {cls}")
```

## Best Practices
1. Use `functools.wraps` to preserve function metadata
2. Keep decorators simple and focused
3. Document decorator behavior
4. Consider performance implications
5. Test decorated and undecorated functions

## Advanced: Decorator Classes
```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)
```

---
*Decorators are syntactic sugar that makes Python code elegant and powerful!*
"""
        }
    ],
    "productivity": [
        {
            "filename": "spaced-repetition-guide.md",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": """# Spaced Repetition: The Science of Remembering

## What is Spaced Repetition?
A learning technique that involves reviewing information at increasing intervals to maximize long-term retention.

## The Forgetting Curve
Discovered by Hermann Ebbinghaus (1885):
- We forget ~50% of new information within 1 hour
- We forget ~70% within 24 hours
- We forget ~90% within 1 week

**But**: Each review resets the curve at a higher level!

## How It Works

### Review Schedule Example
```
Day 1:   Learn new concept
Day 2:   First review (1 day later)
Day 4:   Second review (2 days later)
Day 8:   Third review (4 days later)
Day 16:  Fourth review (8 days later)
Day 32:  Fifth review (16 days later)
```

### Interval Calculation
Most systems use:
- Easy card → multiply interval by 2.5
- Good card → multiply interval by 2.0
- Hard card → multiply interval by 1.2
- Again → reset to 1 day

## Optimal Flashcard Creation

### Good Flashcards
✅ **Q**: What is the capital of France?
**A**: Paris

✅ **Q**: Name 3 advantages of spaced repetition
**A**: 1) Better long-term retention 2) Less study time 3) Prevents cramming

### Bad Flashcards
❌ **Q**: Tell me about France
**A**: France is a country in Europe... (too broad)

❌ **Q**: What is the formula for photosynthesis?
**A**: 6CO2 + 6H2O + light → C6H12O6 + 6O2 (too complex for one card)

## Best Practices

### 1. Make Cards Immediately
Don't wait - create cards right after learning.

### 2. Use Active Recall
Don't just recognize - actively retrieve from memory.

### 3. Keep It Simple
One concept = one card.

### 4. Use Both Directions
"Capital of France?" AND "Where is Paris?"

### 5. Add Context
Include examples, mnemonics, visual cues.

## Research-Backed Benefits
- **200% improvement** in long-term retention (Ebbinghaus)
- **50-70% less study time** for same results
- Reduces cognitive load during exams
- Builds confidence through mastery

## Popular Tools
1. **Anki** - Open-source, powerful, steep learning curve
2. **Quizlet** - User-friendly, limited spaced repetition
3. **RemNote** - Note-taking + spaced repetition
4. **FlowNotes** - Auto-generates cards from notes 😉

## Implementation Tips

### Daily Routine
1. Review all due cards (10-20 min)
2. Create new cards from today's learning (5-10 min)
3. Total time: 15-30 min/day

### What to Memorize
✅ Foreign language vocabulary
✅ Technical definitions
✅ Historical dates
✅ Code syntax
✅ Formulas and equations

❌ Complex conceptual understanding (need other methods)

## The Leitner System
Physical card system:
- Box 1: Review daily
- Box 2: Review every 3 days
- Box 3: Review weekly
- Box 4: Review monthly
- Box 5: Mastered

Got it right? → Move to next box
Got it wrong? → Move back to Box 1

## Conclusion
Spaced repetition is not magic - it's science. The key is consistency.

> "Repetition is the mother of learning, the father of action, which makes it the architect of accomplishment." - Zig Ziglar

---
*Start today: Create 5 flashcards from your recent notes!*
"""
        }
    ]
}


def create_demo_notes(notes_dir: Path):
    """
    Create demo notes in the topics directory

    Args:
        notes_dir: Base notes directory
    """
    topics_dir = notes_dir / "topics"

    for topic, notes_list in SAMPLE_NOTES.items():
        topic_dir = topics_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)

        for note_data in notes_list:
            note_path = topic_dir / note_data["filename"]
            note_path.write_text(note_data["content"], encoding='utf-8')

    print(f"✅ Created {sum(len(notes) for notes in SAMPLE_NOTES.values())} demo notes")


def get_demo_welcome_note() -> str:
    """Get welcome note for first-time users"""
    return """# Welcome to FlowNotes! 🎉

Welcome to your AI-powered learning companion. FlowNotes helps you transform raw notes into comprehensive learning materials.

## 🚀 Quick Start

### 1. Explore the Demo Notes
We've created sample notes in these topics:
- **Machine Learning** - Neural networks and gradient descent
- **Python Programming** - Decorators explained
- **Productivity** - Spaced repetition guide

Click on the topics in the sidebar to explore!

### 2. Try the AI Assistant
1. Open any note (or create your own)
2. Look at the **AI Assistant** panel on the right
3. Click any button to see AI magic:
   - 📋 Generate a summary
   - 🏷️ Extract key concepts
   - 📊 Create a visual diagram
   - ❓ Generate quiz questions
   - 🗂️ Make flashcards

### 3. Use Keyboard Shortcuts
Press `?` to see all shortcuts, or start with:
- `Ctrl+N` - New note
- `Ctrl+S` - Save
- `Ctrl+F` - Find
- `Ctrl+Shift+F` - Focus mode

## ✨ What Makes FlowNotes Special?

### Evidence-Based Learning
Every feature is backed by cognitive science:
- **Active Recall**: Quiz questions improve retention by 50%
- **Spaced Repetition**: Flashcards boost memory by 200%
- **Dual Coding**: Diagrams increase understanding by 65%

### Local-First & Private
- All data stored on your computer
- Works completely offline
- Optional cloud sync (E2E encrypted)

### Beautiful & Fast
- Clean, distraction-free interface
- Keyboard-first workflow
- Live preview as you type

## 📚 Learning Resources

### In the App
- Press `F1` for help
- Press `?` for keyboard shortcuts
- Check the Help menu for tutorials

### Online
- Documentation: docs.flownotes.app
- Community: Discord server
- Video tutorials: YouTube

## 🎯 Your First Task

**Create your first note:**
1. Press `Ctrl+N` (or click "New Note")
2. Choose a topic (or create a new one)
3. Start typing - use Markdown for formatting
4. Try the AI assistant on your content
5. See the magic happen! ✨

## 💡 Pro Tips

### Markdown Basics
```markdown
# Heading 1
## Heading 2
**bold** *italic*
- List item
[link](url)
```

### Maximize Learning
1. Take notes during lectures/reading
2. Generate flashcards immediately
3. Review cards daily (takes 10-15 min)
4. Use diagrams for complex topics
5. Test yourself with quiz questions

### Power User Features
- **Focus Mode**: `Ctrl+Shift+F` for distraction-free writing
- **Search**: `Ctrl+F` to find anything across all notes
- **Export**: Share notes as PDF or HTML
- **Anki Integration**: Export flashcards to Anki

## 🤝 Need Help?

Having issues or questions?
- Check the Help menu (F1)
- Join our Discord community
- Email support@flownotes.app

## 🌟 What's Next?

After exploring the demo:
1. Delete demo notes (or keep them as reference)
2. Start taking your own notes
3. Build a daily learning habit
4. Watch your knowledge grow!

---

**Ready to transform your learning?**

Delete this welcome note and create your first real note with `Ctrl+N`

Happy learning! 🚀

---
*Made with ❤️ for learners, by learners*
"""


# Test
if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        notes_dir = Path(tmpdir) / "notes"
        create_demo_notes(notes_dir)

        # List created files
        for topic_dir in (notes_dir / "topics").iterdir():
            print(f"\nTopic: {topic_dir.name}")
            for note_file in topic_dir.glob("*.md"):
                print(f"  - {note_file.name}")
