#  Cue: The Conversational Video Editor

<p align="center">
  <img src="https://user-images.githubusercontent.com/12345/placeholder-logo.png" alt="Cue Logo" width="200"/>
</p>

<p align="center">
  <strong>Edit videos with the power of natural language.</strong>
  <br />
  <a href="#getting-started">Getting Started</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#tech-stack">Tech Stack</a>
</p>

---

Cue is an innovative, AI-powered video editing application that transforms the way you interact with your media. Instead of complex timelines and confusing menus, Cue allows you to edit your videos by simply talking to it. From simple trims to complex, multi-file operations, Cue understands your intent and brings your vision to life.

## Features

-   **Conversational Editing**: Describe your edits in plain English. "Trim the first 5 seconds," "Make the video black and white," or "Combine video A and video B."
-   **Multi-File Workflow**: Effortlessly manage and edit multiple video and audio files in a single project.
-   **Batch Operations**: Apply edits to all videos in your media bin at once. "Apply a fade-in to every video."
-   **Sequential Editing**: Chain commands together to create complex edits. "Trim the video from 10 to 20 seconds, then speed it up by 2x."
-   **Audio Manipulation**: Extract audio from a video, add a new audio track, or swap audio between clips.
-   **Visual Effects**: Add text overlays, apply visual filters (e.g., grayscale, sepia), and add transitions like fade-in/fade-out.
-   **Smart Media Management**: All your uploaded and edited files are neatly organized in your project's media bin.
-   **Project-Based Workflow**: Organize your work into distinct projects, each with its own media bin and chat history.

## Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

-   Node.js and npm (for the frontend)
-   Python 3.10+ and pip (for the backend)
-   FFmpeg (must be installed and available in your system's PATH)
-   ImageMagick (for the `add_text_to_video` feature)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/cue.git
    cd cue
    ```

2.  **Backend Setup:**
    ```sh
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    Create a `.env` file in the `backend` directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY='your_api_key_here'
    ```

3.  **Frontend Setup:**
    ```sh
    cd frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend Server:**
    Open a terminal, navigate to the `backend` directory, and run:
    ```sh
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

2.  **Start the Frontend Development Server:**
    Open a second terminal, navigate to the `frontend` directory, and run:
    ```sh
    npm run dev
    ```

3.  Open your browser and navigate to `http://localhost:3000` to start using the application.

## Usage

1.  **Create a Project**: Start by creating a new project to house your media.
2.  **Upload Media**: Drag and drop video or audio files into the "My Media" panel.
3.  **Start Editing**: Select a video to make it active, then type a command into the chat input at the bottom. The "Prompt Guide" provides a handy list of available commands.
4.  **Add to Media**: When the AI generates a new video or audio file, click the "Add to Media" button to save it to your project for further edits.

## Tech Stack

-   **Frontend**:
    -   Next.js
    -   React
    -   Tailwind CSS
    -   Zustand (State Management)
-   **Backend**:
    -   FastAPI
    -   Python 3.11
-   **AI & Orchestration**:
    -   LangChain & LangGraph
    -   OpenAI GPT-4
-   **Video & Audio Processing**:
    -   MoviePy
    -   FFmpeg

## License

Distributed under the MIT License. See `LICENSE` for more information.
