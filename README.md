# AI-Powered Child Development Milestone Tracker

An AI-based child development monitoring system specifically designed to track developmental milestones for children with special conditions.

## Features

1. **Child Profile Management** - Create and manage child profiles with special condition information
2. **Development Record Tracking** - Record height, weight, head circumference, gross motor skills, language, fine motor skills, sleep, diet, and more
3. **AI-Powered Assessment** - Automatically assess child's development status (Normal Development / Benign Development / Regression) using OpenAI GPT-4
4. **Milestone Prediction** - Predict next developmental milestones and their expected timelines (up to 3 years of age)
5. **Normal Development Comparison** - Compare child's development with typical milestones for their age group
6. **Multimedia Support** - Support for images, videos, and text input formats
7. **Bilingual Support** - Full support for both English and Chinese interfaces
8. **Data Privacy** - Optional data anonymization before sending to AI services

## Technology Stack

```
React Frontend
    |
    v
FastAPI Backend
    |
    v
SQLite Database (Structured Data)
ChromaDB (Vector Database - for future expansion)
    |
    v
OpenAI GPT-4 (LLM)
```

## Project Structure

```
.
├── backend/          # FastAPI Backend
│   ├── main.py      # API main file
│   ├── models.py    # Database models
│   ├── database.py  # Database configuration
│   ├── llm_service_secure.py  # Secure LLM service with anonymization
│   ├── services.py  # Business logic services
│   ├── migrate_add_english_fields.py  # Database migration scripts
│   ├── migrate_add_child_english_field.py
│   └── requirements.txt
├── frontend/        # React Frontend
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── locales.js  # Internationalization
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Create a `.env` file in the `backend/` directory
   - Add your OpenAI API Key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=8000
   DATABASE_URL=sqlite:///./child_development.db
   ```
   - You can use the helper script: `python create_env.py`

5. Run database migrations (if needed):
```bash
python migrate_add_english_fields.py
python migrate_add_child_english_field.py
```

6. Start the backend server:
```bash
python main.py
# Or using uvicorn directly:
uvicorn main:app --reload --port 8000
```

The backend will run at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the frontend development server:
```bash
npm start
```

The frontend will run at `http://localhost:3000`

## API Endpoints

### Child Management
- `POST /api/children` - Create a child profile
- `GET /api/children` - Get all children
- `GET /api/children/{child_id}` - Get a specific child's information
- `PUT /api/children/{child_id}` - Update child profile

### Development Records
- `POST /api/records` - Create a development record (supports file uploads)
- `GET /api/children/{child_id}/records` - Get all records for a child
- `PUT /api/records/{record_id}` - Update a development record
- `DELETE /api/records/{record_id}` - Delete a development record

### Milestone Prediction
- `GET /api/children/{child_id}/milestones` - Predict next developmental milestones (up to 3 years)

### Development Comparison
- `GET /api/children/{child_id}/comparison` - Compare with normal development standards

## Usage Guide

1. **Create Child Profile**
   - Click the "New Profile" button
   - Fill in the child's basic information and special conditions
   - Submit to create

2. **Add Development Records**
   - Select the child to record
   - Click "New Record"
   - Fill in development indicators (height, weight, gross motor, language, etc.)
   - Optionally upload images or videos
   - After submission, the system will automatically assess development status using AI

3. **View Assessment Results**
   - After record submission, the system automatically displays AI assessment results
   - Assessment status: Normal Development / Benign Development / Regression
   - Detailed evidence and recommendations are provided

4. **View Milestone Predictions**
   - After selecting a child, the system automatically displays predicted developmental milestones
   - Milestones include expected time, normal age range, description, prediction basis, and achievement suggestions
   - Only milestones up to 3 years of age (36 months) are shown

5. **Compare with Normal Development**
   - View normal developmental standards for the child's age
   - See detailed comparison analysis and gap identification
   - Get targeted suggestions for improvement

6. **Language Switching**
   - Use the language toggle button in the header to switch between English and Chinese
   - All UI text and AI-generated content will switch accordingly

## Environment Variables

Configure in `backend/.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
DATABASE_URL=sqlite:///./child_development.db
```

## Data Privacy and Security

- **Data Anonymization**: The system can anonymize sensitive data (names, birth dates) before sending to OpenAI
- **Local Storage**: All data is stored locally in SQLite database
- **No Data Training**: Configure OpenAI to not use your data for training (see `PREVENT_TRAINING.md`)
- **Secure LLM Service**: Use `llm_service_secure.py` which implements data anonymization

For more information, see:
- `backend/PRIVACY_SECURITY.md` - Privacy and security considerations
- `backend/ENABLE_SECURITY.md` - How to enable data anonymization
- `backend/PREVENT_TRAINING.md` - How to prevent OpenAI from using data for training

## Important Notes

1. A valid OpenAI API Key is required to use AI assessment features
2. Uploaded images and videos are saved in the `backend/uploads/` directory
3. Database files are automatically created in the project root directory
4. Database table structure is automatically initialized on first run
5. The system supports automatic translation between English and Chinese
6. Milestone predictions are limited to 3 years of age (36 months) and earlier

## Troubleshooting

### Backend won't start
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify the OpenAI API Key in `.env` file is correct
- Ensure port 8000 is not in use (the system will try alternative ports automatically)
- Use `python kill_port.py` to free port 8000 if needed

### Frontend can't connect to backend
- Ensure the backend is running
- Check `src/App.js` for correct `API_BASE_URL`
- Check browser console for CORS errors

### AI assessment fails
- Verify OpenAI API Key is valid
- Check network connection
- View backend logs for detailed error messages

## Development Roadmap

- [x] Basic child profile management
- [x] Development record tracking
- [x] AI-powered assessment
- [x] Milestone prediction
- [x] Normal development comparison
- [x] Bilingual support (English/Chinese)
- [x] Data anonymization
- [ ] User authentication system
- [ ] Support for more file formats
- [ ] Data visualization charts
- [ ] Export report functionality
- [ ] Mobile app adaptation
- [ ] Multi-user support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Built with React and FastAPI
- Powered by OpenAI GPT-4
- Uses SQLite for data storage
