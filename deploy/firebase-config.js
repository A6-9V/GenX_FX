// Firebase Configuration for GenX FX Frontend
// Auto-generated configuration

const firebaseConfig = {
  // Firebase project configuration
  apiKey: "your-api-key-here", // Replace with your Firebase API key
  authDomain: "your-project.firebaseapp.com", // Replace with your domain
  projectId: "your-project-id", // Replace with your project ID
  storageBucket: "your-project.appspot.com", // Replace with your storage bucket
  messagingSenderId: "123456789", // Replace with your sender ID
  appId: "your-app-id", // Replace with your app ID
  measurementId: "G-XXXXXXXXXX" // Replace with your measurement ID
};

// Authentication configuration with provided hash parameters
const authConfig = {
  hashConfig: {
    algorithm: "SCRYPT",
    base64SignerKey: "process.env.BASE64_SIGNER_KEY", // Replace with your key
    base64SaltSeparator: "process.env.BASE64_SALT_SEPARATOR", // Replace with your salt
    rounds: 8,
    memCost: 14
  },
  // Test user configuration
  testUser: {
    email: "user@example.com",
    token: "process.env.TEST_USER_TOKEN" // Replace with your test user token
  }
};

export { firebaseConfig, authConfig };