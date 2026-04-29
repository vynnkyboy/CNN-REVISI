🗑️ Waste Detection System

AI-powered system untuk mendeteksi dan mengklasifikasikan sampah organik dan anorganik menggunakan Deep Learning (MobileNetV2).
📋 Prasyarat

    Python 3.9 - 3.11

    Node.js 16+

    npm atau yarn

🚀 Quick Start
1. Clone Repository
bash

git clone https://github.com/your-repo/waste-detector.git
cd waste-detector

2. Setup Backend
bash

cd backend
pip install -r requirements.txt
python app.py

Server berjalan di: http://localhost:8000
3. Setup Frontend
bash

cd frontend
npm install
npm run dev

Aplikasi berjalan di: http://localhost:5173
📁 Struktur Folder
text

waste-detector/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── model_handler.py    # Model loading & detection
│   ├── requirements.txt    # Python dependencies
│   └── models/             # Folder model .pth
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styling (Dark/Light mode)
│   │   └── main.jsx        # Entry point
│   └── package.json
└── training/
    ├── train.py            # Training script
    └── requirements.txt

🧠 Training Model (Opsional)
bash

cd training
pip install -r requirements.txt
python train.py

Model akan tersimpan di models/best_waste_classifier_mobilenet.pth
🔧 API Endpoints
Method	Endpoint	Deskripsi
POST	/detect	Upload gambar untuk deteksi
GET	/health	Cek status server
GET	/model-info	Info model yang digunakan
📱 Fitur

    ✅ Deteksi multi-object (3 teratas dengan confidence tertinggi)

    ✅ Klasifikasi Organik (🌿) & Anorganik (🗑️)

    ✅ Bounding box dengan label & confidence score

    ✅ Dark/Light mode toggle

    ✅ Responsive design (Mobile & Desktop)

🛠️ Teknologi
Backend	Frontend
FastAPI	React + Vite
PyTorch	Axios
MobileNetV2	CSS3 + Flexbox
📝 Catatan

    Pastikan model .pth sudah ada di folder backend/models/

    Default confidence threshold: 0.6

    Output hanya menampilkan 3 deteksi dengan confidence tertinggi

👨‍💻 Author

Waste Detector - Clean Environment, Better Future

Selamat mencoba! ♻️
