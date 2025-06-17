# CodeSage - AI-Powered Code Review Assistant

CodeSage is an intelligent code review assistant that leverages AI to analyze code, suggest improvements, and explain complex code snippets in real-time. Built with modern technologies and best practices, it demonstrates advanced full-stack development capabilities.

## Features

- 🔍 Real-time code analysis
- 🤖 AI-powered code suggestions
- 📝 Code explanation generation
- 🎯 Best practices recommendations
- 🔄 Real-time collaboration
- 📊 Code quality metrics
- 🎨 Modern, responsive UI

## Tech Stack

### Backend
- FastAPI (Python)
- OpenAI API for code analysis
- PostgreSQL for data persistence
- Redis for caching
- Docker for containerization

### Frontend
- React with TypeScript
- TailwindCSS for styling
- Monaco Editor for code editing
- Socket.IO for real-time updates

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your OpenAI API key and other configurations
   ```

4. Run the development servers:
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## Architecture

The project follows a clean architecture pattern with:
- Separation of concerns
- Dependency injection
- Repository pattern
- Service layer abstraction
- Event-driven architecture

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your portfolio! 