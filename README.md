# GUI Automation Tool

A simple, web-based GUI automation tool built with NiceGUI and PyAutoGUI. This tool allows you to create and run sequences of mouse and keyboard actions through an easy-to-use web interface.

## Features

- Create automation sequences with different types of actions:
  - Move mouse to specific coordinates
  - Click at specific coordinates
  - Type text
  - Add delays
  - Take screenshots
- Real-time execution logging
- Simple and intuitive web interface
- Cross-platform support (Windows, Linux, macOS)

## Requirements

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd gui-automation-tool
   ```
3. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```
2. Open your web browser and navigate to `http://localhost:8080`
3. Use the interface to create and run your automation sequences

## How It Works

1. **Add Steps**: Use the "Add Step" section to create automation steps
2. **Configure Parameters**: Each step type has its own parameters (coordinates, text, delay time, etc.)
3. **Run Automation**: Click "Run All Steps" to execute the sequence
4. **Monitor Progress**: Watch the execution logs in real-time

## Notes

- The automation runs directly on your machine
- Use the "Clear All Steps" button to start a new automation sequence
- The application is designed for prototyping and testing purposes

## License

This project is open source and available under the [MIT License](LICENSE).
