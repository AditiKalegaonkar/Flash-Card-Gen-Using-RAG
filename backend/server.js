const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());

const FASTAPI_URL = 'http://localhost:8000/generate';

app.post('/api/upload', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        // Forward file to FastAPI
        const formData = new FormData();
        formData.append('file', fs.createReadStream(req.file.path), req.file.originalname);

        const response = await axios.post(FASTAPI_URL, formData, {
            headers: {
                ...formData.getHeaders()
            }
        });

        // Send Clean JSON back to Frontend
        res.json(response.data);

    } catch (error) {
        console.error("Error connecting to AI service:", error.message);
        res.status(500).json({ error: 'Failed to generate flashcards' });
    } finally {
        // Cleanup Node upload
        if (req.file) fs.unlinkSync(req.file.path);
    }
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Node Server running on port ${PORT}`);
});