import os
import PyPDF2
import threading
import pyttsx3
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style
from gtts import gTTS
import tempfile
import webbrowser

# Dark Mode Toggle
is_dark_mode = False

def toggle_theme():
    """Toggles between Dark and Light Mode"""
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    bg_color = "#333333" if is_dark_mode else "#f0f0f0"
    fg_color = "white" if is_dark_mode else "black"
    
    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        widget.configure(bg=bg_color, fg=fg_color)

    style.configure("TProgressbar", background="white" if is_dark_mode else "blue")

def extract_text_from_pdf(pdf_path, progress_bar):
    """Extracts text from a PDF file with progress tracking."""
    text = []
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            for i, page in enumerate(reader.pages):
                extracted_text = page.extract_text()
                if extracted_text:
                    text.append(extracted_text.strip())

                # Update Progress Bar
                progress_bar["value"] = ((i + 1) / total_pages) * 50  # 50% for extraction
                root.update_idletasks()

        return " ".join(text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read PDF:\n{e}")
        return ""

def split_text(text, max_chars=5000):
    """Splits text into chunks for processing."""
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def text_to_speech():
    """Runs the speech conversion process in a background thread."""
    threading.Thread(target=process_text_to_speech).start()

def process_text_to_speech():
    """Extracts text and converts it to speech with progress tracking."""
    pdf_path = file_path.get()
    selected_lang = lang_var.get()
    output_folder = os.path.dirname(pdf_path) + "/audio_output"
    
    if not pdf_path:
        messagebox.showwarning("Warning", "Please select a PDF file!")
        return

    os.makedirs(output_folder, exist_ok=True)
    status_label.config(text="Extracting text... ⏳")
    progress_bar["value"] = 0
    root.update_idletasks()

    text = extract_text_from_pdf(pdf_path, progress_bar)

    if not text:
        status_label.config(text="No text found in PDF! ❌")
        return

    chunks = split_text(text)
    total_chunks = len(chunks)

    status_label.config(text="Converting to speech... 🎙")

    # Use gTTS for Hinglish, pyttsx3 for others
    if selected_lang == "Hinglish":
        for idx, chunk in enumerate(chunks):
            try:
                tts = gTTS(text=chunk, lang="hi")
                output_file = os.path.join(output_folder, f"output_{idx+1}.mp3")
                tts.save(output_file)

                # Update Progress Bar
                progress_bar["value"] = 50 + ((idx + 1) / total_chunks) * 50
                root.update_idletasks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert text to speech:\n{e}")
                return
    else:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        # Set voice based on language
        if selected_lang == "English":
            engine.setProperty("voice", voices[0].id)
        elif selected_lang == "Hindi":
            engine.setProperty("voice", voices[1].id)

        for idx, chunk in enumerate(chunks):
            try:
                output_file = os.path.join(output_folder, f"output_{idx+1}.mp3")
                engine.save_to_file(chunk, output_file)
                engine.runAndWait()

                # Update Progress Bar
                progress_bar["value"] = 50 + ((idx + 1) / total_chunks) * 50
                root.update_idletasks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert text to speech:\n{e}")
                return

    status_label.config(text=f"✅ Audio saved in: {output_folder}")
    messagebox.showinfo("Success", f"Audio saved in:\n{output_folder}")
    progress_bar["value"] = 100  # Set progress to 100% after completion

def browse_file():
    """Opens file dialog to select a PDF file."""
    filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    file_path.set(filename)

# GUI Setup
root = tk.Tk()
root.title("PDF to Speech")
root.geometry("400x380")
root.resizable(False, False)

style = Style()
style.configure("TProgressbar", thickness=20)

file_path = tk.StringVar()
lang_var = tk.StringVar(value="English")

# File Selection
tk.Label(root, text="Select PDF:").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=40, state="readonly").pack(pady=2)
tk.Button(root, text="Browse", command=browse_file).pack(pady=2)

# Language Selection
tk.Label(root, text="Select Language:").pack(pady=5)
tk.OptionMenu(root, lang_var, "English", "Hindi", "Hinglish").pack(pady=2)

# Convert Button
tk.Button(root, text="Convert to Speech", command=text_to_speech).pack(pady=10)

# Progress Bar
progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=5)

# Status Label
status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=5)

# Dark Mode Button
tk.Button(root, text="Toggle Dark Mode", command=toggle_theme).pack(pady=10)

root.mainloop()
