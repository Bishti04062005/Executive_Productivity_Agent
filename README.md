# Executive Productivity Agent

An AI-powered productivity assistant that extracts commitments from business communications, identifies ownership, and tracks deadlines in a Streamlit dashboard.

## Features

- Extract actionable commitments from business communications
- Identify task ownership
- Separate My Actions from Waiting on Others
- Flag unclear ownership
- Track overdue, due-today, and upcoming deadlines
- Export action reports as JSON
- Use Offline Demo Mode when the AI API is unavailable

## Technology Stack

- Python
- Streamlit
- Pydantic
- Requests
- OpenRouter API
- python-dotenv
- Pytest

## Project Structure

```text
Executive_Productivity_Agent/
├── agent/
├── data/
│   ├── sample_inputs.json
│   └── offline_actions.json
├── tests/
├── app.py
├── extractor.py
├── models.py
├── processor.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Executive_Productivity_Agent.git
cd Executive_Productivity_Agent
```

### 2. Create and Activate a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_actual_api_key
OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free
```

**Important:** Never upload `.env` or expose your API key in a public repository.

## Run the Application

```powershell
streamlit run app.py
```

The application normally opens at:

```text
http://localhost:8501
```

## Offline Demo Mode

If the OpenRouter API is unavailable or rate-limited:

1. Open the Streamlit sidebar.
2. Select **Offline Demo Mode**.
3. Set the user name and as-of date.
4. Review the sample actions and deadline categories.

Offline Demo Mode does not require an API key.

## AI Extraction Mode

1. Add a valid OpenRouter API key to `.env`.
2. Confirm that the selected model is available.
3. Ensure that your account has API quota.
4. Select **AI Extraction Mode**.
5. Click **Run AI Extraction**.

## Testing

Run the tests with:

```powershell
python -m pytest -q
```

## Workflow

1. Load business communications from `data/sample_inputs.json`.
2. Send the communications to the extraction module.
3. Convert the AI response into structured action objects.
4. Classify actions by ownership and deadlines.
5. Display results in the Streamlit dashboard.
6. Export the results as a JSON report.

## Limitations

- AI output depends on the selected model.
- OpenRouter free models can have daily rate limits.
- Relative dates may require contextual interpretation.
- Offline Demo Mode uses predefined sample actions.
- Production use requires additional validation and security controls.

## Future Improvements

- PDF and DOCX upload support
- Calendar integration
- Reminder notifications
- Database storage
- Duplicate commitment detection
- Improved date resolution
- Authentication and multi-user support

## Purpose

This project was created for educational and demonstration purposes.