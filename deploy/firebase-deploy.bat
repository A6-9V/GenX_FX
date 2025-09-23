@echo off
echo 🔥 Firebase Frontend Deployment
echo ================================

cd /d "C:\Users\USER\GenX_FX"

:: Install Firebase CLI if not exists
echo Installing Firebase CLI...
npm install -g firebase-tools

:: Login to Firebase
echo 🔐 Logging into Firebase...
echo ⚠️  Please login to Firebase manually or set the FIREBASE_TOKEN environment variable.
firebase login --token %FIREBASE_TOKEN%

:: Initialize Firebase project
echo 🚀 Initializing Firebase project...
firebase init hosting

:: Build frontend
echo 🔨 Building frontend...
npm run build

:: Deploy to Firebase
echo 📤 Deploying to Firebase...
firebase deploy --only hosting

echo ✅ Firebase deployment completed!
pause