"""
VEXA — Versatile Expert Conversational Assistant
Flask Backend  |  CSE Built-in Knowledge Base  |  pyttsx3 TTS  |  SpeechRecognition STT

Setup:
    pip install flask flask-cors requests pyttsx3 SpeechRecognition

Folder structure:
    voice_assistant/
        app.py
        templates/
            index.html     <-- Flask requires this exact location

Run:
    python app.py
Then open:  http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading
import os
import base64
import time
import tempfile
import datetime
import speech_recognition as sr

# ─────────────────────────────────────────────────────────────────────────────
# Resolve the templates folder relative to THIS file's location.
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app)

# ── Optional pyttsx3 ─────────────────────────────────────────────────────────
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[VEXA] pyttsx3 not found — TTS disabled. Run: pip install pyttsx3")




# ── CSE Built-in Knowledge Base ──────────────────────────────────────────────
import re as _re

CSE_KB = [
    {
        "keywords": ["operating system", "os", "what is os"],
        "question": "What is an Operating System?",
        "answer": (
            "An Operating System (OS) is system software that manages computer hardware, "
            "software resources, and provides common services for computer programs. "
            "It acts as an intermediary between users and the computer hardware. "
            "Examples include Windows, Linux, macOS, and Android. "
            "Core functions include process management, memory management, file system handling, "
            "and device I/O management."
        ),
    },
    {
        "keywords": ["data structure", "data structures", "what is data structure"],
        "question": "What are Data Structures?",
        "answer": (
            "A data structure is a way of organising and storing data in a computer so it can be "
            "accessed and modified efficiently. Common data structures include arrays, linked lists, "
            "stacks, queues, trees, graphs, and hash tables. "
            "Choosing the right data structure is crucial for writing efficient algorithms and "
            "directly impacts the time and space complexity of a program."
        ),
    },
    {
        "keywords": ["algorithm", "what is algorithm", "algorithms"],
        "question": "What is an Algorithm?",
        "answer": (
            "An algorithm is a finite, step-by-step set of instructions designed to solve a specific "
            "problem or perform a computation. Good algorithms are correct, efficient, and unambiguous. "
            "Key properties include input, output, definiteness, finiteness, and effectiveness. "
            "Algorithm efficiency is measured using Big-O notation, which describes time and space "
            "complexity in the worst case."
        ),
    },
    {
        "keywords": ["oop", "object oriented", "object-oriented programming"],
        "question": "What is Object-Oriented Programming?",
        "answer": (
            "Object-Oriented Programming (OOP) is a programming paradigm based on the concept of "
            "objects, which bundle data (attributes) and behaviour (methods) together. "
            "The four core principles are Encapsulation, Inheritance, Polymorphism, and Abstraction. "
            "OOP makes code modular, reusable, and easier to maintain. "
            "Popular OOP languages include Java, Python, C++, and C#."
        ),
    },
    {
        "keywords": ["database", "dbms", "what is database"],
        "question": "What is a Database and DBMS?",
        "answer": (
            "A database is an organised collection of structured data stored electronically. "
            "A Database Management System (DBMS) is software that interacts with users, applications, "
            "and the database itself to capture and analyse data. "
            "Types include Relational (SQL), NoSQL, hierarchical, and network databases. "
            "Popular DBMS examples are MySQL, PostgreSQL, Oracle, MongoDB, and SQLite."
        ),
    },
    {
        "keywords": ["sql", "structured query language", "what is sql"],
        "question": "What is SQL?",
        "answer": (
            "SQL (Structured Query Language) is the standard language for managing and manipulating "
            "relational databases. It supports DDL (CREATE, ALTER, DROP), DML (SELECT, INSERT, UPDATE, DELETE), "
            "and DCL (GRANT, REVOKE) operations. "
            "Key concepts include tables, primary keys, foreign keys, joins, indexes, and transactions. "
            "ACID properties - Atomicity, Consistency, Isolation, Durability - ensure reliable transactions."
        ),
    },
    {
        "keywords": ["networking", "computer network", "what is network"],
        "question": "What is Computer Networking?",
        "answer": (
            "Computer networking is the practice of connecting computers and devices to share resources "
            "and communicate. Networks are classified as LAN, WAN, MAN, or PAN based on size. "
            "The OSI model defines 7 layers: Physical, Data Link, Network, Transport, Session, "
            "Presentation, and Application. The TCP/IP model is the practical internet standard. "
            "Key protocols include HTTP, FTP, SMTP, TCP, UDP, and IP."
        ),
    },
    {
        "keywords": ["tcp ip", "tcp", "ip protocol", "transmission control"],
        "question": "What is TCP/IP?",
        "answer": (
            "TCP/IP (Transmission Control Protocol / Internet Protocol) is the foundational suite of "
            "communication protocols used on the internet. IP handles addressing and routing of packets, "
            "while TCP ensures reliable, ordered, and error-checked delivery of data. "
            "UDP is an alternative transport protocol that is faster but does not guarantee delivery. "
            "The model has four layers: Network Access, Internet, Transport, and Application."
        ),
    },
    {
        "keywords": ["sorting", "sorting algorithm", "bubble sort", "quick sort", "merge sort"],
        "question": "What are Sorting Algorithms?",
        "answer": (
            "Sorting algorithms arrange elements in a specific order. "
            "Bubble Sort (O(n squared)) repeatedly swaps adjacent elements. "
            "Selection Sort finds the minimum and places it in order. "
            "Merge Sort (O(n log n)) divides and conquers. "
            "Quick Sort (O(n log n) average) uses a pivot for partitioning. "
            "Heap Sort uses a binary heap. Counting and Radix Sort are non-comparison linear sorts."
        ),
    },
    {
        "keywords": ["linked list", "singly linked", "doubly linked"],
        "question": "What is a Linked List?",
        "answer": (
            "A linked list is a linear data structure where elements (nodes) are connected using pointers. "
            "Each node contains data and a reference to the next node. "
            "A singly linked list has one pointer (next); a doubly linked list has two (next and prev). "
            "Insertion and deletion are O(1) at the head; search is O(n). "
            "Linked lists are the foundation of stacks, queues, and hash table chaining."
        ),
    },
    {
        "keywords": ["stack", "what is stack", "lifo"],
        "question": "What is a Stack?",
        "answer": (
            "A stack is a linear data structure that follows the Last In, First Out (LIFO) principle. "
            "The main operations are push (add to top), pop (remove from top), and peek (view top). "
            "All operations are O(1). Stacks are used in function call management, "
            "expression evaluation, backtracking algorithms, undo/redo operations, and DFS traversal. "
            "They can be implemented using arrays or linked lists."
        ),
    },
    {
        "keywords": ["queue", "what is queue", "fifo"],
        "question": "What is a Queue?",
        "answer": (
            "A queue is a linear data structure that follows the First In, First Out (FIFO) principle. "
            "Elements are added at the rear (enqueue) and removed from the front (dequeue). "
            "Variants include circular queue, deque (double-ended queue), and priority queue. "
            "Queues are used in CPU scheduling, BFS traversal, print spooling, "
            "and buffering in network routers. Enqueue and dequeue are O(1) operations."
        ),
    },
    {
        "keywords": ["tree", "binary tree", "bst", "binary search tree"],
        "question": "What is a Binary Tree and BST?",
        "answer": (
            "A binary tree is a hierarchical data structure where each node has at most two children. "
            "A Binary Search Tree (BST) maintains the property that left subtree values are less than "
            "the root, and right subtree values are greater. "
            "BST search, insertion, and deletion are O(log n) on average. "
            "Traversals include inorder (LNR), preorder (NLR), and postorder (LRN). "
            "Balanced BSTs like AVL and Red-Black trees guarantee O(log n) worst case."
        ),
    },
    {
        "keywords": ["graph", "what is graph", "graph theory"],
        "question": "What is a Graph in Computer Science?",
        "answer": (
            "A graph is a non-linear data structure consisting of vertices (nodes) and edges (connections). "
            "Graphs can be directed or undirected, weighted or unweighted. "
            "Representations include adjacency matrix and adjacency list. "
            "Key algorithms: BFS, DFS, Dijkstra shortest path, Bellman-Ford, Prim and Kruskal MST. "
            "Applications include social networks, routing, and dependency resolution."
        ),
    },
    {
        "keywords": ["recursion", "what is recursion", "recursive"],
        "question": "What is Recursion?",
        "answer": (
            "Recursion is a programming technique where a function calls itself to solve a smaller "
            "instance of the same problem. Every recursive function needs a base case (stopping condition) "
            "and a recursive case. "
            "Classic examples: factorial, Fibonacci, Tower of Hanoi, and tree traversal. "
            "Recursion uses the call stack, so deep recursion can cause a stack overflow. "
            "Dynamic programming often optimises recursive solutions using memoization."
        ),
    },
    {
        "keywords": ["big o", "time complexity", "space complexity", "complexity"],
        "question": "What is Big-O Notation?",
        "answer": (
            "Big-O notation describes the upper bound of an algorithm's time or space complexity "
            "as input size grows. Common complexities from fastest to slowest: "
            "O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, "
            "O(n squared) quadratic, and O(2^n) exponential. "
            "We analyse best, average, and worst cases. Big-Omega is the lower bound and Big-Theta is the tight bound."
        ),
    },
    {
        "keywords": ["process", "thread", "multithreading", "process vs thread"],
        "question": "What is the difference between Process and Thread?",
        "answer": (
            "A process is an independent program in execution with its own memory space. "
            "A thread is the smallest unit of execution within a process; threads share memory and resources. "
            "Context switching between threads is faster than between processes. "
            "Multithreading improves CPU utilisation and responsiveness. "
            "Synchronisation issues like race conditions and deadlocks are solved using mutexes and semaphores."
        ),
    },
    {
        "keywords": ["deadlock", "what is deadlock"],
        "question": "What is a Deadlock?",
        "answer": (
            "A deadlock is a situation where two or more processes are blocked forever, "
            "each waiting for a resource held by another. "
            "The four necessary Coffman conditions are: Mutual Exclusion, Hold and Wait, "
            "No Preemption, and Circular Wait. "
            "Prevention strategies include resource ordering and preemption. "
            "Banker's Algorithm is used for deadlock avoidance. "
            "Recovery involves process termination or resource rollback."
        ),
    },
    {
        "keywords": ["memory management", "paging", "segmentation", "virtual memory"],
        "question": "What is Memory Management in OS?",
        "answer": (
            "Memory management controls and coordinates computer memory allocation. "
            "Techniques include contiguous allocation, paging (fixed-size frames), and segmentation. "
            "Virtual memory allows processes to use more memory than physically available via a page file. "
            "Page replacement algorithms include FIFO, LRU (Least Recently Used), and Optimal. "
            "Thrashing occurs when excessive paging degrades performance. "
            "The MMU (Memory Management Unit) translates virtual to physical addresses."
        ),
    },
    {
        "keywords": ["compiler", "interpreter", "what is compiler"],
        "question": "What is a Compiler vs Interpreter?",
        "answer": (
            "A compiler translates the entire source code into machine code before execution, "
            "producing a standalone executable (e.g., GCC for C/C++). "
            "An interpreter translates and executes code line by line at runtime (e.g., Python). "
            "Compiled programs run faster; interpreted programs are more portable. "
            "JIT (Just-In-Time) compilation used by Java's JVM combines both benefits."
        ),
    },
    {
        "keywords": ["encryption", "cryptography", "what is encryption", "rsa", "aes"],
        "question": "What is Encryption and Cryptography?",
        "answer": (
            "Cryptography is the science of securing information using codes. "
            "Symmetric encryption uses the same key for encryption and decryption (e.g., AES, DES). "
            "Asymmetric encryption uses a public key to encrypt and a private key to decrypt (e.g., RSA). "
            "Hashing converts data to a fixed-size digest and is one-way (e.g., SHA-256, MD5). "
            "TLS/SSL protocols use asymmetric encryption for key exchange and symmetric for bulk data. "
            "Digital signatures ensure authenticity and non-repudiation."
        ),
    },
    {
        "keywords": ["machine learning", "ml", "what is machine learning"],
        "question": "What is Machine Learning?",
        "answer": (
            "Machine Learning (ML) is a subset of AI that enables systems to learn from data "
            "and improve without being explicitly programmed. "
            "Types: Supervised learning (labelled data), Unsupervised learning (unlabelled data, clustering), "
            "and Reinforcement learning (reward-based). "
            "Popular algorithms include Linear Regression, Decision Trees, SVM, K-Means, and Neural Networks. "
            "Key libraries: scikit-learn, TensorFlow, PyTorch, and Keras."
        ),
    },
    {
        "keywords": ["artificial intelligence", "ai", "what is ai"],
        "question": "What is Artificial Intelligence?",
        "answer": (
            "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines. "
            "It encompasses learning, reasoning, problem-solving, perception, and language understanding. "
            "Branches include Machine Learning, Deep Learning, NLP, Computer Vision, and Robotics. "
            "AI is applied in healthcare, autonomous vehicles, finance, and virtual assistants. "
            "Narrow AI performs specific tasks; General AI (AGI) would match full human ability."
        ),
    },
    {
        "keywords": ["cloud computing", "what is cloud", "cloud"],
        "question": "What is Cloud Computing?",
        "answer": (
            "Cloud computing delivers computing services over the internet on a pay-as-you-go basis. "
            "Service models: IaaS (Infrastructure as a Service, e.g., AWS EC2), "
            "PaaS (Platform as a Service, e.g., Google App Engine), "
            "and SaaS (Software as a Service, e.g., Gmail). "
            "Deployment types: Public, Private, Hybrid, and Multi-cloud. "
            "Major providers include AWS, Microsoft Azure, and Google Cloud Platform."
        ),
    },
    {
        "keywords": ["software engineering", "sdlc", "software development life cycle"],
        "question": "What is the Software Development Life Cycle?",
        "answer": (
            "The SDLC is a structured process for planning, creating, testing, and delivering software. "
            "Common phases: Requirements, System Design, Implementation, Testing, Deployment, Maintenance. "
            "Popular models include Waterfall (sequential), Agile (iterative sprints), Scrum, Kanban, "
            "Spiral (risk-driven), and DevOps (continuous integration and delivery). "
            "Agile promotes collaboration, flexibility, and rapid delivery of working software."
        ),
    },
]


def _normalise(text: str) -> str:
    return _re.sub(r"[^a-z0-9 ]", " ", text.lower())


def lookup_cse(query: str):
    q = _normalise(query)
    best_entry, best_score = None, 0
    for entry in CSE_KB:
        score = sum(1 for kw in entry["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best_entry = entry
    if best_entry and best_score >= 1:
        return {"source": "cse_kb", "title": best_entry["question"],
                "answer": best_entry["answer"], "error": None}
    return None

# ── TTS singleton ─────────────────────────────────────────────────────────────
_tts_lock = threading.Lock()


def text_to_speech_b64(text: str) -> str | None:
    """Convert text → pyttsx3 WAV → base64 string, or None if TTS unavailable."""
    if not TTS_AVAILABLE:
        return None
    try:
        with _tts_lock:
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            engine.setProperty("volume", 0.95)

            voices  = engine.getProperty("voices")
            PREFER  = ("david", "mark", "james", "daniel", "george", "richard", "male")
            EXCLUDE = ("zira", "hazel", "susan", "helen", "linda", "female")

            chosen = None
            for v in voices:
                if any(k in v.name.lower() for k in PREFER):
                    chosen = v
                    break
            if not chosen:
                for v in voices:
                    if not any(k in v.name.lower() for k in EXCLUDE):
                        chosen = v
                        break
            if chosen:
                engine.setProperty("voice", chosen.id)

            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            engine.save_to_file(text, tmp.name)
            engine.runAndWait()

            with open(tmp.name, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            os.unlink(tmp.name)
            return data
    except Exception as e:
        print(f"[VEXA] TTS error: {e}")
        return None


# ── Greeting text ─────────────────────────────────────────────────────────────
def get_greeting_text() -> str:
    h = datetime.datetime.now().hour
    if 5 <= h < 12:
        return ("Good morning! I'm Vexa, your versatile expert conversational assistant. "
                "How can I help you today?")
    elif 12 <= h < 17:
        return ("Good afternoon! I'm Vexa, your versatile expert conversational assistant. "
                "What would you like to know?")
    elif 17 <= h < 21:
        return ("Good evening! I'm Vexa, your versatile expert conversational assistant. "
                "How can I assist you?")
    else:
        return ("Good night! I'm Vexa, your versatile expert conversational assistant. "
                "I'm ready for your queries.")








# ── Answer router — CSE Knowledge Base only ──────────────────────────────────
def get_best_answer(query: str) -> dict:
    # Check built-in CSE knowledge base
    cse = lookup_cse(query)
    if cse:
        print(f"[VEXA] CSE KB hit: {cse['title']}")
        return cse

    # No match found
    return {
        "source": "cse_kb",
        "title":  query,
        "answer": (
            f"I don't have a specific answer for '{query}' in my knowledge base. "
            "Try asking about topics like Operating Systems, Data Structures, Algorithms, "
            "OOP, Networking, Databases, Sorting, Trees, Graphs, Recursion, "
            "Deadlocks, Memory Management, Machine Learning, or Cloud Computing."
        ),
        "error": None,
    }


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    html_path = os.path.join(TEMPLATE_DIR, "index.html")
    if not os.path.exists(html_path):
        return (
            "<h2 style='font-family:sans-serif;color:#c00'>Setup error</h2>"
            "<p style='font-family:sans-serif'>Flask cannot find <b>index.html</b>.</p>"
            "<p style='font-family:sans-serif'>Make sure your folder looks like this:</p>"
            "<pre style='background:#f4f4f4;padding:12px;border-radius:6px'>"
            "voice_assistant/\n"
            "    app.py\n"
            "    templates/\n"
            "        index.html   &lt;-- move it here\n"
            "</pre>",
            500,
        )
    return render_template("index.html")


@app.route("/api/greeting", methods=["GET"])
def api_greeting():
    greeting  = get_greeting_text()
    audio_b64 = text_to_speech_b64(greeting)
    return jsonify({"greeting": greeting, "audio_b64": audio_b64})


@app.route("/api/query", methods=["POST"])
def api_query():
    body  = request.get_json(force=True)
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    start   = time.time()
    result  = get_best_answer(query)
    elapsed = round(time.time() - start, 2)

    answer_text = result.get("answer") or "I'm sorry, I couldn't find an answer."
    audio_b64   = text_to_speech_b64(answer_text)

    return jsonify({
        "query":     query,
        "answer":    answer_text,
        "source":    result.get("source", "unknown"),
        "title":     result.get("title", query),
        "elapsed":   elapsed,
        "audio_b64": audio_b64,
    })


@app.route("/api/stt", methods=["POST"])
def api_stt():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_file.save(tmp.name)
    tmp.close()

    recognizer = sr.Recognizer()
    text = ""
    error = None
    try:
        with sr.AudioFile(tmp.name) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        error = "Could not understand audio. Please speak more clearly."
    except sr.RequestError as e:
        error = f"Speech recognition service unavailable: {e}"
    except Exception as e:
        error = str(e)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

    if error:
        return jsonify({"error": error}), 422
    return jsonify({"text": text})


@app.route("/api/status", methods=["GET"])
def api_status():
    """Status endpoint expected by the frontend (was /api/health before — fixed)."""
    return jsonify({
        "status":          "ok",
        "tts":             TTS_AVAILABLE,
        "tts_available":   TTS_AVAILABLE,
        "template_dir":    TEMPLATE_DIR,
        "template_exists": os.path.exists(os.path.join(TEMPLATE_DIR, "index.html")),
        "timestamp":       datetime.datetime.now().isoformat(),
    })


# Keep /api/health for backwards compat
@app.route("/api/health", methods=["GET"])
def api_health():
    return api_status()


# ── Startup ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    html_path = os.path.join(TEMPLATE_DIR, "index.html")
    print("=" * 62)
    print("  VEXA — Versatile Expert Conversational Assistant  v5.0")
    print(f"  Template dir : {TEMPLATE_DIR}")
    print(f"  index.html   : {'FOUND ✓' if os.path.exists(html_path) else 'MISSING ✗  — copy index.html into templates/'}")
    print(f"  TTS          : {'pyttsx3 ready ✓' if TTS_AVAILABLE else 'disabled (pip install pyttsx3)'}")
    print("  AI Engine    : CSE Knowledge Base (built-in, no API needed)")
    print("  Running at   : http://127.0.0.1:5000")
    print("=" * 62)
    app.run(debug=True, port=5000, threaded=True)