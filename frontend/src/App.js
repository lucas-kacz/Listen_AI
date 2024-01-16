import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Optionally, you can display a message to the user
    // indicating that the file has been uploaded successfully

    console.log('File uploaded:', file.name);
  };

  const sendFileToBackend = async () => {
    try {
      // Use the selectedFile state variable to retrieve the file
      const file = selectedFile;
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/transcribe', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      // Handle the response from the server
      console.log(data);
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  return (
    <div className="App">
      <input type="file" onChange={handleFileUpload} />
      <button onClick={sendFileToBackend}>Send to Backend</button>
    </div>
  );
}

export default App;
